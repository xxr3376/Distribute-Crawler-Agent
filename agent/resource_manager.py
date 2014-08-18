import requests
__resource__ = {}
__pool = None
logger = None
from collections import deque
from util import retry
import threading

"""
Resource Item
name:
error:
pool: [
    {
        id:
        expire:
        quota:
        cookies: {}
    }
    ...

]
"""

def init(pool, _logger):
    global __pool, logger
    __pool = pool
    logger = _logger
    return

class NoResourceError(Exception):
    pass

create_lock = threading.Lock()
domain_lock = {}

def guarantee_lock_exist(name):
    global domain_lock
    with create_lock:
        if name not in domain_lock:
            domain_lock[name] = threading.Lock()
    return

def decode_cookies(cookies_str):
    try:
        cookies = dict((x.strip().split('=', 1)) for x in cookies_str.split(';'))
    except:
        raise Exception('Cookies Decode Failed, origin: %s' % cookies_str)
    return cookies

def _get_new_resource(name):
    data = fetch_resource(name)
    if not data:
        logger.log('Get New Resource of %s Failed' % (name))
        if name not in __resource__:
            __resource__[name] = {
                "name": name,
                "error": True,
                "pool": [],
            }
        else:
            __resource__[name]['error'] = True
    else:
        logger.log('Get New Resource of %s, ID=%s' % (name, data['rid']))
        item = {
            "id": data['rid'],
            "quota": data.get('quota', 100),
            "cookies": decode_cookies(data['resource'])
            #"expire": None,
        }

        if name not in __resource__:
            __resource__[name] = {
                "name": name,
                "error": False,
                "pool": deque()
            }
        else:
            __resource__[name]['error'] = False
        __resource__[name]['pool'].append(item)
    return

def get_resource(name):
    guarantee_lock_exist(name)

    # need synchorize
    with domain_lock[name]:
        if name not in __resource__:
            _get_new_resource(name)
        data = __resource__[name]
        if data['error']:
            raise NoResourceError()
        if len(data['pool']) == 0:
            _get_new_resource(name)

        # because _get_new_resource may cause new error, check again
        if data['error']:
            raise NoResourceError()

        item = data['pool'][0]
        ret = item['cookies']
        item['quota'] -= 1
        print 'quota!!!\t%s' % item['quota']
        if item['quota'] <= 0:
            #TODO RETURN THIS ONE
            data['pool'].popleft()
        return ret

def _fetch_exception(e, name):
    logger.log('fetching %s got error %s' % (name, e))

@retry(times=3, except_callback=_fetch_exception)
def fetch_resource(name):
    payload = { 'token': __pool.token, 'name': name}
    r = requests.get(__pool.get_resource, timeout=5, params=payload)
    r.raise_for_status()
    j = r.json()
    if j['status'] != 'OK':
        raise Exception('Server Error')
    return j

def new_round():
    # remove all error
    need_to_remove = []
    for k, v in __resource__.iteritems():
        if v['error']:
            need_to_remove.append(k)

    for name in need_to_remove:
        del __resource__[name]

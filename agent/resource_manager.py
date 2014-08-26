import requests
import Queue

__resource__ = {}
__pool = None
logger = None
return_queue = Queue.Queue()
returner = None

from collections import deque
from util import retry
import threading
from daemon import ResourceReturner
import const

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
    global __pool, logger, returner
    __pool = pool
    logger = _logger
    returner = ResourceReturner(return_queue, logger, __pool)
    returner.start()
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
        cookies = dict((x.strip().split('=', 1)) for x in filter(lambda x: '=' in x, cookies_str.split(';')))
    except:
        raise Exception('Cookies Decode Failed, origin: %s' % cookies_str)
    return cookies

def _get_new_resource(name):
    data = fetch_resource(name)
    if not data:
        logger.error('Get New Resource of %s Failed' % (name))
        if name not in __resource__:
            __resource__[name] = {
                "name": name,
                "error": True,
                "pool": [],
            }
        else:
            __resource__[name]['error'] = True
    else:
        logger.info('Get New Resource of %s, ID=%s' % (name, data['rid']))
        item = {
            "id": data['rid'],
            "quota": data.get('times', const.DEFAULT_RESOURCE_QUOTA),
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
        ret = item
        item['quota'] -= 1
        if item['quota'] <= 0:
            #RETURN THIS ONE
            expired = data['pool'].popleft()
            logger.info('Resource %s - %s Expired' % (name, expired['id']))
            return_queue.put(expired)

        return ret

def _fetch_exception(e, name):
    logger.error('Fetching %s got error %s' % (name, e))

@retry(times=3, except_callback=_fetch_exception)
def fetch_resource(name):
    logger.debug('Fetching %s' % name)
    payload = { 'token': __pool.token, 'source': name}
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

def remove_unvalid(need_remove):
    for value in __resource__.itervalues():
        new = filter(lambda x: x['id'] not in need_remove, value['pool'])
        value['pool'] = deque(new)
    return

import requests
import util
import resource_manager
from requests.exceptions import ConnectionError, HTTPError, TooManyRedirects, Timeout
import const
from util import retry
import random
import time
from resource_manager import NoResourceError
import traceback

def basic_downloader(query, base_headers, timeout):
    result = __basic_downloader(query, base_headers, timeout)
    answer = generate_answer(result)
    return answer

def _exception(e, query, base_headers, timeout):
    print query['url']
    traceback.print_exc()
    time.sleep(random.random() * 5)
    return

def _fatal(e, query, base_headers, timeout):
    return {
        'query': query,
        'state': 'fail',
        'exception': e,
    }
    return e

@retry(times=const.RETRY_CNT_PER_URL, except_callback=_exception, fatal_callback=_fatal)
def __basic_downloader(query, base_headers, timeout):
    s = requests.session()
    url = query['url']
    arguments = {
        "headers": base_headers,
        "timeout": timeout,
        "allow_redirects": True,
    }
    used_cookies = None
    options = query.get('options', {})
    if options.get('login', False):
        resource_name = options['source']
        cookies = resource_manager.get_resource(resource_name)
        arguments['cookies'] = cookies['cookies']
        used_cookies = cookies
    redirect = True
    while redirect:
        r = s.get(url, **arguments)
        redirect, url = util.test_for_meta_redirections(r)
        r.raise_for_status()
    ret = {
        'query': query,
        'state': 'ok',
        'response': r,
    }

    if used_cookies:
        ret['resource_id'] = used_cookies['id']
    return ret

def judge_fail_reason(exception):
    fail_reason_map = {
        ConnectionError: const.FAIL_REASON['ConnectionError'],
        HTTPError: const.FAIL_REASON['HTTPError'],
        Timeout: const.FAIL_REASON['Timeout'],
        TooManyRedirects: const.FAIL_REASON['TooManyRedirects'],
        NoResourceError: const.FAIL_REASON['NoResourceError'],
    }
    return fail_reason_map.get(type(exception), const.FAIL_REASON['Other'])

def generate_answer(result):
    answer = {
        'url': result['query']['url']
    }
    if result.has_key('resource_id'):
        answer['resource_id'] = result['resource_id']

    if result['state'] == 'ok':
        r = result['response']
        extension = util.guess_extension(r)
        if extension in const.VALID_EXTENSION:
            answer['success'] = True
            answer['headers'] = {}
            answer['final_url'] = r.url
            for field in const.INTEREST_HEADER_FIELDS:
                if field in r.headers:
                    answer['headers'][field] = r.headers[field]
            answer['status_code'] = r.status_code

            encoding = util.guess_encoding(r, extension)
            if not encoding:
                answer['success'] = False
                answer['raw_exception_text'] = 'Failed to detect encoding'
                answer['fail_reason'] = const.FAIL_REASON['UnicodeDecodeError']
            else:
                r.encoding = encoding
                answer['content'] = r.text
        else:
            answer['success'] = False
            answer['raw_exception_text'] = 'Wrong extension, this is %s' % extension
            answer['fail_reason'] = const.FAIL_REASON['WrongExtension']
    else:
        answer['success'] = False
        answer['raw_exception_text'] = str(result['exception'])
        answer['fail_reason'] = judge_fail_reason(result['exception'])
    return answer

downloader_config = {
    'basic': basic_downloader,
    'render': None,
}

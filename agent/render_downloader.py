import subprocess
import tempfile
import os
import resource_manager
import util
from resource_manager import NoResourceError
import simplejson as json
import const
import traceback
import random
import time
from util import retry


class RenderTimeout(Exception):
    pass
class NoZeroError(Exception):
    pass

def render_downloader(query, base_headers, timeout):
    ret = phantom_js(query, base_headers, timeout)
    answer = generate_answer(ret, query)
    return answer

def _exception(e, query, base_headers, timeout):
    print query['url']
    traceback.print_exc()
    time.sleep(random.random() * 5)
    return

def _fatal(e, query, base_headers, timeout):
    return {
        'state': 'fail',
        'exception': e,
    }
    return e
@retry(times=const.RETRY_CNT_PER_URL, except_callback=_exception, fatal_callback=_fatal)
def phantom_js(query, base_headers, timeout):
    arguments = {
        "url": query['url'],
        "domain": util.extract_domain(query['url']),
        "headers": base_headers,
        "timeout": timeout,
    }
    used_cookies = None
    options = query.get('options', {})
    if options.get('login', False):
        resource_name = options['source']
        cookies = resource_manager.get_resource(resource_name)
        arguments['cookies'] = cookies['cookies']
        used_cookies = cookies

    try:
        infd, in_path = tempfile.mkstemp()
        # close output file first
        outfd, out_path = tempfile.mkstemp()
        os.fdopen(outfd).close
        in_params = os.fdopen(infd, 'wb')

        #Pass Arguments
        try:
            in_params.write(json.dumps(arguments))
        finally:
            in_params.close()
        time_left = const.RENDER_TIMEOUT_LIMIT

        RENDER_PATH = os.path.join(const.BASE_DIR, 'agent', 'render.js')

        proc = subprocess.Popen(['phantomjs', RENDER_PATH, in_path, out_path, '--disk-cache=yes', '--max-disk-cache-size 100000', '--web-security=no'])

        while proc.poll() is None:
            time.sleep(const.UPDATE_INTERVAL)
            time_left -= const.UPDATE_INTERVAL
            if time_left < 0:
                proc.kill()
                raise RenderTimeout()
        if proc.returncode != 0:
            raise NoZeroError()
        ret = None
        #Read return data
        with open(out_path) as f:
            ret = json.loads(f.read())

        if used_cookies:
            ret['resource_id'] = used_cookies['id']
        ret['state'] = 'ok'
        return ret
    finally:
        os.unlink(in_path)
        os.unlink(out_path)

def generate_answer(result, query):
    answer = {
        'url': query['url'],
    }
    if result.has_key('resource_id'):
        answer['resource_id'] = result['resource_id']
    if result['state'] == 'ok':
        answer['success'] = True
        headers = dict((x['name'].lower(), x['value']) for x in result['headers'])
        answer['headers'] = {}
        for field in const.INTEREST_HEADER_FIELDS:
            field = field.lower()
            if field in headers:
                answer['headers'][field] = headers[field]
        answer['status_code'] = result['status_code']
        answer['final_url'] = result['url']
        answer['content'] = result['doc']
        answer['iframes'] = result['iframes']
    else:
        answer['success'] = False
        answer['raw_exception_text'] = str(result['exception'])
        answer['fail_reason'] = judge_fail_reason(result['exception'])
    return answer

def judge_fail_reason(exception):
    fail_reason_map = {
        RenderTimeout: const.FAIL_REASON['Timeout'],
        NoResourceError: const.FAIL_REASON['NoResourceError'],
        NoZeroError: const.FAIL_REASON['RenderError'],
    }
    return fail_reason_map.get(type(exception), const.FAIL_REASON['Other'])

if __name__ == '__main__':
    print render_downloader({'url': 'http://www.google.com/fsdf/dsf'},
            {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.79 Safari/537.4',
            }
            , 30)

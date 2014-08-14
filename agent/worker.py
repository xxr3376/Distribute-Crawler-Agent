#!encoding=utf-8
import requests
import threading
import util
import const
import random
import time
from requests.exceptions import ConnectionError, HTTPError, TooManyRedirects, Timeout
from downloader import downloader_config

class Worker(threading.Thread):
    def __init__(self, query_list, timeout=const.READ_TIMEOUT_LIMIT):
        super(Worker, self).__init__()
        self.daemon = True
        self.query_list = query_list
        self.timeout = timeout
        self.answers = []

    def run(self):
        headers = self.generate_header()
        for query in self.query_list:
            result = self.crawl_query(query, headers)
            answer = self.generate_answer(result)
            self.answers.append(answer)
            time.sleep(random.random() * 5)
        return

    def judge_fail_reason(self, exception):
        fail_reason_map = {
            ConnectionError: const.FAIL_REASON['ConnectionError'],
            HTTPError: const.FAIL_REASON['HTTPError'],
            Timeout: const.FAIL_REASON['Timeout'],
            TooManyRedirects: const.FAIL_REASON['TooManyRedirects'],
        }
        return fail_reason_map.get(type(exception), const.FAIL_REASON['Other'])

    def generate_answer(self, result):
        answer = {
            'url': result['query']['url']
        }
        if result['state'] == 'ok':
            r = result['response']
            extension = util.guess_extension(r)
            if extension in const.VALID_EXTENSION:
                answer['success'] = True
                answer['content'] = r.text
                answer['headers'] = {}
                answer['final_url'] = r.url
                for field in const.INTEREST_HEADER_FIELDS:
                    if field in r.headers:
                        answer['headers'][field] = r.headers[field]
                answer['status_code'] = r.status_code
            else:
                answer['success'] = False
                answer['raw_exception_text'] = 'Wrong extension, this is %s' % extension
                answer['fail_reason'] = const.FAIL_REASON['WrongExtension']
        else:
            answer['success'] = False
            answer['raw_exception_text'] = str(result['exception'])
            answer['fail_reason'] = self.judge_fail_reason(result['exception'])
        return answer

    def crawl_query(self, query, headers):
        retry_cnt = 0
        # easy access for get data

        result = {}

        result['query'] = query
        downloader_type = query.get('downloader', 'basic')
        downloader = downloader_config[downloader_type]
        #each url will retry for N times
        while True:
            try:
                r = downloader(query, headers, self.timeout)
                # already get final html
                result['state'] = 'ok'
                result['response'] = r
                # done for crawl, exist repeat
                break
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                print query['url']
                print e
                retry_cnt += 1

                if retry_cnt >= const.RETRY_CNT_PER_URL:
                    result['state'] = 'fail'
                    result['exception'] = e
                    break
                else:
                    time.sleep(random.random() * 5)
        return result

    def generate_header(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': random.choice(const.LANGUAGE_POOL),
            'User-Agent': random.choice(const.UA_POOL),
        }
        return headers

#!encoding=utf-8
import threading
import const
import basic_downloader
import render_downloader
import time
import random


downloader_config = {
    'basic': basic_downloader.basic_downloader,
    'render': render_downloader.render_downloader,
}

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
            answer = self.crawl_query(query, headers)
            self.answers.append(answer)
            time.sleep(random.random() * 5)
        return

    def crawl_query(self, query, headers):
        downloader_type = query.get('options', {}).get('downloader', 'basic')
        downloader = downloader_config[downloader_type]
        #each url will retry for N times
        answer = downloader(query, headers, self.timeout)
        return answer

    def generate_header(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': random.choice(const.LANGUAGE_POOL),
            'User-Agent': random.choice(const.UA_POOL),
        }
        return headers

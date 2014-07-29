#!encoding=utf-8
import requests
import threading
import time

class TaskGetter(threading.Thread):
    def __init__(self, task_queue, logger, server_pool):
        super(TaskGetter, self).__init__()
        self.task_queue = task_queue
        self.logger = logger
        self.pool = server_pool
        self.daemon = True
        self.sleep_time = 1
    def run(self):
        while True:
            if self.task_queue.qsize() < 1:
                self.get_task()
            else:
                time.sleep(self.sleep_time)
        return

    def get_task(self):
        payload = { 'token': self.pool.token }
        try:
            r = requests.get(self.pool.control, params=payload, timeout=10)
            r.raise_for_status()
            data = r.json()
            if self.task_validator(data):
                self.task_queue.put(data)
                self.sleep_time = 1
            else:
                self.logger.log('receive unvalid queries')
                raise Exception('UNVALID QUERIES')
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            new_time = self.sleep_time * 2
            if new_time <= 64:
                self.sleep_time = new_time
        return

    def task_validator(self, data):
        return True

class TaskSubmitter(threading.Thread):
    def __init__(self, answer_queue, logger, server_pool):
        super(TaskSubmitter, self).__init__()
        self.answer_queue = answer_queue
        self.logger = logger
        self.pool = server_pool
        self.daemon = True
    def run(self):
        while True:
            job = self.answer_queue.get()
            print 'get!!!!!!! %s' % job.query_id
            try:
                self.submit(job)
                #submit answer
                pass
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.answer_queue.put(job)
                time.sleep(0.5)
    def submit(self, job):
        with open(job.zip_file_path, 'rb') as f:
            r = requests.post(self.pool.upload, \
                    data=job.meta, \
                    files={"file": f}\
                )
            print r.text
            r.raise_for_status()

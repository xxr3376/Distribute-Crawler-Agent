#!encoding=utf-8
import requests
import threading
import time
import const

class TaskGetter(threading.Thread):
    def __init__(self, task_queue, logger, server_pool):
        super(TaskGetter, self).__init__()
        self.task_queue = task_queue
        self.logger = logger
        self.pool = server_pool
        self.daemon = True
        self.sleep_time = const.BASIC_WAIT_TIME
    def run(self):
        while True:
            if self.task_queue.qsize() < const.QUEUE_MIN_LIMIT:
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
                self.sleep_time = const.BASIC_WAIT_TIME
            else:
                self.logger.log('receive unvalid queries')
                raise Exception('UNVALID QUERIES')
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            print e
            time.sleep(self.sleep_time)
            new_time = self.sleep_time * 2

            if new_time <= const.MAX_WAIT_TIME:
                self.sleep_time = new_time
        return

    def task_validator(self, data):
        #TODO
        if data['status'] != 'OK':
            raise Exception('No More Task!')
        return True

class TaskSubmitter(threading.Thread):
    def __init__(self, answer_queue, logger, server_pool):
        super(TaskSubmitter, self).__init__()
        self.answer_queue = answer_queue
        self.logger = logger
        self.pool = server_pool
        self.daemon = True
        self.sleep_time = const.BASIC_WAIT_TIME
    def run(self):
        while True:
            job = self.answer_queue.get()
            try:
                self.submit(job)
                self.sleep_time = const.BASIC_WAIT_TIME
                print 'submit success'
                #submit answer
                pass
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.answer_queue.put(job)
                time.sleep(self.sleep_time)

                new_time = self.sleep_time * 2
                if new_time <= const.MAX_WAIT_TIME:
                    self.sleep_time = new_time
    def submit(self, job):
        data = job.meta
        data['token'] = self.pool.token
        print data
        with open(job.zip_file_path, 'rb') as f:
            r = requests.post(self.pool.upload, \
                    data=data, \
                    files={"file": f}\
                )
            print r.content
            print r.status_code
            r.raise_for_status()

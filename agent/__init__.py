#!encoding=utf-8
import const
import server_pool
import daemon
import worker
import time
import util
from base_class import SubmitJob
#from collections import deque
import Queue

class Agent(object):
    def __init__(self, token, type_, logger):
        self.token = token
        self.type_ = type_
        self.logger = logger

        self.logger.log('Starting, agent type: %s, token: "%s"' % (type_, token))
        #register to master
        self.pool = server_pool.ServerPool(const.SERVER_INFO, self.token, self.logger)
        self.pool.update()

        self.tasks = Queue.Queue()
        self.answers = Queue.Queue()

        self.task_getter = daemon.TaskGetter(self.tasks, self.logger, self.pool)
        self.task_getter.start()

        self.task_submitter = daemon.TaskSubmitter(self.answers, self.logger, self.pool)
        self.task_submitter.start()
        return

    def schedule_jobs(self, task):
        domains = {}
        total = len(task['queries'])
        for query in task['queries']:
            domain = util.extract_domain(query['url'])
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(query)
        result = []
        for domain, jobs in domains.iteritems():
            l = len(jobs)
            if l < 2:
                result.append(jobs)
            elif l < 4:
                part = int(l / 2)
                result.append(jobs[0:part])
                result.append(jobs[part:])
            else:
                part = int(l / 4)
                for i in range(0, 4):
                    if i < 3:
                        result.append(jobs[part * i:part * (i + 1)])
                    else:
                        result.append(jobs[part * i:])
        # current just give each domain to one worker
        return result

    def alive_count(self, lst):
        alive = map(lambda x : 1 if x.isAlive() else 0, lst)
        return sum(alive)

    def post_process(self, task, answers):

        pass

    def one_pass(self):

        self.logger.log('Waiting Task')
        while True:
            try:
                current_task = self.tasks.get(timeout=5)
                break
            except Queue.Empty:
                #TODO report
                pass
        begin = time.time()
        jobs = self.schedule_jobs(current_task)

        self.logger.log('Task %s begin. Contains %s queries' % \
            (current_task['id'], len(current_task['queries']))\
        )
        self.logger.log('Task %s dispatch %s jobs' %\
            (current_task['id'], len(jobs))\
        )

        threads = [worker.Worker(job) for job in jobs]
        #threads = [worker.Worker(self.tasks[0]['queries'])]
        for thread in threads:
            # This is for easy killing
            thread.start()
        while self.alive_count(threads) > 0:
            time.sleep(const.UPDATE_INTERVAL)
        answers = []
        for thread in threads:
            answers += thread.answers

        submit_job = SubmitJob(current_task['id'], answers)
        self.answers.put(submit_job)

        timeuse = time.time() - begin
        self.logger.log('Task %s is done, timeuse: %s seconds' %\
            (current_task['id'], timeuse) \
        )
        return

    def run(self):
        while True:
            self.one_pass()

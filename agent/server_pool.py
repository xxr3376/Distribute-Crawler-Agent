import traceback
import time
import random
import requests
import threading

class ServerPool(object):
    def __init__(self, update_url, token, logger):
        self.logger = logger
        self.update_url = update_url
        self.__control = []
        self.__upload = []
        self.lock = threading.Lock()
        self.__get_resource = []
        self.__pay_resource = []
        self.token = token
        return
    def update(self):
        retry_cnt = 0
        while True:
            try:
                self.logger.debug('updating server_pool')
                r = requests.get(self.update_url, timeout=10)
                r.raise_for_status()
                self.parse(r.json())
                self.logger.info('update server_pool success, control_num:%s, upload_num:%s'\
                        % (len(self.__control), len(self.__upload)) \
                    )
                # DONE Everything
                break
            except (KeyboardInterrupt, SystemExit) as e:
                self.logger.info('receive kill signal, exiting')
                raise e
            except:
                #retry
                retry_cnt += 1
                if retry_cnt < 3:
                    self.logger.info('agent\'s info request failed, retry #%s' % retry_cnt)
                    self.logger.debug(traceback.format_exc())
                    time.sleep(random.random())
                else:
                    self.logger.critical('agent\'s info failed too many times')
                    raise Exception('request for info failed too many time')
        return

    def parse(self, data):
        with self.lock:
            self.__control = map(str, data['control_server'])
            self.__upload = map(str, data['upload_server'])
            self.__get_resource = map(str, data['get_resource'])
            self.__pay_resource = map(str, data['pay_resource'])
        return

    @property
    def control(self):
        with self.lock:
            return random.choice(self.__control)
    @property
    def upload(self):
        with self.lock:
            return random.choice(self.__upload)
    @property
    def get_resource(self):
        with self.lock:
            return random.choice(self.__get_resource)
    @property
    def pay_resource(self):
        with self.lock:
            return random.choice(self.__pay_resource)

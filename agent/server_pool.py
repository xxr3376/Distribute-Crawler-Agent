import logger
import traceback
import time
import random
import requests

class ServerPool(object):
    def __init__(self, update_url, token, logger):
        self.logger = logger
        self.update_url = update_url
        self.__control = []
        self.__upload = []
        self.token = token
        return
    def update(self):
        retry_cnt = 0
        while True:
            try:
                self.logger.log('updating server_pool')
                r = requests.get(self.update_url, timeout=10)
                r.raise_for_status()
                self.parse(r.json())
                self.logger.log('update server_pool success, control_num:%s, upload_num:%s'\
                        % (len(self.__control), len(self.__upload)) \
                    )
                # DONE Everything
                break
            except (KeyboardInterrupt, SystemExit) as e:
                self.logger.log('receive kill signal, exiting')
                raise e
            except:
                #retry
                retry_cnt += 1
                if retry_cnt < 3:
                    self.logger.log('agent\'s info request failed, retry #%s' % retry_cnt\
                        , logger.WARN)
                    self.logger.log(traceback.format_exc(), logger.WARN)
                    time.sleep(random.random())
                else:
                    self.logger.log('agent\'s info failed too many times', logger.FATAL)
                    raise Exception('request for info failed too many time')
        return

    def parse(self, data):
        self.__control = map(str, data['control_server'])
        self.__upload = map(str, data['upload_server'])
        return

    @property
    def control(self):
        return self.__control[0]

    @property
    def upload(self):
        return self.__upload[0]

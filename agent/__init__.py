#!encoding=utf-8
import requests
from requests.exceptions import ConnectionError, HTTPError, TooManyRedirects, Timeout
import const
import simplejson as json


def json_request(url, payload, **kwargs):
    headers = {'Content-type': 'application/json'}
    data = json.dumps(payload)
    return requests.post(url, data=data, headers=headers)

class Agent(object):
    def __init__(self, name, type_):
        #register to master
        data = {
            "name": name,
            "type": type_,
        }
        while True:
            try:
                r = json_request(const.SERVER_INFO, data, timeout=20)
                r.raise_for_status()
                self.server = r.json()
                break
            except (KeyboardInterrupt, SystemExit) as e:
                raise e
            except:
                #retry
                pass
        return

    def safe_request(url, **kwargs):
        try:
            requests(url, **kwargs)
        except (ConnectionError, HTTPError, TooManyRedirects):
            pass
        except Timeout:
            pass
        return

    def get_task():
        r = requests.get(const.GET_TASK, timeout=20)
        r.raise_for_status()

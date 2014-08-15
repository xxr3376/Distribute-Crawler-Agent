#!encoding=utf-8
from datetime import datetime
import sys

INFO, WARN, FATAL = range(3)

state = ['INFO', 'WARN', 'FATAL']

class Logger(object):
    def __init__(self):
        return
    def log(self, text, type_=INFO):
        self.stdout_log(type_, text)

    def stdout_log(self, type_, text):
        print "[%s]%s:\t%s" % (state[type_], datetime.now(), text)
        sys.stdout.flush()

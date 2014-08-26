#!encoding=utf-8
import logging
import logstash
import agent
import sys
import const

if len(sys.argv) != 2:
    print 'error'
    exit(0)

FORMAT = ('(agent-%s)' % sys.argv[1]) + '[%(levelname)s]%(asctime)s:%(message)s'

formatter = logging.Formatter(FORMAT)

logger = logging.getLogger('agent')
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)
logger.addHandler(console)

#remote = logstash.LogstashHandler(const.LOGSTASH_HOST, const.LOGSTASH_PORT, version=1)
#remote.setLevel(logging.INFO)
#remote.setFormatter(formatter)
#logger.addHandler(remote)

client = agent.Agent(sys.argv[1], 'normal', logger)

client.run()

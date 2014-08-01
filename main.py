#!encoding=utf-8
import agent.logger
import agent
import sys

logger = agent.logger.Logger()
if len(sys.argv) != 2:
    print 'error'
    exit(0)

client = agent.Agent(sys.argv[1], 'normal', logger)

client.run()

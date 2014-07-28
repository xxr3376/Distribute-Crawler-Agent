#!encoding=utf-8
import agent.logger
import agent

logger = agent.logger.Logger()

client = agent.Agent('hahaha', 'a', logger)

client.run()

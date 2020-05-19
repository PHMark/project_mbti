from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import numpy as np

class UserAgentRotatorMiddleware(UserAgentMiddleware):
	f = open('bypass_misc/user_agent_list.txt', 'r')
	user_agents = f.readlines()
	user_agents = list(map(lambda i: i.strip('\n'), user_agents))

	def __init__(self, user_agent=''):
		self.user_agent = user_agent

	def process_request(self, request, spider):
		rand_agent_index = np.random.randint(len(self.user_agents))	
		self.user_agent = self.user_agents[rand_agent_index]
		request.headers.setdefault('User-Agent', self.user_agent)
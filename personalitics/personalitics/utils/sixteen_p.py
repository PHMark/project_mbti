import re
import requests
import json
from urllib.parse import urljoin
from personalitics.utils.xpath_lookup import SixteenDiscussionXpath

xpath_topic_user = SixteenDiscussionXpath.XPATHS['topic_user']
xpath_topic = SixteenDiscussionXpath.XPATHS['topic']

class SixteenDiscussionContent:
	def __init__(self, response, cookies, i):
		self.response = response
		self.current_page_url = urljoin(response.url, '?page='+str(i))
		self.current_page = i
		self.cookies = cookies

		_page_type_ind = "Multi Pager" if i >= 1 else "One Pager"
		print("{} Current URL:  {}".format(_page_type_ind, self.current_page_url))

	def get_topic_content_values(self):
		topic_user_type = self.response.xpath(xpath_topic_user['user_type']).extract_first()

		if topic_user_type:
			topic_user_type = topic_user_type.strip()

		topic_title = self.response.xpath(xpath_topic['topic_title']).extract_first()
		topic_post = self.response.xpath(xpath_topic['topic_post']).extract()
		topic_user = {'avatar': self.response.xpath(xpath_topic_user['user_name']).extract_first(),
		'user_name': self.response.xpath(xpath_topic_user['user_name']).extract_first(),
		'user_type': topic_user_type,
		'posted_time_text': self.response.xpath(xpath_topic['posted_time_text']).extract_first(),
		'posted_datetime': self.response.xpath(xpath_topic['posted_datetime']).extract_first()
		}
		return topic_user_type, topic_title, topic_post, topic_user

	def get_post_id(self):
		id = re.findall(r'/([\d]+)/', self.current_page_url)[0]
		return id

	def get_comments(self, id, page, cookies):
		headers = {'content-type': 'application/json',
				   'accept': 'application/json, text/plain, */*',
				   'cookie': cookies
		}
		url = 'https://www.16personalities.com/community/discussions/comments/retrieve'
		success = False

		while not success:
			try:
				r = requests.post(url=url, headers=headers, data=json.dumps({"page": int(page), "id": int(id)}))
				success = True
			except:
				print('[REQUEST FAILED]: Retrying to send a new request.')
				success = False
		return json.dumps(r.json())

	def get_comments_json(self):
		# 1.) Get the Current Page Number
		page = self.current_page

		# 2.) Get the Current Post's id
		id = self.get_post_id()

		# 3.) Parse the comments in the current page
		comments = self.get_comments(id, page, self.cookies)

		return comments

	
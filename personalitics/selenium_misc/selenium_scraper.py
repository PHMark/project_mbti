from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
import pandas as pd
import numpy as np

browser = webdriver.Chrome(r"chromedriver.exe")

browser.get('https://www.16personalities.com/intj-personality#comments')

search_page = browser.find_element_by_xpath
users = []

links_to_scrape = browser.find_elements_by_xpath('//*[(@class="sections")]//a[@href[not(contains(., "/academy"))]]')
links_to_scrape = [l.get_attribute('href') for l in links_to_scrape]

for link in links_to_scrape:
	# Go to a section in page
	browser.get(link)

	# Parse mbti and section
	current_mbti = search_page('//div[@class="type-info"]/h1/span').text.lower()
	current_page = search_page('//li[@class="active"]').text.lower()


	while True:
		clicked_other = False
		while not clicked_other:
			# Click the other tab on comment section
			try:
				other_tab = search_page('//div[(text()[contains(.,"Other Comments")]) and (@class="title")]')
				other_tab.click()
				clicked_other = True
			except:
				print('Trying to click other....')
				time.sleep(np.random.uniform(1.3, 2.5))
				browser.get(browser.current_url)
				clicked_other = False

		# Get the list of comments
		comment_wrapper = browser.find_elements_by_xpath('//*[contains(@class, "comment-wrapper")]')
		
		for element in comment_wrapper:
			search_comments = element.find_element_by_xpath
			new_user = {}

			name = search_comments('.//div[@class="name"]//span').text
			if name.lower() == 'anonymous':
				user_id = 'anonymous'
				user_type = 'ASSERTIVE ARCHITECT (INTJ-A)'
			else:	
				user_id = search_comments('.//div[@class="name"]/a[@class="with-border"]').get_attribute('href')
				user_id = re.sub('.+\/profiles\/', '', user_id)
				user_type = search_comments('.//div[@class="type"]').text
				date = search_comments('//div[@class="date"]//span').get_attribute('title')
			user_comment = search_comments('.//div[@class="content"]').text
			new_user['user_id'] = user_id
			new_user['user_type'] = user_type
			new_user['text'] = user_comment
			new_user['date'] = date
			new_user['source'] = current_mbti + ' ' + current_page
			users.append(new_user)
		
		try:
			next_button = search_page('//a[contains(@rel, "next")]')
		except:
			break
			browser.quit()

		next_button.click()
		print('Next!!!!!!!!')
		time.sleep(np.random.uniform(1, 1.5))
		
# Close Chrome
browser.quit()
df = pd.DataFrame(users)
df.to_csv('output/intj.csv', index=False)


	
from bs4 import BeautifulSoup

class Xpath:	
	XPATHS = {}
	'''Xpath for each element in the comment section'''
	XPATHS['comment_section'] = {'user_comments': '//*[contains(@class, "comment-wrapper")]',
	'user_id': './/a[@class="with-border"]/@href',
	'user_type': './/div[@class="type"]/text()',
	'text': './/div[@class="content"]//text()',
	'date': './/div[@class="date"]//span/@title'
	}

	'''Scrapy Rule Xpath for: Traversing each Personality Type, Traversing each 
	   Section of a particular personality, Traversing each comment pages'''
	XPATHS['rules'] = {'types': '//div[contains(@class, "types")]//a[contains(@class, "type")]',
	'type_explorer': '//*[(@class="sections")]//a[@href[not(contains(., "/academy"))]]',
	'next_comment_section': '//a[contains(@rel, "next")]'
	}


def split_parent_child(string):
	'''Split the content inside a quoted text / parent message
	   and the content of the immediate text / child message
	'''
	soup = BeautifulSoup(string)
	bbcode_element = [i.extract() for i in soup.findAll('div')]
	parent_message = [j.get_text().strip() for j in bbcode_element]
	parent_message = ' '.join(parent_message).strip()
	parent_message = remove_template_words(parent_message)
	child_message = [i.get_text().strip() for i in soup]
	child_message = ' '.join(child_message).strip()

	return parent_message, child_message

def remove_template_words(string):
	'''Remove template words from a post'''
	string = string.replace('Originally Posted by ', '')
	string = ' '.join(string.split()[1:])
	return string

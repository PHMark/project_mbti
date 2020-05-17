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

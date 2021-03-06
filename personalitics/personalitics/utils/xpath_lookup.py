class SixteenpXpath:
	''' Rules Loop:
            X1 = Go to a Personality Type Page (Will return a page with a page with Type explorer, 
            and comments at the bottom of the page)
            ==> X2 = Explore a section in X1 (Will return the content of a section, and comments at the bottom)
            ==> Parse Comment(s) in X2 
            ==> X3 = Go to the next comment page in X2 (Will return a page with a list of comments)
            ==> Parse Comment(s) in X3 
    '''	
	XPATHS = {}

	XPATHS['rules'] = {'types': '//div[contains(@class, "types")]//a[contains(@class, "type")]',
	'type_explorer': '//*[(@class="sections")]//a[@href[not(contains(., "/academy"))]]',
	'next_comment_section': '//a[contains(@rel, "next")]'
	}

	# Xpath for each element in the comment section
	XPATHS['comment_section'] = {'user_comments': '//*[contains(@class, "comment-wrapper")]',
	'topic': '//li[@class="active"]/a/@href',
	'user_id': './/a[@class="with-border"]/@href',
	'user_type': './/div[@class="type"]/text()',
	'parent_text': './/*[contains(@class, "content") and not(parent::div[contains(@class, "subcomment")])]/text()',
	'child_text': './/*[contains(@class, "content") and (parent::div[contains(@class, "subcomment")])]/text()',
	'date': './/div[@class="date"]//span/@title'
	}


class SixteenDiscussionXpath:
	XPATHS = {}
	XPATHS['logged_in_user'] = '//div[@class="info"]//div[@class="name"]//text()'
	XPATHS['rules'] = { 'discussions': '//a[contains(@class, "discussions")]/@href',
	'categories': '//div[contains(@class, "category")]',
	'subcategory': './/div[@class="title"]/a/@href',
	'subcategories': './/div[@class="subcategories"]//a/@href',
	'threads': '//div[contains(@class, "thread")]//a/@href',
	'thread_last_page': '//a[@class="page-link"]/text()',
	'comments_last_page': '//li[@class="active"]//text()',
	'parse_content': '//div[@class="content"]',
	'active_page': '//div[@class="container"]/ul[@class="pagination"]/li[contains(@class, "active")]//text()'
	}

	XPATHS['topic_user'] = {'user_type': '//section[contains(@class, "meta")]//div[@class="poster"]//div[contains(@class, "type")]//text()',
	'user_name': '//section[contains(@class, "meta")]//div[@class="poster"]//div[contains(@class, "name")]//text()',
	'avatar': '//section[contains(@class, "meta")]//div[@class="poster"]//div[contains(@class, "avatar")]//img/@src'
	}

	XPATHS['topic'] = {'topic_title': '//section[@class="heading"]//span/text()',
	'topic_post': '//section[contains(@class, "meta")]//div[contains(@class, "content")]//div[@class="body"]//text()',
	'posted_time_text': '//section[contains(@class, "meta")]//div[@class="poster"]//div[contains(@class, "time")]//text()',
	'posted_datetime': '//section[contains(@class, "meta")]//div[@class="content"]//div[contains(@class, "time")]//@title'
	}

class PersonalityCafeXpath:
	''' Rules Loop:
            X1 = Go to a Personality Type Forum (Will return a page with a list of Threads)
            ==> X2 = Go to a thread in X1 (Will return a page with a list of Posts)
            ==> Parse Post(s) in X2 
            ==> X3 = Go to the next page in X2 (Will return a page with a list of Posts)
            ==> Parse Post(s) in X3 
            ==> X4 = Go to next page in X1 (Will return a page with a list of Threads)
    '''
	XPATHS = {}

	XPATHS['rules'] = {'type_threads': '//div[@class="body_wrap"]//a[contains(@href, "-forum-") and font[@color="#0033FF"]]',
	'posts': '//div[(@id!="forumbits") and (//div[(h2/span[text()[not(contains(., "Myers"))]])])]//a[contains(@id, "thread_title_") and (@class="title")]',
	'next_post': '//div[contains(@id, "bottom")]//a[contains(@rel, "next")]',
	'next_thread': '//div[(div//h1[text()[not(contains(., "Myers"))]])]//div[contains(@class, "below_threadlist")]//a[(@rel="next")]'
	} 

	# Xpath for each element in each post
	XPATHS['forum_post'] = {'thread_posts': '//ol[@id="posts"]//li[contains(@id, "post_") and not(contains(@id, "advert"))]',
	'topic': '//title/text()',
	'user_id': './/div[@class="userinfo"]//a[contains(@class, "username")]//text()',
	'user_type': './/div[@class="userinfo"]//span[@class="rank"]/preceding::div[1]/text()',
	'post_html': './/div[contains(@id, "post_message_")]/*[contains(@class, "postcontent restore")]',
	'date': './/span[@class="date"]/text()',
	'time': './/span[@class="time"]/text()'
	}
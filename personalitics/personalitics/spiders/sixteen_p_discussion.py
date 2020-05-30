# -*- coding: utf-8 -*-

import time
import json
import datetime
import socket
from urllib.parse import urljoin

from personalitics.items import PersonaliticsDiscussionItem
from personalitics.utils.sixteen_p import SixteenDiscussionContent
from personalitics.utils.xpath_lookup import SixteenDiscussionXpath
from personalitics.utils.lua_lookup import lua_dict

from scrapy.spiders import CrawlSpider
from scrapy.loader import ItemLoader
from scrapy.http import HtmlResponse
from scrapy import signals
from scrapy_splash import SplashRequest, SplashJsonResponse, SplashTextResponse

from tqdm import tqdm
import numpy as np


class SixteenPDiscussionSpider(CrawlSpider):
    name = 'sixteen_p_discussion'
    allowed_domains = ['16personalities.com']
    start_urls = ['https://www.16personalities.com/community']
    xpath_rules = SixteenDiscussionXpath.XPATHS['rules']
    xpath_logged_in_user = SixteenDiscussionXpath.XPATHS['logged_in_user']
    render_js = lua_dict['render_js']

    def start_requests(self):
        '''Start the very first request by logging in to the page
           then go to the after_login function'''

        lua_script = lua_dict['login']
        print('Logging in ....')
        yield SplashRequest(
                url='https://www.16personalities.com/community',
                endpoint='execute',
                cache_args=['lua_source'],
                session_id="foo",
                callback=self.after_login,
                args={'wait': 1, 'lua_source': lua_script}
            )
    
    def after_login(self, response):
        '''A function that is called after logging in to the page.
           This redirects the login page to the discussion page'''

        print('Logged in as: ', response.xpath(self.xpath_logged_in_user).extract_first().strip())
        discussions = response.xpath(self.xpath_rules['discussions']).extract_first()
        yield SplashRequest(urljoin(response.url, discussions),
                            endpoint='execute',
                            session_id="foo",
                            args={'wait': 1.5, 'lua_source': self.render_js},
                            callback=self.parse_category)

    def parse_category(self, response):
        '''Parse the category & subcategory links in the discussion page'''

        categories = response.xpath(self.xpath_rules['categories'])
        for url in categories:
            subcategories = url.xpath(self.xpath_rules['subcategories'])

            # If the current category has no subcategory
            if not subcategories:
                subcat_url = url.xpath(self.xpath_rules['subcategory']).extract_first()
                yield SplashRequest(urljoin(response.url, subcat_url),
                                    endpoint='execute',
                                    session_id="foo",
                                    args={'wait': 1, 'lua_source': self.render_js},
                                    callback=self.parse_thread_pagination)

            # If the current category has a subcategory
            else:
                for subcat_url in subcategories.extract():
                    yield SplashRequest(urljoin(response.url, subcat_url),
                                        endpoint='execute',
                                        session_id="foo",
                                        args={'wait': 1, 'lua_source': self.render_js},
                                        callback=self.parse_thread_pagination)

    def parse_thread_pagination(self, response):
        '''Parse all the Thread links from Page i to the Last Page'''

        thread_last_page = response.xpath(self.xpath_rules['thread_last_page'])[-2].get()
        for i in range(1, int(thread_last_page)+1):
            current_page_url = urljoin(response.url, '?&page='+str(i))
            yield SplashRequest(current_page_url,
                                endpoint='execute',
                                session_id="foo",
                                args={'wait': 0.5, 'lua_source': self.render_js},
                                callback=self.parse_thread)

    def parse_thread(self, response):
        '''A function that is called by parse_thread_pagination function.
           This function will visit a Thread'''

        threads = response.xpath(self.xpath_rules['threads'])
        print(response.url)
        for thread in threads.extract():
            yield SplashRequest(urljoin(response.url, thread),
                                        endpoint='execute',
                                        session_id="foo",
                                        args={'wait': 6.5, 'lua_source': self.render_js},
                                        callback=self.parse_content)

    def parse_content(self, response):
        '''Parse the content of the current Thread, from Page i to the Last Page'''

        self.pbar.update()
        ls_cookies = response.meta['splash']['args']['cookies']
        cookies = '; '.join([l['name'] + '=' + l['value'] for l in ls_cookies])
        last_page = response.xpath(self.xpath_rules['comments_last_page']).extract_first()

        # If Multi Pager
        if last_page and '{{' not in last_page:
            for i in range(1, int(last_page)+1):
                print("[Last Page: {}]".format(last_page))
                loader = ItemLoader(item=PersonaliticsDiscussionItem())

                discussion_content = SixteenDiscussionContent(response, cookies, i)

                # 1.) Get the content of the topic
                topic_user_type, topic_title, topic_post, topic_user = discussion_content.get_topic_content_values()
                
                # 2.) Get the comments json on the Current Page
                comments = discussion_content.get_comments_json()

                # 3.) Load the page items
                #
                # 3.1.) Housekeeping fields
                loader.add_value('project', self.settings.get('BOT_NAME'))
                loader.add_value('spider', self.name)
                loader.add_value('server', socket.gethostname())
                loader.add_value('created_at', datetime.datetime.now())

                # 3.2.) Primary fields
                loader.add_value('topic_title', topic_title)
                loader.add_value('topic_user', json.dumps(topic_user))
                loader.add_value('topic_post', ' '.join(topic_post))
                loader.add_value('comment_list', comments)
                loader.add_value('url', discussion_content.current_page_url)
                loader.add_value('id', discussion_content.get_post_id())

                time.sleep(np.random.uniform(0.75, 1.25))
                yield loader.load_item()

        # If One Pager
        else:
            loader = ItemLoader(item=PersonaliticsDiscussionItem())

            discussion_content = SixteenDiscussionContent(response, cookies, 1)

            # 1.) Get the content of the topic
            topic_user_type, topic_title, topic_post, topic_user = discussion_content.get_topic_content_values()
            
            # 2.) Get the comments json on the Current Page
            comments = discussion_content.get_comments_json()

             # 3.) Load the page items

            # 3.1.) Housekeeping fields
            loader.add_value('project', self.settings.get('BOT_NAME'))
            loader.add_value('spider', self.name)
            loader.add_value('server', socket.gethostname())
            loader.add_value('created_at', datetime.datetime.now())

            # 3.2.) Primary fields
            loader.add_value('topic_title', topic_title)
            loader.add_value('topic_user', json.dumps(topic_user))
            loader.add_value('topic_post', ' '.join(topic_post))
            loader.add_value('comment_list', comments)
            loader.add_value('url', discussion_content.current_page_url)
            loader.add_value('id', discussion_content.get_post_id())
            
            time.sleep(np.random.uniform(0.5, 1))
            yield loader.load_item()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SixteenPDiscussionSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_opened(self, spider):
        self.pbar = tqdm() 
        self.pbar.clear()
        self.pbar.write('Opening {} spider'.format(spider.name))

    def spider_closed(self, spider):
        self.pbar.clear()
        self.pbar.write('Closing {} spider'.format(spider.name))
        self.pbar.close()
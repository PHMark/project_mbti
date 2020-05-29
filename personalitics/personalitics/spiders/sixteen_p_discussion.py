# -*- coding: utf-8 -*-

import time
import json
import datetime
import socket
import requests
import re
from urllib.parse import urljoin

from personalitics.items import PersonaliticsDiscussionItem
from personalitics.utils import get_topic
from personalitics.utils.xpath_lookup import SixteenpXpath
from personalitics.utils.lua_lookup import lua_dict

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy.http import HtmlResponse
from scrapy.http import FormRequest, Request
from scrapy.utils.python import to_bytes
from scrapy.signalmanager import SignalManager
from scrapy import signals
from scrapy_splash import SplashRequest, SplashJsonResponse
from scrapy_splash import SplashTextResponse

from selenium import webdriver
from tqdm import tqdm
import numpy as np


class SixteenPDiscussionSpider(CrawlSpider, SixteenpXpath):
    name = 'sixteen_p_discussion'
    allowed_domains = ['16personalities.com']
    start_urls = ['https://www.16personalities.com/community']

    xpath_rules = SixteenpXpath.XPATHS['rules']
    xpath_comment_section = SixteenpXpath.XPATHS['comment_section']
    render_js = lua_dict['render_js']

    def start_requests(self):
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
        print('Logged in as: ', response.xpath('//div[@class="info"]//div[@class="name"]//text()').extract_first().strip())
        discussion = response.xpath('//a[contains(@class, "discussions")]/@href').extract_first()
        yield SplashRequest(urljoin(response.url, discussion),
                            endpoint='execute',
                            session_id="foo",
                            args={'wait': 1.5, 'lua_source': self.render_js},
                            callback=self.parse_category)

    def parse_category(self, response):
        categories = response.xpath('//div[contains(@class, "category")]')

        for url in categories:
            subcategories = url.xpath('.//div[@class="subcategories"]//a/@href')
            if not subcategories:
                subcat_url = url.xpath('.//div[@class="title"]/a/@href').extract_first()
                yield SplashRequest(urljoin(response.url, subcat_url),
                                    endpoint='execute',
                                    session_id="foo",
                                    args={'wait': 1, 'lua_source': self.render_js},
                                    callback=self.parse_thread_pagination)

            else:
                for subcat_url in subcategories.extract():
                    yield SplashRequest(urljoin(response.url, subcat_url),
                                        endpoint='execute',
                                        session_id="foo",
                                        args={'wait': 1, 'lua_source': self.render_js},
                                        callback=self.parse_thread_pagination)

    # 1.) Go to page x
    def parse_thread_pagination(self, response):
        last_page = response.xpath('//a[@class="page-link"]/text()')[-2].get()
        for i in range(1, int(last_page)):
            current_page_url = urljoin(response.url, '?&page='+str(i))
            yield SplashRequest(current_page_url,
                                endpoint='execute',
                                session_id="foo",
                                args={'wait': 0.5, 'lua_source': self.render_js},
                                callback=self.parse_thread)

    def parse_thread(self, response):
        threads = response.xpath('//div[contains(@class, "thread")]//a/@href')
        print(response.url)
        for thread in threads.extract():
            yield SplashRequest(urljoin(response.url, thread),
                                        endpoint='execute',
                                        session_id="foo",
                                        args={'wait': 6.5, 'lua_source': self.render_js},
                                        callback=self.parse_content)

    def parse_content(self, response):
        self.pbar.update()
        
        ls = response.meta['splash']['args']['cookies']
        cookies = '; '.join([l['name'] + '=' + l['value'] for l in ls])
        last_page = response.xpath('//li[@class="active"]//text()').extract_first()

        if last_page and '{{' not in last_page:
            for i in range(1, int(last_page)+1):
                loader = ItemLoader(item=PersonaliticsDiscussionItem())
                user_type = response.xpath('//section[contains(@class, "meta")]//div[@class="poster"]//div[contains(@class, "type")]//text()').extract_first()
                if user_type:
                    user_type = user_type.strip()
                 # 1.) Get topic title & topic post
                topic_title = response.xpath('//section[@class="heading"]//span/text()').extract_first()
                topic_user = {'avatar': response.xpath('//section[contains(@class, "meta")]//div[@class="poster"]//div[contains(@class, "avatar")]//img/@src').extract_first(),
                'user_name': response.xpath('//section[contains(@class, "meta")]//div[@class="poster"]//div[contains(@class, "name")]//text()').extract_first(),
                'user_type': user_type,
                'posted_time_text': response.xpath('//section[contains(@class, "meta")]//div[@class="poster"]//div[contains(@class, "time")]//text()').extract_first(),
                'posted_datetime': response.xpath('//section[contains(@class, "meta")]//div[@class="content"]//div[contains(@class, "time")]//@title').extract_first()
                }
                topic_post = response.xpath('//section[contains(@class, "meta")]//div[contains(@class, "content")]//div[@class="body"]//text()').extract()
                
                # Housekeeping fields
                loader.add_value('project', self.settings.get('BOT_NAME'))
                loader.add_value('spider', self.name)
                loader.add_value('server', socket.gethostname())
                loader.add_value('created_at', datetime.datetime.now())

                # Primary fields
                loader.add_value('topic_title', topic_title)
                loader.add_value('topic_user', json.dumps(topic_user))
                loader.add_value('topic_post', ' '.join(topic_post))

                current_page_url = urljoin(response.url, '?page='+str(i))
                print("Multi Pager Current URL: [Last Page: {}] {}".format(last_page, current_page_url))
                loader.add_value('url', current_page_url)

                # 1.1.) Get id
                id = re.findall(r'/([\d]+)/', current_page_url)[0]
                loader.add_value('id', id)

                # 1.2.) Get page
                page = i

                # 1.3.) Get comments
                comments = self.get_comments(id, page, cookies)

                loader.add_value('comment_list', comments)
                time.sleep(np.random.uniform(0.75, 1.5))
                yield loader.load_item()

        else:
            loader = ItemLoader(item=PersonaliticsDiscussionItem())
            user_type = response.xpath('//section[contains(@class, "meta")]//div[@class="poster"]//div[contains(@class, "type")]//text()').extract_first()
            if user_type:
                user_type = user_type.strip()
             # 1.) Get topic title & topic post
            topic_title = response.xpath('//section[@class="heading"]//span/text()').extract_first()
            topic_user = {'avatar': response.xpath('//section[contains(@class, "meta")]//div[@class="poster"]//div[contains(@class, "avatar")]//img/@src').extract_first(),
            'user_name': response.xpath('//section[contains(@class, "meta")]//div[@class="poster"]//div[contains(@class, "name")]//text()').extract_first(),
            'user_type': user_type,
            'posted_time_text': response.xpath('//section[contains(@class, "meta")]//div[@class="poster"]//div[contains(@class, "time")]//text()').extract_first(),
            'posted_datetime': response.xpath('//section[contains(@class, "meta")]//div[@class="content"]//div[contains(@class, "time")]//@title').extract_first()
            }
            topic_post = response.xpath('//section[contains(@class, "meta")]//div[contains(@class, "content")]//div[@class="body"]//text()').extract()
            
            # Housekeeping fields
            loader.add_value('project', self.settings.get('BOT_NAME'))
            loader.add_value('spider', self.name)
            loader.add_value('server', socket.gethostname())
            loader.add_value('created_at', datetime.datetime.now())

            # Primary fields
            loader.add_value('topic_title', topic_title)
            loader.add_value('topic_user', json.dumps(topic_user))
            loader.add_value('topic_post', ' '.join(topic_post))

            # One pager
            current_page_url = response.url
            print("One Pager Current URL: {}".format(current_page_url))
            loader.add_value('url', current_page_url)

            # 1.1.) Get id
            id = re.findall(r'/([\d]+)/', current_page_url)[0]
            loader.add_value('id', id)

            # 1.2.) Get page
            page = 1

            # 1.3.) Get comments
            comments = self.get_comments(id, page, cookies)
            loader.add_value('comment_list', comments)
            time.sleep(np.random.uniform(0.75, 1.25))
            yield loader.load_item()

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

    # Source https://github.com/scrapy-plugins/scrapy-splash/issues/92
    def _requests_to_follow(self, response):
        if not isinstance(
                response,
                (HtmlResponse, SplashJsonResponse, SplashTextResponse)):
            return
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [lnk for lnk in rule.link_extractor.extract_links(response)
                     if lnk not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                r = self._build_request(n, link)
                yield rule.process_request(r)
    
    def use_splash(self, request):
        request.meta.update(splash={
            'session_id': "foo",
            'args': {
                'wait': 0.5,
            },

            'endpoint': 'render.html',
        })
        return request

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
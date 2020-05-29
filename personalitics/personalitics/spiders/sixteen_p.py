# -*- coding: utf-8 -*-

import time
import json
import datetime
import socket
from urllib.parse import urljoin
from personalitics.items import PersonaliticsItem
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


class SixteenPSpider(CrawlSpider, SixteenpXpath):
    name = 'sixteen_p'
    allowed_domains = ['16personalities.com']
    start_urls = ['https://www.16personalities.com/personality-types']

    xpath_rules = SixteenpXpath.XPATHS['rules']
    xpath_comment_section = SixteenpXpath.XPATHS['comment_section']
    render_js = lua_dict['render_js']

    def start_requests(self):
        lua_script = lua_dict['login']

        yield SplashRequest(
                url='https://www.16personalities.com/personality-types',
                endpoint='execute',
                cache_args=['lua_source'],
                session_id="foo",
                callback=self.parse_types,
                args= {'wait': 0.5, 'lua_source': lua_script}
            )

    # rules = [
    #         Rule(LinkExtractor(restrict_xpaths=xpath_rules['types']), follow=True, ),
    #         Rule(LinkExtractor(restrict_xpaths=xpath_rules['type_explorer']), callback='parse_comment', process_request='use_splash', follow=True),
    #         Rule(LinkExtractor(restrict_xpaths=xpath_rules['next_comment_section']), callback='parse_comment', process_request='use_splash', follow=True)
    #     ]

    def parse_types(self, response):
        # print(response.xpath('//div[@class="info"]//div[@class="name"]//text()').extract_first().strip())

        # Parse Type List
        type_selector = response.xpath(self.xpath_rules['types'] + '/@href')
        for url in type_selector.extract():
            yield SplashRequest(urljoin('https://www.16personalities.com/', url),
                                endpoint='execute',
                                session_id="foo",
                                args={'lua_source': self.render_js},
                                callback=self.parse_explorer)

    def parse_explorer(self, response):
        # print(response.xpath('//div[@class="info"]//div[@class="name"]//text()').extract_first().strip())

        # Parse Explorer List
        explore_selector = response.xpath(self.xpath_rules['type_explorer'] + '/@href')
        for url in explore_selector.extract():
            yield SplashRequest(urljoin('https://www.16personalities.com/', url),
                                endpoint='execute',
                                session_id="foo",
                                # headers = response.data['headers'],
                                args={'lua_source': self.render_js},
                                callback=self.parse_comment)

    def parse_comment(self, response):
        self.pbar.update()
        user_comments = response.xpath(self.xpath_comment_section['user_comments'])
        print(response.xpath('//div[@class="info"]//div[@class="name"]//text()').extract_first().strip())

        # Parse next comment page
        next_selector = response.xpath(self.xpath_rules['next_comment_section'] + '/@href')
        for url in next_selector.extract():
            yield SplashRequest(urljoin('https://www.16personalities.com/', url),
                                endpoint='execute',
                                session_id="foo",
                                # headers = response.data['headers'],
                                args={'lua_source': self.render_js},
                                callback=self.parse_comment)

        # Loop over the comment list
        for element in user_comments:
            loader = ItemLoader(item=PersonaliticsItem())

            # Main fields
            loader.add_value('topic', get_topic(element.xpath(self.xpath_comment_section['topic']).extract_first()))
            loader.add_value('user_id', element.xpath(self.xpath_comment_section['user_id']).extract_first())
            loader.add_value('user_type', element.xpath(self.xpath_comment_section['user_type']).extract_first())
            loader.add_value('parent_text', element.xpath(self.xpath_comment_section['parent_text']).extract_first())
            loader.add_value('child_text', element.xpath(self.xpath_comment_section['child_text']).extract_first())
            loader.add_value('date', element.xpath(self.xpath_comment_section['date']).extract_first())

            # House keeping fields
            loader.add_value('source', response.url)
            loader.add_value('project', self.settings.get('BOT_NAME'))
            loader.add_value('spider', self.name)
            loader.add_value('server', socket.gethostname())
            loader.add_value('created_at', datetime.datetime.now())
            yield loader.load_item()

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
                'wait': 1,
            },

            'endpoint': 'render.html',
        })
        return request

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SixteenPSpider, cls).from_crawler(crawler, *args, **kwargs)
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
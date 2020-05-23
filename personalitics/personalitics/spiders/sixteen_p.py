# -*- coding: utf-8 -*-

import time
import datetime
import socket
from personalitics.items import PersonaliticsItem
from personalitics.utils import get_topic
from personalitics.utils.xpath_lookup import SixteenpXpath

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy.http import HtmlResponse
from scrapy_splash import SplashTextResponse
from scrapy.utils.python import to_bytes
from scrapy.signalmanager import SignalManager
from scrapy import signals
from scrapy_splash import SplashRequest, SplashJsonResponse

from selenium import webdriver
from tqdm import tqdm
import numpy as np


class SixteenPSpider(CrawlSpider, SixteenpXpath, scrapy.spiders.crawl):
    name = 'sixteen_p'
    xpath_rules = SixteenpXpath.XPATHS['rules']
    xpath_comment_section = SixteenpXpath.XPATHS['comment_section']
    allowed_domains = ['16personalities.com']
    start_urls = ['https://www.16personalities.com/personality-types']
    rules = [
            Rule(LinkExtractor(restrict_xpaths=xpath_rules['types']), follow=True, ),
            Rule(LinkExtractor(restrict_xpaths=xpath_rules['type_explorer']), callback='parse_comment', process_request='use_splash', follow=True),
            Rule(LinkExtractor(restrict_xpaths=xpath_rules['next_comment_section']), callback='parse_comment', process_request='use_splash', follow=True)
        ]

    def parse_comment(self, response):
        self.pbar.update()
        user_comments = response.xpath(self.xpath_comment_section['user_comments'])
        print(user_comments)
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
            print( loader.load_item())
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
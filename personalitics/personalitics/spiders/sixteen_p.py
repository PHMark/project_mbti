# -*- coding: utf-8 -*-

import time
import datetime
import socket
from personalitics.items import PersonaliticsItem
from personalitics.spiders.utils import Xpath

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy.http import HtmlResponse
from scrapy.utils.python import to_bytes
from scrapy.signalmanager import SignalManager
from scrapy import signals

from selenium import webdriver
from tqdm import tqdm
import numpy as np


class SixteenPSpider(CrawlSpider, Xpath):
    name = 'sixteen_p'
    xpath_rules = Xpath.XPATHS['rules']
    xpath_comment_section = Xpath.XPATHS['comment_section']

    def __init__(self, *args, **kwargs):
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe')
        self.allowed_domains = ['16personalities.com']
        self.start_urls = ['https://www.16personalities.com/personality-types']
        
        self.rules = [
            Rule(LinkExtractor(restrict_xpaths=self.xpath_rules['types']), follow=True),
            Rule(LinkExtractor(restrict_xpaths=self.xpath_rules['type_explorer']), callback='parse_comment', follow=True),
            Rule(LinkExtractor(restrict_xpaths=self.xpath_rules['next_comment_section']), callback='parse_comment', follow=True),
        ]

        super(SixteenPSpider, self).__init__(*args, **kwargs)

    def parse_comment(self, response):
        self.pbar.update()

        response = self.process_response(response.url)
        user_comments = response.xpath(self.xpath_comment_section['user_comments'])

        # Loop over the comment list
        for element in user_comments:
            loader = ItemLoader(item=PersonaliticsItem())

            # Main fields
            loader.add_value('user_id', element.xpath(self.xpath_comment_section['user_id']).extract_first())
            loader.add_value('user_type', element.xpath(self.xpath_comment_section['user_type']).extract_first())
            loader.add_value('child_text', element.xpath(self.xpath_comment_section['text']).extract_first())
            loader.add_value('date', element.xpath(self.xpath_comment_section['date']).extract_first())

            # House keeping fields
            loader.add_value('source', response.url)
            loader.add_value('project', self.settings.get('BOT_NAME'))
            loader.add_value('spider', self.name)
            loader.add_value('server', socket.gethostname())
            loader.add_value('created_at', datetime.datetime.now())

            yield loader.load_item()

    def process_response(self, url):
        ''' 
            Modify the response of a URL to render the needed elements from the
            `Other Comment` tab.
            
            Parameters
            ----------
            url : str
                  The URL of response that we will modify
            
            Returns
            -------
            resp : HtmlResponse
                   The modified response of URL
        '''

        self.driver.get(url)
        clicked_other = False

        # Click the `Other` tab in the comment section
        while not clicked_other:
            try:
                other_tab = self.driver.find_element_by_xpath('//div[(text()[contains(.,"Other Comments")]) and (@class="title")]')
                other_tab.click()
                clicked_other = True
            except:
                print('Failed clicking, retrying to click the `Other` tab button....')
                time.sleep(np.random.uniform(1.3, 2.5))
                self.driver.get(self.driver.current_url)
                clicked_other = False

        body = to_bytes(self.driver.page_source)
        resp = HtmlResponse(self.driver.current_url, body=body, encoding='utf-8')
        return resp

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
        if self.driver:
            self.driver.quit()
            self.driver = None
        self.pbar.clear()
        self.pbar.write('Closing {} spider'.format(spider.name))
        self.pbar.close()
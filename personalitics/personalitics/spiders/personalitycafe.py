# -*- coding: utf-8 -*-

import socket
import datetime
from personalitics.items import PersonaliticsItem
from personalitics.spiders import utils

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy import signals

from html2text import html2text
from tqdm import tqdm

class PersonalitycafeSpider(CrawlSpider):
    name = 'personalitycafe'
    allowed_domains = ['personalitycafe.com']
    start_urls = ['https://www.personalitycafe.com/myers-briggs-forum']

    ''' Rules Loop:
            X1 = Go to a Personality Type Forum (Will return a page with a list of Threads)
            ==> X2 = Go to a thread in X1 (Will return a page with a list of Posts)
            ==> Parse Post(s) in X2 
            ==> X3 = Go to next page in X2 (Will return a page with a list of Posts)
            ==> Parse Post(s) in X3 
            ==> X4 = Go to next page in X1 (Will return a page with a list of Threads)
    '''
    rules = (
        Rule(LinkExtractor(restrict_xpaths='//div[@class="body_wrap"]//a[contains(@href, "-forum-") and font[@color="#0033FF"]]'), 
             follow=True),
        Rule(LinkExtractor(restrict_xpaths='//div[(@id!="forumbits") and (//div[(h2/span[text()[not(contains(., "Myers"))]])])]//a[contains(@id, "thread_title_") and (@class="title")]'), 
             follow=True, callback='parse_post'),
        Rule(LinkExtractor(restrict_xpaths='//div[contains(@id, "bottom")]//a[contains(@rel, "next")]'), 
             follow=True, callback='parse_post'),
        Rule(LinkExtractor(restrict_xpaths='//div[(div//h1[text()[not(contains(., "Myers"))]])]//div[contains(@class, "below_threadlist")]//a[(@rel="next")]'), 
             follow=True),
    )

    def parse_post(self, response):
        self.pbar.update()
        
        # For debugging
        self.pbar.set_description("Current URL: {}".format(response.url))

        thread_posts = response.xpath('//ol[@id="posts"]//li[contains(@id, "post_") and not(contains(@id, "advert"))]')
        for post in thread_posts:
            topic = post.xpath('//title/text()').extract_first()
            user_id = post.xpath('.//div[@class="userinfo"]//a[contains(@class, "username")]//text()').extract_first()
            user_type = post.xpath('.//div[@class="userinfo"]//span[@class="rank"]/preceding::div[1]/text()').extract_first()
            html_text = post.xpath('.//div[contains(@id, "post_message_")]/*[contains(@class, "postcontent restore")]').extract_first()
            parent_text, child_text = utils.split_parent_child(html_text)
            date = post.xpath('.//span[@class="date"]/text()').extract_first()
            time = post.xpath('.//span[@class="time"]/text()').extract_first()
            date_time = date + u' ' + time

            # Main fields
            loader = ItemLoader(item=PersonaliticsItem())
            loader.add_value('topic', topic)
            loader.add_value('user_id', user_id)
            loader.add_value('user_type', user_type)
            loader.add_value('parent_text', parent_text)
            loader.add_value('child_text', child_text)
            loader.add_value('date', date_time, MapCompose(lambda i: i.encode('ascii', errors='ignore').decode("utf-8")))

            # Housekeeping fields
            loader.add_value('source', response.url)
            loader.add_value('project', self.settings.get('BOT_NAME'))
            loader.add_value('spider', self.name)
            loader.add_value('server', socket.gethostname())
            loader.add_value('created_at', datetime.datetime.now())
            # print(loader.load_item())
            yield loader.load_item()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(PersonalitycafeSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_opened(self, spider):
        self.pbar = tqdm() 
        self.pbar.write('Opening {} spider'.format(spider.name))

    def spider_closed(self, spider):
        self.pbar.write('Closing {} spider'.format(spider.name))
        self.pbar.close()
        
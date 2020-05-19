# -*- coding: utf-8 -*-

import socket
import datetime
from personalitics.items import PersonaliticsItem
from personalitics import utils
from personalitics.utils.xpath_lookup import PersonalityCafeXpath
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy import signals

from html2text import html2text
from tqdm import tqdm

class PersonalitycafeSpider(CrawlSpider, PersonalityCafeXpath):
    name = 'personalitycafe'
    allowed_domains = ['personalitycafe.com']
    start_urls = ['https://www.personalitycafe.com/myers-briggs-forum']
    xpath_rules = PersonalityCafeXpath.XPATHS['rules']
    xpath_forum_post = PersonalityCafeXpath.XPATHS['forum_post']

    rules = (
        Rule(LinkExtractor(restrict_xpaths=xpath_rules['type_threads']), 
             follow=True),
        Rule(LinkExtractor(restrict_xpaths=xpath_rules['posts']), 
             follow=True, callback='parse_post'),
        Rule(LinkExtractor(restrict_xpaths=xpath_rules['next_post']), 
             follow=True, callback='parse_post'),
        Rule(LinkExtractor(restrict_xpaths=xpath_rules['next_thread']), 
             follow=True),
    )

    def parse_post(self, response):
        self.pbar.update()
        self.pbar.set_description("Current URL: {}".format(response.url))

        thread_posts = response.xpath(self.xpath_forum_post['thread_posts'])

        for post in thread_posts:
            # Extracting Main fields
            topic = post.xpath(self.xpath_forum_post['topic']).extract_first()
            user_id = post.xpath(self.xpath_forum_post['user_id']).extract_first()
            user_type = post.xpath(self.xpath_forum_post['user_type']).extract_first()
            post_html = post.xpath(self.xpath_forum_post['post_html']).extract_first()
            parent_text, child_text = utils.split_parent_child(post_html)
            date = post.xpath(self.xpath_forum_post['date']).extract_first()
            time = post.xpath(self.xpath_forum_post['time']).extract_first()
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
        
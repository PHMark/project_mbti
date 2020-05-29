# -*- coding: utf-8 -*-
import scrapy
from personalitics.utils.xpath_lookup import SixteenpXpath


class SixteenPArticlesSpider(scrapy.spiders.CrawlSpider):
    name = 'sixteen_p_articles'
    allowed_domains = ['16personalities.com']
    xpath_comment_section = SixteenpXpath.XPATHS['comment_section']

    start_urls = ['https://www.16personalities.com/articles/6-times-architect-intj-personality-types-spiked-the-stats']


    def parse(self, response):
        user_comments = response.xpath(self.xpath_comment_section['user_comments'])

        # Loop over the comment list
        for element in user_comments:
        	print({'user_id': element.xpath(self.xpath_comment_section['user_id']).extract_first(),
        		'user_type': element.xpath(self.xpath_comment_section['user_type']).extract_first(),
        		'parent_text': element.xpath(self.xpath_comment_section['parent_text']).extract_first(),
        		'child_text': element.xpath(self.xpath_comment_section['child_text']).extract_first(),
        		'date': element.xpath(self.xpath_comment_section['date']).extract_first()
        		})
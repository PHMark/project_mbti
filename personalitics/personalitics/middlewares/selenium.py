# from scrapy.http import HtmlResponse
# from scrapy.utils.python import to_bytes
# from selenium import webdriver
# from scrapy import signals
# import time
# import numpy as np

# class SeleniumMiddleware(object):

#     @classmethod
#     def from_crawler(cls, crawler):
#         middleware = cls()
#         crawler.signals.connect(middleware.spider_opened, signals.spider_opened)
#         crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
#         return middleware

#     def process_request(self, request, spider):
#         request.meta['driver'] = self.driver  # to access driver from response
#         self.driver.get(request.url)

#         clicked_other = False
#         while not clicked_other:
#             # Click the other tab on comment section
#             try:
#                 other_tab = self.driver.find_element_by_xpath('//div[(text()[contains(.,"Other Comments")]) and (@class="title")]')
#                 other_tab.click()
#                 clicked_other = True
#             except:
#                 print('Trying to click other comment....')
#                 time.sleep(np.random.uniform(1.3, 2.5))
#                 self.driver.get(self.driver.current_url)
#                 clicked_other = False

#         body = to_bytes(self.driver.page_source)  # body must be of type bytes 
#         return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)

#     def spider_opened(self, spider):
#         self.driver = webdriver.Chrome(r"chromedriver.exe")

#     def spider_closed(self, spider):
#         self.driver.close()
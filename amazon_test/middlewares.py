# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class AmazonTestSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class AmazonTestDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# class UserAgentDownloadMiddleware(object):
#     """
#     随机使用 User Agent 中间件
#     """
#     def process_request(self, request, spider):
#         """
#         每次请求都会添加一个随机的 UA
#         :param request:
#         :param spider:
#         :return:
#         """
#         user_agent = random.choice(USER_AGENT_LIST)
#         request.headers['User-Agent'] = user_agent
#         # request.headers.setdefault('User-Agent', user_agent)
#         spider.logger.info(f"[User-Agent] : {user_agent}")



from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from logging import getLogger

from selenium.webdriver.chrome.options import Options


class SeleniumMiddleware():
    def __init__(self, timeout=None):
        chrome_options = Options()
        chrome_options.add_argument('window-size=1920x1260')  # 指定浏览器分辨率
        chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
        # chrome_options.add_argument('--headless')

        # self.logger = getLogger(__name__)
        self.timeout = timeout
        self.browser = webdriver.Chrome(executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe", options=chrome_options)
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)

    def __del__(self):
        self.browser.close()

    def process_request(self, request, spider):
        """
            用PhantomJS抓取页面
            :param request: Request对象
            :param spider: Spider对象
            :return: HtmlResponse
            """
        spider.logger.debug('Chrome is Starting')
        # page = request.meta.get('page', 1)  # 通过Request的meta属性获取当前需要爬取的页码
        try:
            self.browser.get(request.url)
            # if page > 1:
            #     input = self.wait.until(
            #         EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager div.form > input')))  # 选择页码框
            #     submit = self.wait.until(
            #         EC.element_to_be_clickable(
            #             (By.CSS_SELECTOR, '#mainsrp-pager div.form > span.btn.J_Submit')))  # 确定按钮
            #     input.clear()
            #     input.send_keys(page)
            #     submit.click()
            # self.wait.until(
            #     EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager li.item.active > span'),
            #                                      str(page)))  # 第一页
            # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.m-itemlist .items .item')))  # 单个商品概览
            return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8',
                                status=200)  # 调用page_source属性获取页码的源代码，用它来直接构造并返回一个HtmlResponse对象，构造这个对象需要传入url,body等多个参数
        except TimeoutException:
            return HtmlResponse(url=request.url, status=500,
                                request=request)  # 返回一个HtmlResponse对象。利用PhantomJS代替Scrapy完成页面的加载，最后将Response返回，回传给Spider内的回调函数进行解析

    @classmethod
    def from_crawler(cls, crawler):
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'))

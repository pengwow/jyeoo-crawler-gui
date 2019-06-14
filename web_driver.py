# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import DesiredCapabilities
from interface.utils import get_phantomjs_path


class WebDriver(object):
    def __init__(self):
        self.phantomjs_path = get_phantomjs_path()
        self.desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
        # get()方法会一直等到页面被完全加载，然后才会继续程序
        headers = {'Accept': '*/*',
                   'Accept-Language': 'en-US,en;q=0.8',
                   'Cache-Control': 'max-age=0',
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
                   'Connection': 'keep-alive',
                   }
        for key, value in headers.items():
            self.desired_capabilities['phantomjs.page.customHeaders.{}'.format(key)] = value

        self.desired_capabilities[
            'phantomjs.page.customHeaders.User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        self.driver = None

    def init_phantomjs_driver(self):
        self.driver = webdriver.PhantomJS(executable_path=self.phantomjs_path,
                                          desired_capabilities=self.desired_capabilities)

    def __del__(self):
        self.driver.quit()
        # driver.get("http://www.jyeoo.com/math2/ques/search")
        #
        # # 获取页面名为wrapper的id标签的文本内容
        # data = driver.find_element_by_id("pageArea").text
        # driver.find_element_by_class_name('next').click()
        # aaa = driver.find_element_by_class_name('ques-list list-box').text
        # print(aaa)

    def get_topic_count(self,url):
        self.driver.get(url)
        topic_count = self.driver.find_elements_by_xpath('//td[@id="TotalQuesN"]/em')[0].text
        return topic_count



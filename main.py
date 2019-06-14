# coding=utf-8
import sys
import time
from interface.ui import client
from interface.ui import DB_dialog, WebView
from interface.webview import MainWindow

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5.QtCore import QThread, pyqtSignal, QByteArray
from PyQt5.QtGui import QPixmap, QImage
# from lxml import etree
from interface import utils
from interface.mysql_model import *
# from interface.web_driver import WebDriver

# 自动化引入
# ###超时相关
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
# ###设备相关
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
# 必须添加 否则打包会遗漏
import pymysql
# 忽略警告
import warnings

warnings.filterwarnings("ignore")

jyeoo_qqlogin_url = 'http://www.jyeoo.com/api/qqlogin?u=http://www.jyeoo.com/'

# 详情页面
DETAIL_PAGE = 'http://www.jyeoo.com/{subject}/ques/detail/{fieldset}'


class MyDBDialog(QDialog, DB_dialog.Ui_Dialog):
    def __init__(self):
        super(MyDBDialog, self).__init__()
        self.setupUi(self)
        self.buttonBox.clicked.connect(self.set_db_info)
        self.db_dict = utils.get_db_config()
        self.init_db_info()

    def init_db_info(self):
        self.lineEdit_ip.setText(self.db_dict.get('db_ip'))
        self.lineEdit_account.setText(self.db_dict.get('db_account'))
        self.lineEdit_dbname.setText(self.db_dict.get('db_name'))
        self.lineEdit_port.setText(self.db_dict.get('db_port'))
        self.lineEdit_password.setText(self.db_dict.get('db_password'))

    def set_db_info(self):
        db_dict = dict()
        db_dict['db_password'] = self.lineEdit_password.text()
        db_dict['db_port'] = self.lineEdit_port.text()
        db_dict['db_dbname'] = self.lineEdit_dbname.text()
        db_dict['db_account'] = self.lineEdit_account.text()
        db_dict['db_ip'] = self.lineEdit_ip.text()
        utils.set_db_config(db_dict)


class WebViewDialog(QDialog, WebView.Ui_Dialog):
    def __init__(self):
        super(WebViewDialog, self).__init__()
        self.setupUi(self)

    def set_image(self, image_png):
        self.setWindowTitle('错误图片，清晰版看当前目录下的error.png')
        self.label.setScaledContents(True)
        image = QImage.fromData(image_png)
        pixmap = QPixmap.fromImage(image)
        self.label.setPixmap(pixmap)


class Worker(QThread):
    sinOut = pyqtSignal(str)  # 自定义信号，执行run()函数时，从相关线程发射此信号
    crawler_progress = pyqtSignal(int, int)  # 爬虫进度条信号
    chapter_progress = pyqtSignal(int, int)  # 章节进度条信号

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self.type = None
        self.db_session = None
        self.working = True
        self.db_connect = None
        self.subject_code = ''
        self.chapter_id = ''
        self.is_recursive = False  # 是否递归
        self.cookies = dict()
        self.num = 0
        self.crawl_maximum = 0
        self.driver = None
        self.UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari\
        /537.36'
        self.phantomjs_path = utils.get_phantomjs_path()
        self.desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
        self.cookie_dict = {
            'name': '',
            'value': '',
            'domain': '.jyeoo.com',
            'path': '/',
            'expiry': int(time.time()) + 10000000
        }

    def __del__(self):
        self.working = False
        self.wait()
        self.driver.quit()

    def init_phantomjs_driver(self):

        # get()方法会一直等到页面被完全加载，然后才会继续程序
        headers = {'Accept': '*/*',
                   'Accept-Language': 'en-US,en;q=0.8',
                   'Cache-Control': 'max-age=0',
                   'User-Agent': self.UA,
                   'Connection': 'keep-alive',
                   }
        for key, value in headers.items():
            self.desired_capabilities['phantomjs.page.customHeaders.{}'.format(key)] = value

        self.desired_capabilities[
            'phantomjs.page.customHeaders.User-Agent'] = self.UA
        self.driver = webdriver.PhantomJS(executable_path=self.phantomjs_path,
                                          desired_capabilities=self.desired_capabilities)
        # 设置超时时间30秒
        self.driver.set_page_load_timeout(30)

    def add_cookie(self):
        for k, v in self.cookies.items():
            self.cookie_dict['name'] = k
            self.cookie_dict['value'] = v
            self.driver.add_cookie(self.cookie_dict)

    def run(self):

        if not self.driver:
            self.init_phantomjs_driver()

        # 发出信号
        self.sinOut.emit("无头浏览器启动完成")
        # 添加cookie
        self.add_cookie()
        if self.type:
            eval('self.{func}()'.format(func=self.type))

    def library_chapter(self):
        """
        章节爬取动作
        :return:
        """
        self.get

    def item_bank(self):
        """
        题库爬取动作
        :return:
        """
        start_url = self.get_item_bank_init_url(self.chapter_id, self.subject_code)
        for chapters in start_url:
            for item in chapters.values():
                try:
                    self.driver.get(item.get('url'))
                    # 滚动页面
                    self.driver.execute_script('window.scrollBy(0, 1000)')
                    # 翻页入库
                    self.page_turning(item)
                except Exception as e:
                    # 出现错误！
                    self.sinOut.emit(str(e))
                    image_png = self.driver.get_screenshot_as_png()
                    self.driver.get_screenshot_as_file('./error.png')
                    wvd = WebViewDialog()
                    wvd.set_image(image_png)
                    wvd.exec_()

    def page_turning(self, args):
        """
        翻页入库
        :param args:
        :return:
        """
        # 获取总题量
        WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, '//td[@id="TotalQuesN"]/em')))
        topic_count = self.driver.find_element_by_xpath('//td[@id="TotalQuesN"]/em').text
        # 已经爬取的个数
        already_crawler_count = 0
        while True:

            # 等待翻页已加载到页面
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, "//a[@class='index cur']")))

            # 获取当前页
            cur_page = self.driver.find_element_by_xpath('//a[@class="index cur"]').text
            # 获取总页数
            total_pages = 0
            one_page = self.driver.find_element_by_xpath('//select[@class="ml10"]/option[@value="1"]').text
            if one_page:
                total_pages = one_page.split('/')[1].lstrip()
            # 下一页
            next_page = int(cur_page) + 1
            # 更新爬虫次数进度
            self.crawler_progress.emit(next_page, int(self.crawl_maximum))
            # 更新章节进度条
            self.chapter_progress.emit(already_crawler_count, int(topic_count))
            # 判断是否完成章节的爬取
            if already_crawler_count >= int(topic_count):
                self.sinOut.emit("已经爬取完章节题数： %s 【结束】" % str(already_crawler_count))
                break
            if next_page > int(total_pages):
                # 判断是否是最后一页
                # 如果下一页 大于 总页数 则跳出循环
                self.sinOut.emit(
                    "已经爬取完 {cur_page} / {total_pages} 【结束】".format(cur_page=cur_page, total_pages=total_pages))
                break

            if next_page > self.crawl_maximum:
                # 判断是否已经到达爬取次数
                self.sinOut.emit("已到爬取的请求数量 %s 【结束】" % str(next_page))
                break

            fieldset = self.driver.find_elements_by_xpath('.//fieldset')
            for item in fieldset:
                fieldset_id = item.get_attribute('id')

                if not fieldset_id or fieldset_id == '00000000-0000-0000-0000-000000000000':
                    self.sinOut.emit("错误！题目的id错误")
                    continue
                detail_page_url = DETAIL_PAGE.format(subject=self.subject_code, fieldset=fieldset_id)
                # print(detail_page_url)
                # 入库
                self.add_chapter_to_db(fieldset_id, detail_page_url, args)
                # 已经爬取数统计
                already_crawler_count += 1
                self.sinOut.emit(
                    '{cur_page} / {total_pages}页 数量：{count} ID：{id}'.format(cur_page=cur_page,
                                                                            total_pages=total_pages,
                                                                            count=already_crawler_count,
                                                                            id=fieldset_id
                                                                            ))
            gopage = 'goPage({page},this)'.format(page=next_page)
            self.driver.execute_script(gopage)
            # 滚动页面
            self.driver.execute_script('window.scrollBy(0, 2000)')

    def add_chapter_to_db(self, fieldset_id, detail_page_url, args):
        item_bank_init = dict()
        item_bank_init['fieldset_id'] = fieldset_id
        item_bank_init['detail_page_url'] = detail_page_url
        item_bank_init['ques_url'] = args.get('url')
        item_bank_init['from_code'] = self.subject_code
        item_bank_init['item_style_code'] = args.get('item_style_code')
        item_bank_init['library_id'] = args.get('library_id')
        item_bank_init['chaper_id'] = self.chapter_id
        item_bank_init['is_finish'] = 0
        self.db_connect.add(ItemBankInit(**item_bank_init))

    def get_item_bank_init_url(self, chapter_id, subject_code):
        """
        获取题库url列表用来爬取数据
        :return:
        """
        re_dict = dict()
        query = self.db_session.query(LibraryChapter).filter(LibraryChapter.id == chapter_id)
        url_str = 'http://www.jyeoo.com/{subject}/ques/search?f=0&q={pk}'
        last_data = None
        # 遍历章节
        for item in query:
            if last_data:
                is_ok_count = self.db_session.query(ItemBankInit).filter(ItemBankInit.chaper_id == last_data.id).count()
                if is_ok_count > 1:
                    last_data.is_finish = 1
                    self.db_session.commit()
            last_data = item
            temp_dict = dict()
            # 学科
            temp_dict['subject'] = subject_code
            # 教材ID
            temp_dict['library_id'] = item.library_id
            # 章节ID
            temp_dict['chaper_id'] = item.id
            # 章节直连
            temp_dict['pk'] = item.pk
            # 题型
            temp_dict['item_style_code'] = ''
            # 题类
            temp_dict['field_code'] = ''
            temp_dict['url'] = url_str.format(**temp_dict)
            re_dict[item.id] = temp_dict
            yield re_dict

    def get_chapter_url(self):
        # from jyeoo.mysql_model import DBSession, LibraryEntry
        # re_list = list()
        re_dict = dict()
        print(self.subject_code)
        # query = session.session.query(LibraryEntry).all()
        # for item in query:
        # url_str = 'http://www.jyeoo.com/{subject}/ques/search?f=0&q={id}'
        # if int(item.level_code) > 1:
        #     re_dict[item.id] = url_str.format(subject=item.subject_code + item.level_code, id=item.id)
        # else:
        #     re_dict[item.id] = url_str.format(subject=item.subject_code, id=item.id)
        return re_dict


class MyWindow(QMainWindow, client.Ui_MainWindow):
    windowList = []

    def __init__(self):
        super(MyWindow, self).__init__()
        self.refresh_list = ['refresh_level',
                             'refresh_grade',
                             'refresh_subject',
                             'refresh_teaching',
                             'refresh_chapter',
                             ]
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.db_connect = self.init_db_connect()
        # 按钮初始化
        self.btn_init()
        # self.combobox_init()
        self.browser = MainWindow()
        self.actionDB.triggered.connect(self.set_db_connect)  # 触发事件动作为"关闭窗口"

        # 线程信号槽
        self.thread = Worker()
        self.thread.db_session = self.db_connect.session
        self.thread.sinOut.connect(self.crawler_signal)
        self.thread.crawler_progress.connect(self.crawler_progress)
        self.thread.chapter_progress.connect(self.chapter_progress)

    @staticmethod
    def init_db_connect():
        db_dict = utils.get_db_config()

        db_connect = DBSession(account=db_dict['db_account'], password=db_dict['db_password'],
                               ip=db_dict['db_ip'], port=db_dict['db_port'], dbname=db_dict['db_dbname'])
        return db_connect

    def get_cookie(self):
        account = utils.get_config('account')
        self.label_account_content.setText(account.get('current_account'))

    def btn_init(self):

        # 账号信息相关
        self.pushButton_getAccount.clicked.connect(self.get_cookie)
        self.pushButton_change.clicked.connect(self.change_account)
        self.pushButton_logout.clicked.connect(self.logout)
        # 操作：题库相关
        self.pushButton_start.clicked.connect(self.start)
        self.comboBox_level.activated.connect(
            lambda: self.combobox_init(['refresh_grade', 'refresh_subject', 'refresh_teaching', 'refresh_chapter']))
        self.comboBox_grade.activated.connect(
            lambda: self.combobox_init(['refresh_subject', 'refresh_teaching', 'refresh_chapter']))
        self.comboBox_subject.activated.connect(lambda: self.combobox_init(['refresh_teaching', 'refresh_chapter']))
        self.comboBox_teaching.activated.connect(lambda: self.combobox_init(['refresh_chapter']))
        self.pushButton_loaddata.clicked.connect(lambda: self.combobox_init(self.refresh_list))
        self.pushButton_start_chapter.clicked.connect(self.start_chapter)

    def combobox_init(self, refresh_list):
        exec_str = 'self.{func}()'
        for item in refresh_list:
            eval(exec_str.format(func=item))
        self.statusbar.showMessage("加载数据完成")

    def refresh_level(self):
        """
        学级
        :return:
        """
        self.comboBox_level.clear()
        levels = self.db_connect.session.query(ItemStyle.level_name, ItemStyle.level_code).group_by(
            ItemStyle.level_name)
        for item in levels:
            self.comboBox_level.addItem(item[0], item[1])

    def refresh_chapter(self):
        """
        章节
        :return:
        """
        self.comboBox_chapter.clear()
        library_id = self.comboBox_teaching.currentData()
        chapters = self.db_connect.session.query(LibraryChapter.name, LibraryChapter.id).filter(
            LibraryChapter.library_id == library_id)
        for item in chapters:
            self.comboBox_chapter.addItem(item[0], item[1])

    def refresh_grade(self):
        """
        年级
        :return:
        """
        self.comboBox_grade.clear()
        level_code = self.comboBox_level.currentData()
        grade_query = self.db_connect.session.query(LevelGradeRef.grade_name,
                                                    LevelGradeRef.grade_code).filter(
            LevelGradeRef.level_code == level_code)
        for item in grade_query:
            self.comboBox_grade.addItem(item[0], item[1])

    def refresh_subject(self):
        """
        刷新学科
        :return:
        """
        self.comboBox_subject.clear()
        level_data = self.comboBox_level.currentData()
        subject_query = self.db_connect.session.query(LevelSubjectsRef.subject_name,
                                                      LevelSubjectsRef.subject_code).filter(
            LevelSubjectsRef.level_code == level_data)
        for item in subject_query:
            _level = '' if int(level_data) == 1 else level_data
            self.comboBox_subject.addItem(item[0], item[1] + _level)

    def refresh_teaching(self):
        """
        刷新教材
        :return:
        """
        self.comboBox_teaching.clear()
        grade = self.comboBox_grade.currentData()
        subject = self.comboBox_subject.currentData()
        if subject[-1].isdigit():
            subject = subject[:-1]
        teaching_query = self.db_connect.session.query(LibraryEntry.style_name, LibraryEntry.id).filter(
            LibraryEntry.grade_code == grade, LibraryEntry.subject_code == subject)
        for item in teaching_query:
            self.comboBox_teaching.addItem(item[0], item[1])

    def logout(self):
        self.browser.logout()
        self.browser.clear_all_data()

    @staticmethod
    def set_db_connect():
        # print('show db dialog')
        MyDBDialog().exec_()

    def change_account(self):
        self.browser.show()

    def init_work_thread_data(self):
        self.thread.chapter_id = self.comboBox_chapter.currentData()
        self.thread.cookies = utils.get_config('cookies')
        self.thread.subject_code = self.comboBox_subject.currentData()
        self.thread.level_code = self.comboBox_level.currentData()
        self.thread.crawl_maximum = int(self.spinBox_crawlMaximum.text())
        self.thread.db_connect = self.db_connect

    def start(self):
        self.statusbar.showMessage('正在启动无头浏览器')
        self.init_work_thread_data()
        self.thread.type = 'item_bank'
        self.thread.start()

    def start_chapter(self):
        self.statusbar.showMessage('正在启动无头浏览器')
        self.init_work_thread_data()
        self.thread.type = 'library_chapter'
        self.thread.start()

    def crawler_signal(self, message_str):
        self.statusbar.showMessage(message_str)

    def crawler_progress(self, current, maximum):
        self.progressBar_crawler.setMaximum(maximum)
        if current > maximum:
            self.progressBar_crawler.setValue(maximum)
        else:
            self.progressBar_crawler.setValue(current)

    def chapter_progress(self, current, maximum):
        self.progressBar_chapter.setMaximum(maximum)
        if current > maximum:
            self.progressBar_chapter.setValue(maximum)
        else:
            self.progressBar_chapter.setValue(current)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())

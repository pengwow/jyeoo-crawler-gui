# coding=utf-8
import sys
import time
from lxml import etree
from ui import client
from ui import DB_dialog, WebView
from webview import MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import utils
from mysql_model import *
from multiprocessing import Lock
# 自动化引入
# ###超时相关
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait, TimeoutException
# ###设备相关
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
# 忽略警告
import warnings

# 忽略警告
warnings.filterwarnings("ignore")
jyeoo_qqlogin_url = 'http://www.jyeoo.com/api/qqlogin?u=http://www.jyeoo.com/'
# 详情页面
DETAIL_PAGE = 'http://www.jyeoo.com/{subject}/ques/detail/{fieldset}'
# 锁
mutex = Lock()


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
        pixmap = QPixmap()
        pixmap = pixmap.fromImage(QImage=image, flags=None)
        self.label.setPixmap(pixmap)


class Worker(QThread):
    sinOut = pyqtSignal(str)  # 自定义信号，执行run()函数时，从相关线程发射此信号
    crawler_progress = pyqtSignal(int, int)  # 爬虫进度条信号
    chapter_progress = pyqtSignal(int, int)  # 章节进度条信号
    crawler_chapter_progress = pyqtSignal(int, int)  # 爬取章节进度条信号
    message_box = pyqtSignal(str, str)  # 弹窗提示

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self.type = None
        self.db_session = None
        self.working = True
        self.db_connect = None
        # 是否断点续爬
        self.item_bank_continue = False
        self.subject_code = ''
        self.subject_name = ''
        self.teaching = ''
        self.teaching_name = ''
        self.level_code = ''
        self.level_name = ''
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
            # 动态执行方法
            eval('self.{func}()'.format(func=self.type))

    def item_bank_details(self):
        """
        详情页爬取方法
        :return:
        """
        start_urls = self.get_details_url()
        for url in start_urls:
            self.driver.get(url)
            self.driver.find_element_by_xpath('.//div[@class="pt1"]')
            
        return

    def library_chapter(self):
        """
        章节爬取动作
        :return:
        """
        start_url = self.get_chapter_url()
        self.driver.get(start_url)
        try:
            WebDriverWait(self.driver, 30).until(
                ec.visibility_of_element_located((By.XPATH, '//div[@class="tree-head"]/span[@id="spanEdition"]')))
        except TimeoutException as e:
            self.sinOut.emit('超时！！！ %s' % str(e))
            return
        teaching = self.driver.find_element_by_xpath('//div[@class="tree-head"]/span[@id="spanEdition"]').text
        level_name = self.driver.find_element_by_xpath('//div[@class="tree-head"]/span[@id="spanGrade"]').text
        teaching = teaching.replace(':', '').replace('：', '')
        self.sinOut.emit('进行爬取章节！')
        if self.teaching_name != teaching or self.level_name != level_name:
            self.message_box.emit('警告', "没有数据！")
            return
        # WebDriverWait(self.driver, 30).until(
        #     ec.visibility_of_element_located((By.XPATH, '//ul[@id="JYE_POINT_TREE_HOLDER"]//li')))
        et = etree.HTML(self.driver.page_source)
        library_id = self.teaching
        # sub_obj = self.driver.find_elements_by_xpath('//ul[@id="JYE_POINT_TREE_HOLDER"]//li')
        sub_obj = et.xpath('//ul[@id="JYE_POINT_TREE_HOLDER"]//li')
        chapters_list = list()

        total = len(sub_obj)
        current_count = 0
        for item in sub_obj:
            lc_item = dict()
            lc_item['id'] = str(uuid.uuid1())
            pk = item.attrib.get('pk')

            lc_item['pk'] = pk
            temp_list = pk.split('~')

            lc_item['name'] = item.attrib.get('nm')

            if temp_list[-1]:
                lc_item['library_id'] = library_id
                parent_id = temp_list[temp_list.index(temp_list[-1]) - 1]
                lc_item['parent_id'] = ''
                if parent_id != lc_item['library_id']:
                    lc_item['parent_id'] = parent_id
            else:
                lc_item['library_id'] = library_id
                parent_id = temp_list[temp_list.index(temp_list[-2]) - 1]
                lc_item['parent_id'] = ''
                if parent_id != lc_item['library_id']:
                    lc_item['parent_id'] = parent_id
            chapters_list.append(lc_item)
            current_count += 1
            self.crawler_chapter_progress.emit(current_count, total)
        if chapters_list:
            chapters = self.db_connect.session.query(LibraryChapter.name, LibraryChapter.id).filter(
                LibraryChapter.library_id == library_id)
            mutex.acquire()
            chapters.delete()
            self.db_connect.session.commit()
            mutex.release()
            for item in chapters_list:
                mutex.acquire()
                self.db_session.add(LibraryChapter(**item))
                mutex.release()
        self.sinOut.emit('章节爬取完成，重新加载查看')

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
            ec.visibility_of_element_located((By.XPATH, '//td[@id="TotalQuesN"]/em')))
        topic_count = self.driver.find_element_by_xpath('//td[@id="TotalQuesN"]/em').text
        # 已经爬取的个数
        already_crawler_count = 0
        while True:

            # 等待翻页已加载到页面
            WebDriverWait(self.driver, 30).until(
                ec.visibility_of_element_located((By.XPATH, "//a[@class='index cur']")))

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
        mutex.acquire()
        self.db_connect.add(ItemBankInit(**item_bank_init))
        mutex.release()

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
                    mutex.acquire()
                    self.db_session.commit()
                    mutex.release()
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
        url_str = 'http://www.jyeoo.com/{subject}/ques/search?f=0&q={id}'
        re_url = url_str.format(subject=self.subject_code, id=self.teaching)
        return re_url

    def get_details_url(self):
        """
        获取详情页url
        :return: list
        """
        re_list = list()
        item_bank_init = self.db_session.query(ItemBankInit).filter(ItemBankInit.chaper_id == self.chapter_id)
        for item in item_bank_init:
            re_list.append(item.detail_page_url)
        return re_list


class MyWindow(QMainWindow, client.Ui_MainWindow):
    windowList = []

    def __init__(self):
        super(MyWindow, self).__init__()
        self.refresh_list = ['refresh_level',
                             'refresh_grade',
                             'refresh_subject',
                             'refresh_teaching',
                             'refresh_chapter',
                             'refresh_bank_total',
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
        self.thread.crawler_chapter_progress.connect(self.crawler_chapter_progress)
        self.thread.message_box.connect(self.message_box)

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
            lambda: self.combobox_init(
                ['refresh_grade', 'refresh_subject', 'refresh_teaching', 'refresh_chapter', 'refresh_bank_total']))
        self.comboBox_grade.activated.connect(
            lambda: self.combobox_init(
                ['refresh_subject', 'refresh_teaching', 'refresh_chapter', 'refresh_bank_total']))
        self.comboBox_subject.activated.connect(
            lambda: self.combobox_init(['refresh_teaching', 'refresh_chapter', 'refresh_bank_total']))
        self.comboBox_teaching.activated.connect(lambda: self.combobox_init(['refresh_chapter', 'refresh_bank_total']))
        self.comboBox_chapter.activated.connect(lambda: self.combobox_init(['refresh_bank_total']))
        self.pushButton_loaddata.clicked.connect(lambda: self.combobox_init(self.refresh_list))
        # 章节开始
        self.pushButton_start_chapter.clicked.connect(self.start_chapter)
        # 详情页开始
        self.pushButton_start_details.clicked.connect(self.start_details)

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
        mutex.acquire()
        levels = self.db_connect.session.query(ItemStyle.level_name, ItemStyle.level_code).group_by(
            ItemStyle.level_name)
        mutex.release()
        for item in levels:
            self.comboBox_level.addItem(item[0], item[1])

    def refresh_chapter(self):
        """
        章节
        :return:
        """
        self.comboBox_chapter.clear()
        library_id = self.comboBox_teaching.currentData()
        mutex.acquire()
        chapters = self.db_connect.session.query(LibraryChapter.name, LibraryChapter.id).filter(
            LibraryChapter.library_id == library_id)
        mutex.release()
        for item in chapters:
            self.comboBox_chapter.addItem(item[0], item[1])

    def refresh_grade(self):
        """
        年级
        :return:
        """
        self.comboBox_grade.clear()
        level_code = self.comboBox_level.currentData()
        mutex.acquire()
        grade_query = self.db_connect.session.query(LevelGradeRef.grade_name,
                                                    LevelGradeRef.grade_code).filter(
            LevelGradeRef.level_code == level_code)
        mutex.release()
        for item in grade_query:
            self.comboBox_grade.addItem(item[0], item[1])

    def refresh_subject(self):
        """
        刷新学科
        :return:
        """
        self.comboBox_subject.clear()
        level_data = self.comboBox_level.currentData()
        mutex.acquire()
        subject_query = self.db_connect.session.query(LevelSubjectsRef.subject_name,
                                                      LevelSubjectsRef.subject_code).filter(
            LevelSubjectsRef.level_code == level_data)
        mutex.release()
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
        mutex.acquire()
        teaching_query = self.db_connect.session.query(LibraryEntry.style_name, LibraryEntry.id).filter(
            LibraryEntry.grade_code == grade, LibraryEntry.subject_code == subject)
        mutex.release()
        for item in teaching_query:
            self.comboBox_teaching.addItem(item[0], item[1])

    def refresh_bank_total(self):
        """
        刷新题库量
        :return:
        """
        chapter = self.comboBox_chapter.currentData()
        bank_count = 0
        if chapter:
            bank_count = self.db_connect.session.query(ItemBankInit).filter(ItemBankInit.chaper_id == chapter).count()
        self.lcdNumber_chapter.display(int(bank_count))

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
        self.thread.subject_name = self.comboBox_subject.currentText()
        self.thread.level_code = self.comboBox_level.currentData()
        self.thread.level_name = self.comboBox_grade.currentText()
        self.thread.teaching = self.comboBox_teaching.currentData()
        self.thread.teaching_name = self.comboBox_teaching.currentText()
        self.thread.crawl_maximum = int(self.spinBox_crawlMaximum.text())
        self.thread.db_connect = self.db_connect

    def start(self):
        self.statusbar.showMessage('正在启动无头浏览器')
        self.init_work_thread_data()
        self.thread.type = 'item_bank'
        if self.radioButton_continue.isChecked():
            self.thread.item_bank_continue = True
        self.thread.start()

    def start_details(self):
        self.statusbar.showMessage('正在启动无头浏览器')
        self.init_work_thread_data()
        self.thread.type = 'item_bank_details'
        self.thread.start()

    def start_chapter(self):
        self.statusbar.showMessage('正在启动无头浏览器')
        message_box = QMessageBox()
        result = message_box.warning(self, "警告", "警告！会删除章节数据，已爬取的题库将会影响！", QMessageBox.Ok | QMessageBox.Cancel)
        if result == QMessageBox.Cancel:
            return
        self.init_work_thread_data()
        self.thread.type = 'library_chapter'
        self.thread.start()

    def crawler_signal(self, message_str):
        self.statusbar.showMessage(message_str)

    def crawler_progress(self, current, maximum):
        self.progressBar_crawler.setMaximum(maximum)
        if current >= maximum:
            self.progressBar_crawler.setValue(maximum)
        else:
            self.progressBar_crawler.setValue(current)

    def chapter_progress(self, current, maximum):
        self.progressBar_chapter.setMaximum(maximum)
        if current >= maximum:
            self.progressBar_chapter.setValue(maximum)
        else:
            self.progressBar_chapter.setValue(current)

    def crawler_chapter_progress(self, current, maximum):
        self.progressBar_crawler_chapter.setMaximum(maximum)
        if current >= maximum:
            self.progressBar_crawler_chapter.setValue(maximum)
            self.combobox_init(['refresh_chapter'])
        else:
            self.progressBar_crawler_chapter.setValue(current)

    def message_box(self, title, content):
        message_box = QMessageBox()
        message_box.warning(self, title, content, QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())

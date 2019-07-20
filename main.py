# coding=utf-8
import sys

from ui import client
from worker import Worker
from dialog import MyDBDialog
from webview import MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTreeWidgetItem, QTableWidgetItem
from PyQt5.QtCore import Qt
import utils
from utils import mutex
from mysql_model import *

# 忽略警告
import warnings

# 忽略警告
warnings.filterwarnings("ignore")


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
                             'refresh_from'
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
        # self.thread.chapter_progress.connect(self.chapter_progress)
        self.thread.crawler_chapter_progress.connect(self.crawler_chapter_progress)
        self.thread.message_box.connect(self.message_box)
        self.thread.execution_method.connect(self.execution_method)
        self.thread.details_progress.connect(self.details_progress)

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

        self.pushButton_loaddata.clicked.connect(lambda: self.combobox_init(self.refresh_list))
        # 章节点击触发
        # 原章节切换触发
        # self.comboBox_chapter.activated.connect(lambda: self.combobox_init(['refresh_bank_total']))
        self.treeWidget_chapter.clicked.connect(lambda: self.combobox_init(['refresh_bank_total']))
        self.treeWidget_chapter.clicked.connect(self.tree_chapter)
        # 章节开始
        self.pushButton_start_chapter.clicked.connect(self.start_chapter)
        # 详情页开始
        self.pushButton_start_details.clicked.connect(self.start_details)
        # tab切换触发
        self.tabWidget.currentChanged.connect(self.tab_change)

    def combobox_init(self, refresh_list):
        exec_str = 'self.{func}()'
        for item in refresh_list:
            eval(exec_str.format(func=item))
        self.statusbar.showMessage("加载数据完成")

    def refresh_level(self):
        """
        刷新学级
        :return:
        """
        self.comboBox_level.clear()
        mutex.acquire()
        levels = self.db_connect.session.query(ItemStyle.level_name, ItemStyle.level_code).group_by(
            ItemStyle.level_name)
        mutex.release()
        for item in levels:
            self.comboBox_level.addItem(item[0], item[1])

    def refresh_from(self):
        """
        刷新来源
        :return:
        """
        self.comboBox_from.clear()
        mutex.acquire()
        level_code = self.comboBox_level.currentData()
        levels = self.db_connect.session.query(ItemFrom.from_name, ItemFrom.from_code).filter(
            ItemFrom.level_code == level_code)
        mutex.release()
        # 默认为全部
        self.comboBox_from.addItem('全部', '')
        for item in levels:
            self.comboBox_from.addItem(item[0], item[1])

    def refresh_chapter(self):
        """
        章节
        :return:
        """
        self.comboBox_chapter.clear()
        self.treeWidget_chapter.clear()
        self.treeWidget_chapter.setColumnCount(1)
        library_id = self.comboBox_teaching.currentData()
        mutex.acquire()
        chapters = self.db_connect.session.query(LibraryChapter.name, LibraryChapter.id,
                                                 LibraryChapter.parent_id, LibraryChapter.pk).filter(
            LibraryChapter.library_id == library_id)

        tree_dict = dict()
        for item in chapters:
            self.comboBox_chapter.addItem(item[0], item[1])
            if '' == item[2]:
                tree_item = QTreeWidgetItem(self.treeWidget_chapter)
                tree_item.setText(0, item[0])
                tree_item.setText(1, item[1])
                tree_item.setText(2, item[3])
                tree_dict[item[1]] = {'item': tree_item, 'parent_id': ''}
            else:
                tree_item = QTreeWidgetItem()
                tree_item.setText(0, item[0])
                tree_item.setText(1, item[1])
                tree_item.setText(2, item[3])
                tree_dict[item[1]] = {'item': tree_item, 'parent_id': item[2]}
        mutex.release()
        for key, value in tree_dict.items():
            parent_id = value.get('parent_id')
            if parent_id:
                if not tree_dict.get(parent_id):
                    result = self.message_box_choice('章节获取错误', '请重新获取此章节')
                    if result == QMessageBox.Ok:
                        # 重新爬取章节
                        self.start_chapter()
                    break
                tree_dict[parent_id]['item'].addChild(value.get('item'))

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
        # 0=name 1=chapter_id 2=pk
        chapter_current_item = self.treeWidget_chapter.currentItem()
        if not chapter_current_item:
            return
        chapter = chapter_current_item.text(1)
        # chapter = self.comboBox_chapter.currentData()
        bank_count = 0
        if chapter:
            bank_count = self.db_connect.session.query(ItemBankInit).filter(ItemBankInit.chaper_id == chapter).count()
        self.lcdNumber_chapter.display(int(bank_count))

    def tree_chapter(self):
        """
        章节树点击操作
        :return:
        """
        current_item = self.treeWidget_chapter.currentItem()
        name = current_item.text(0)
        chapter_id = current_item.text(1)
        # pk = current_item.text(2)
        self.comboBox_chapter.clear()
        self.comboBox_chapter.addItem(name, chapter_id)

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
        self.thread.from_code = self.comboBox_from.currentData()

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
        self.thread.crawl_maximum = int(self.spinBox_details.text())
        self.thread.type = 'item_bank_details'
        self.thread.start()

    def start_chapter(self):
        self.statusbar.showMessage('正在启动无头浏览器')
        message_box = QMessageBox()
        result = message_box.warning(self, "警告", "警告！将会重建章节数据。", QMessageBox.Ok | QMessageBox.Cancel)
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

    def details_progress(self, current, maximum):
        self.progressBar_details.setMaximum(maximum)
        if current >= maximum:
            self.progressBar_details.setValue(maximum)
        else:
            self.progressBar_details.setValue(current)

    # def chapter_progress(self, current, maximum):
    #     self.progressBar_chapter.setMaximum(maximum)
    #     if current >= maximum:
    #         self.progressBar_chapter.setValue(maximum)
    #     else:
    #         self.progressBar_chapter.setValue(current)

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

    def message_box_choice(self, title, content):
        message_box = QMessageBox()
        result = message_box.warning(self, title, content, QMessageBox.Ok | QMessageBox.Cancel)
        return result

    def execution_method(self, method):
        # self.statusbar.showMessage('执行方法：%s' % method)
        eval(method)

    def tab_change(self):
        current_index = self.tabWidget.currentIndex()
        # 清空数据详情窗体内容
        self.tableWidget_dataInfo.clear()
        # 章节ID
        chaper_id = self.comboBox_chapter.currentData()
        if 0 == current_index and chaper_id:
            # 切换到题库
            self.tableWidget_dataInfo.setColumnCount(2)  # 控制表格有几列

            self.tableWidget_dataInfo.setColumnWidth(1, 1000)  # 设置j列的宽度
            self.tableWidget_dataInfo.verticalHeader().setVisible(False)  # 隐藏垂直表头
            self.tableWidget_dataInfo.horizontalHeader().setVisible(False)  # 隐藏水平表头
            itembank_init_query = self.db_connect.session.query(ItemBankInit.id, ItemBankInit.detail_page_url).filter(
                ItemBankInit.chaper_id == chaper_id)
            r_pos = 0
            self.tableWidget_dataInfo.setRowCount(itembank_init_query.count())  # 控制表格有几行
            for item in itembank_init_query:
                _id = QTableWidgetItem(str(item.id))
                _detail_page_url = QTableWidgetItem(item.detail_page_url)
                _id.setFlags(Qt.ItemIsSelectable)
                _detail_page_url.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable)
                self.tableWidget_dataInfo.setItem(r_pos, 0, _id)
                self.tableWidget_dataInfo.setItem(r_pos, 1, _detail_page_url)
                r_pos += 1

            # self.tableWidget_dataInfo.setRowHeight(i, 50)  # 设置i行的高度
        elif 1 == current_index:
            # 切换到详情页
            pass
        elif 2 == current_index:
            # 切换到章节
            pass

    def __del__(self):
        self.db_connect.session.close_all()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())

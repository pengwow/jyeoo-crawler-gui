import sys
from interface.utils import set_cookie_config, set_config
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QMainWindow
from lxml import etree

jyeoo_qqlogin_url = 'http://www.jyeoo.com/api/qqlogin?u=http://www.jyeoo.com/'
jyeoo_logoff_url = 'http://www.jyeoo.com/account/logoff'


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(1000, 600)

        # self.back_btn = QPushButton(self)
        # self.forward_btn = QPushButton(self)
        self.refresh_btn = QPushButton(self)
        self.zoom_in_btn = QPushButton(self)
        self.zoom_out_btn = QPushButton(self)
        self.url_le = QLineEdit(self)

        self.browser = WebEngineView()  # QWebEngineView()

        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()

        self.layout_init()
        self.btn_init()
        self.le_init()
        self.browser_init()

    def layout_init(self):
        self.h_layout.setSpacing(0)
        # self.h_layout.addWidget(self.back_btn)
        # self.h_layout.addWidget(self.forward_btn)
        self.h_layout.addWidget(self.refresh_btn)
        self.h_layout.addStretch(2)
        self.h_layout.addWidget(self.url_le)
        self.h_layout.addStretch(2)
        self.h_layout.addWidget(self.zoom_in_btn)
        self.h_layout.addWidget(self.zoom_out_btn)

        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(self.browser)

        self.setLayout(self.v_layout)

    def browser_init(self):
        self.browser.load(QUrl(jyeoo_qqlogin_url))
        self.browser.urlChanged.connect(lambda: self.url_le.setText(self.browser.url().toDisplayString()))

    def btn_init(self):
        # self.back_btn.setIcon(QIcon('images/back.png'))
        # self.forward_btn.setIcon(QIcon('images/forward.png'))
        self.refresh_btn.setIcon(QIcon('images/refresh.png'))
        self.zoom_in_btn.setIcon(QIcon('images/zoom_in.png'))
        self.zoom_out_btn.setIcon(QIcon('images/zoom_out.png'))

        # self.back_btn.clicked.connect(self.get_cookie)
        # self.forward_btn.clicked.connect(self.browser.forward)
        self.refresh_btn.clicked.connect(self.browser.reload)
        self.zoom_in_btn.clicked.connect(self.zoom_in_func)
        self.zoom_out_btn.clicked.connect(self.zoom_out_func)

    def get_cookie(self):
        cookie = self.browser.get_cookie()
        # print('获取到cookie: ', cookie)
        return cookie

    def le_init(self):
        self.url_le.setFixedWidth(400)
        self.url_le.setPlaceholderText('Search or enter website name')

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Return or QKeyEvent.key() == Qt.Key_Enter:
            if self.url_le.hasFocus():
                if self.url_le.text().startswith('https://') or self.url_le.text().startswith('http://'):
                    self.browser.load(QUrl(self.url_le.text()))
                else:
                    self.browser.load(QUrl('http://' + self.url_le.text()))

    def zoom_in_func(self):
        self.browser.setZoomFactor(self.browser.zoomFactor() + 0.1)

    def zoom_out_func(self):
        self.browser.setZoomFactor(self.browser.zoomFactor() - 0.1)

    # ###### 重写关闭事件，回到第一界面
    windowList = []

    def closeEvent(self, event):
        cookies = self.get_cookie()

        set_cookie_config({
            'jyean': cookies.get('jyean'),
            'jy': cookies.get('jy'),
        })
        self.browser.page().toHtml(self.get_account)
        # self.get_cookie()
        # set_cookie_config()
        # from interface.main import client
        # the_window = client.Ui_MainWindow().setupUi(self)
        # self.windowList.append(the_window)  ##注：没有这句，是不打开另一个主界面的！
        # #the_window.show()
        # event.accept()

    @staticmethod
    def get_account(html):
        # print(html)
        element = etree.HTML(html)
        account_list = element.xpath('//div[@class="user"]/span/text()')
        if len(account_list) > 0:
            # print(account_list[0])
            set_config('account', {'current_account': account_list[0]})

    def logout(self):
        self.browser.load(QUrl(jyeoo_logoff_url))

    def clear_all_data(self):
        self.browser.page().profile().clearHttpCache()
        self.page().profile().cookieStore().deleteAllCookies()


class WebEngineView(QWebEngineView):

    def __init__(self, *args, **kwargs):
        super(WebEngineView, self).__init__(*args, **kwargs)
        self.page().profile().clearHttpCache()
        self.page().profile().cookieStore().deleteAllCookies()
        # 绑定cookie被添加的信号槽
        QWebEngineProfile.defaultProfile().cookieStore().cookieAdded.connect(self.onCookieAdd)
        self.cookies = {}  # 存放cookie字典
        self.windowList = []

    def onCookieAdd(self, cookie):  # 处理cookie添加的事件
        # self.cookies = {}
        name = cookie.name().data().decode('utf-8')  # 先获取cookie的名字，再把编码处理一下
        value = cookie.value().data().decode('utf-8')  # 先获取cookie值，再把编码处理一下
        self.cookies[name] = value

    # 获取cookie
    def get_cookie(self):
        cookie_dict = dict()
        for key, value in self.cookies.items():  # 遍历字典
            cookie_dict[key] = value
        return cookie_dict  # 返回拼接好的字符串
        # cookie_str = ''
        # for key, value in self.cookies.items():  # 遍历字典
        #     cookie_str += (key + '=' + value + ';')  # 将键值对拿出来拼接一下
        # return cookie_str  # 返回拼接好的字符串


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

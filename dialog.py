# coding=utf-8
from ui import DB_dialog, WebView
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap, QImage, QIcon
import utils


class MyDBDialog(QDialog, DB_dialog.Ui_Dialog):
    def __init__(self):
        super(MyDBDialog, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('./images/db.png'))
        self.buttonBox.clicked.connect(self.set_db_info)
        self.db_dict = utils.get_db_config()
        self.init_db_info()

    def init_db_info(self):
        self.lineEdit_ip.setText(self.db_dict.get('db_ip'))
        self.lineEdit_account.setText(self.db_dict.get('db_account'))
        self.lineEdit_dbname.setText(self.db_dict.get('db_name'))
        self.lineEdit_port.setText(self.db_dict.get('db_port'))
        db_password = utils.HashManager().back_aes_ecb(self.db_dict.get('db_password'))
        self.lineEdit_password.setText(db_password)

    def set_db_info(self):
        db_dict = dict()
        db_password = utils.HashManager().get_aes_ecb(self.lineEdit_password.text())
        db_dict['db_password'] = db_password
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

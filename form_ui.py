# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from page1_clipboard import Ui_Dialog  # 导入 page1_clipboard 的 UI 类
from page2_device import Ui_DeviceDialog  # 导入设备页面的 UI 类
from page3_login import Ui_LoginDialog  # 导入登录页面的 UI 类


class Ui_app_ui(object):
    def setupUi(self, app_ui):
        app_ui.setObjectName("app_ui")
        app_ui.resize(1000, 700)
        self.label = QtWidgets.QLabel(app_ui)
        self.label.setGeometry(QtCore.QRect(290, 20, 141, 21))
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(app_ui)
        self.pushButton.setGeometry(QtCore.QRect(40, 60, 71, 41))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(app_ui)
        self.pushButton_2.setGeometry(QtCore.QRect(40, 160, 71, 41))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(app_ui)
        self.pushButton_3.setGeometry(QtCore.QRect(40, 270, 71, 41))
        self.pushButton_3.setObjectName("pushButton_3")
        self.stackedWidget = QtWidgets.QStackedWidget(app_ui)
        self.stackedWidget.setGeometry(QtCore.QRect(150, 60, 800, 600))
        self.stackedWidget.setObjectName("stackedWidget")

        # 创建初始空白页面
        self.blank_page = QtWidgets.QWidget()
        self.blank_page.setObjectName("blank_page")
        self.stackedWidget.addWidget(self.blank_page)

        # 创建并初始化所有子页面
        self.init_pages()

        self.retranslateUi(app_ui)
        # 设置初始显示为空白页面
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(app_ui)

        # 绑定按钮点击事件
        self.pushButton.clicked.connect(self.show_page_1)
        self.pushButton_2.clicked.connect(self.show_page_2)
        self.pushButton_3.clicked.connect(self.show_page_3)

    def init_pages(self):
        """初始化所有子页面"""
        # 页面1 (剪切板页面)
        self.page_1 = QtWidgets.QWidget()
        self.page_1.setObjectName("page_1")
        self.clipboard_ui = Ui_Dialog()
        self.clipboard_ui.setupUi(self.page_1)
        self.stackedWidget.addWidget(self.page_1)

        # 页面2 (设备页面)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.device_ui = Ui_DeviceDialog()
        self.device_ui.setupUi(self.page_2)
        self.stackedWidget.addWidget(self.page_2)

        # 页面3 (登录页面)
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setObjectName("page_3")
        self.login_ui = Ui_LoginDialog()
        self.login_ui.setupUi(self.page_3)
        self.stackedWidget.addWidget(self.page_3)

    def retranslateUi(self, app_ui):
        _translate = QtCore.QCoreApplication.translate
        app_ui.setWindowTitle(_translate("app_ui", "app_ui"))
        self.label.setText(_translate("app_ui", "BeeSyncClip"))
        self.pushButton.setText(_translate("app_ui", "剪切板"))
        self.pushButton_2.setText(_translate("app_ui", "设备"))
        self.pushButton_3.setText(_translate("app_ui", "登录"))

    def show_page_1(self):
        # 直接显示已初始化的页面1
        self.stackedWidget.setCurrentIndex(1)

    def show_page_2(self):
        # 直接显示已初始化的页面2
        self.stackedWidget.setCurrentIndex(2)

    def show_page_3(self):
        # 直接显示已初始化的页面3
        self.stackedWidget.setCurrentIndex(3)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app_ui = QtWidgets.QWidget()
    ui = Ui_app_ui()
    ui.setupUi(app_ui)
    app_ui.show()
    sys.exit(app.exec_())
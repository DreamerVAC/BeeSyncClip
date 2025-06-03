# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from page1_clipboard import Ui_Dialog, ClipboardDialog
from page2_device import DeviceDialog
from page3_login import LoginDialog  # 修改为导入LoginDialog类


class Ui_app_ui(object):
    def setupUi(self, app_ui):
        app_ui.setObjectName("app_ui")
        app_ui.resize(1000, 700)

        # 设置窗口图标和标题
        app_ui.setWindowIcon(QtGui.QIcon(':/icons/app_icon.png'))  # 如果有图标资源

        # 主布局
        self.main_layout = QtWidgets.QHBoxLayout(app_ui)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 左侧导航栏
        self.nav_frame = QtWidgets.QFrame()
        self.nav_frame.setFixedWidth(120)
        self.nav_frame.setStyleSheet("background-color: #f0f0f0;")
        self.nav_layout = QtWidgets.QVBoxLayout(self.nav_frame)
        self.nav_layout.setContentsMargins(10, 20, 10, 20)
        self.nav_layout.setSpacing(10)

        # 应用标题
        self.title_label = QtWidgets.QLabel("BeeSyncClip")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.nav_layout.addWidget(self.title_label)

        # 导航按钮
        self.btn_clipboard = QtWidgets.QPushButton("剪切板")
        self.btn_device = QtWidgets.QPushButton("设备")
        self.btn_login = QtWidgets.QPushButton("登录")

        # 设置按钮样式
        nav_btn_style = """
            QPushButton {
                padding: 10px;
                text-align: left;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """
        for btn in [self.btn_clipboard, self.btn_device, self.btn_login]:
            btn.setStyleSheet(nav_btn_style)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        # 添加按钮到导航栏
        self.nav_layout.addWidget(self.btn_clipboard)
        self.nav_layout.addWidget(self.btn_device)
        self.nav_layout.addWidget(self.btn_login)

        # 添加伸缩空间使按钮靠上
        self.nav_layout.addStretch()

        # 右侧内容区域
        self.content_frame = QtWidgets.QFrame()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        # 堆叠窗口部件
        self.stackedWidget = QtWidgets.QStackedWidget()
        self.stackedWidget.setObjectName("stackedWidget")

        # 创建初始空白页面
        self.blank_page = QtWidgets.QWidget()
        self.blank_page.setObjectName("blank_page")
        self.stackedWidget.addWidget(self.blank_page)

        # 初始化所有子页面
        self.init_pages()

        # 添加堆叠窗口到内容区域
        self.content_layout.addWidget(self.stackedWidget)

        # 将导航栏和内容区域添加到主布局
        self.main_layout.addWidget(self.nav_frame)
        self.main_layout.addWidget(self.content_frame)

        self.retranslateUi(app_ui)
        # 设置初始显示为空白页面
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(app_ui)

        # 绑定按钮点击事件
        self.btn_clipboard.clicked.connect(self.show_page_1)
        self.btn_device.clicked.connect(self.show_page_2)
        self.btn_login.clicked.connect(self.show_page_3)

    def init_pages(self):
        """初始化所有子页面"""
        # 页面1 (剪切板页面)
        self.page_1 = QtWidgets.QWidget()  # 改为普通QWidget容器
        self.page_1.setObjectName("page_1")
        self.clipboard_dialog = ClipboardDialog()  # 创建ClipboardDialog实例
        # 将ClipboardDialog添加到页面1的布局中
        layout = QtWidgets.QVBoxLayout(self.page_1)
        layout.addWidget(self.clipboard_dialog)
        self.stackedWidget.addWidget(self.page_1)

        # 页面2 (设备页面)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.device_dialog = DeviceDialog()
        layout = QtWidgets.QVBoxLayout(self.page_2)
        layout.addWidget(self.device_dialog)
        self.stackedWidget.addWidget(self.page_2)

        # 页面3 (登录页面)
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setObjectName("page_3")
        self.login_dialog = LoginDialog()
        layout = QtWidgets.QVBoxLayout(self.page_3)
        layout.addWidget(self.login_dialog)
        self.stackedWidget.addWidget(self.page_3)

    def retranslateUi(self, app_ui):
        _translate = QtCore.QCoreApplication.translate
        app_ui.setWindowTitle(_translate("app_ui", "BeeSyncClip"))
        self.title_label.setText(_translate("app_ui", "BeeSyncClip"))
        self.btn_clipboard.setText(_translate("app_ui", "剪切板"))
        self.btn_device.setText(_translate("app_ui", "设备"))
        self.btn_login.setText(_translate("app_ui", "登录"))

    def show_page_1(self):
        """显示剪切板页面"""
        self.stackedWidget.setCurrentIndex(1)
        self.update_nav_btn_style(self.btn_clipboard)

    def show_page_2(self):
        """显示设备页面"""
        self.stackedWidget.setCurrentIndex(2)
        self.update_nav_btn_style(self.btn_device)

    def show_page_3(self):
        """显示登录页面"""
        self.stackedWidget.setCurrentIndex(3)
        self.update_nav_btn_style(self.btn_login)

    def update_nav_btn_style(self, active_btn):
        """更新导航按钮样式，突出显示当前活动按钮"""
        for btn in [self.btn_clipboard, self.btn_device, self.btn_login]:
            if btn == active_btn:
                btn.setStyleSheet("""
                    QPushButton {
                        padding: 10px;
                        text-align: left;
                        border-radius: 5px;
                        background-color: #d0d0d0;
                        font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        padding: 10px;
                        text-align: left;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                    QPushButton:pressed {
                        background-color: #d0d0d0;
                    }
                """)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_app_ui()
        self.ui.setupUi(self)

        # 监听登录成功信号
        self.ui.login_dialog.accepted.connect(self.on_login_success)

    def on_login_success(self):
        """登录成功后设置用户信息"""
        login_dialog = self.ui.login_dialog
        api_url = login_dialog.api_url
        username = login_dialog.get_current_username()
        current_device_id = login_dialog.get_device_info().get('device_id')

        # 打印调试信息，确保数据正确
        print(f"[DEBUG] Login success! api_url={api_url}, username={username}")

        # 设置设备对话框的用户信息
        self.ui.device_dialog.set_user_info(api_url, username, current_device_id)

        # 设置剪贴板对话框的用户信息
        self.ui.clipboard_dialog.set_user_info(api_url, username)  # 确保这行执行了


if __name__ == "__main__":
    import sys
    import traceback



    def excepthook(exc_type, exc_value, exc_traceback):
        """全局异常处理"""
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"发生未捕获的异常:\n{error_msg}")
        QtWidgets.QMessageBox.critical(None, "错误", f"程序发生错误:\n{str(exc_value)}")
        sys.exit(1)


    sys.excepthook = excepthook

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

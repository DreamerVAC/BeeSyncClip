# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from page1_clipboard import Ui_Dialog, ClipboardDialog
from page2_device import DeviceDialog
from page3_login import LoginDialog  # 修改为导入LoginDialog类
from page5_userinfo import UserInfoDialog


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

        # 定义导航按钮样式
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

        # 在导航栏中添加用户信息按钮
        self.btn_userinfo = QtWidgets.QPushButton("用户信息")
        self.btn_userinfo.setStyleSheet(nav_btn_style)
        self.btn_userinfo.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.nav_layout.addWidget(self.btn_userinfo)
        self.btn_userinfo.hide()  # 初始隐藏
        self.btn_userinfo.clicked.connect(self.show_page_4)  # 绑定点击事件

        # 设置按钮样式
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

        # 创建初始空白页面 - 添加emoji图案
        self.blank_page = QtWidgets.QWidget()
        self.blank_page.setObjectName("blank_page")

        # 添加垂直布局
        blank_layout = QtWidgets.QVBoxLayout(self.blank_page)
        blank_layout.setContentsMargins(0, 0, 0, 0)
        blank_layout.setSpacing(20)

        # 添加居中的emoji标签
        self.emoji_label = QtWidgets.QLabel()
        self.emoji_label.setAlignment(QtCore.Qt.AlignCenter)
        self.emoji_label.setStyleSheet("""
            QLabel {
                font-size: 100px;
            }
        """)
        self.emoji_label.setText("🐝")  # 蜜蜂emoji

        # 添加欢迎文本
        self.welcome_label = QtWidgets.QLabel("欢迎使用 BeeSyncClip")
        self.welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        self.welcome_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #555555;
            }
        """)

        # 添加提示文本
        self.hint_label = QtWidgets.QLabel("请点击左侧登录按钮开始使用")
        self.hint_label.setAlignment(QtCore.Qt.AlignCenter)
        self.hint_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #888888;
            }
        """)

        # 添加到布局
        blank_layout.addStretch(1)  # 顶部弹性空间
        blank_layout.addWidget(self.emoji_label)
        blank_layout.addWidget(self.welcome_label)
        blank_layout.addWidget(self.hint_label)
        blank_layout.addStretch(1)  # 底部弹性空间

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

        self.page_4 = QtWidgets.QWidget()
        self.page_4.setObjectName("page_4")
        self.userinfo_dialog = UserInfoDialog()  # 导入UserInfoDialog
        layout = QtWidgets.QVBoxLayout(self.page_4)
        layout.addWidget(self.userinfo_dialog)
        self.stackedWidget.addWidget(self.page_4)

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

    def show_page_4(self):
        """显示用户信息页面"""
        self.stackedWidget.setCurrentIndex(4)  # page_4 是用户信息页面
        self.update_nav_btn_style(self.btn_userinfo)

    def update_nav_btn_style(self, active_btn):
        """更新导航按钮样式，突出显示当前活动按钮"""
        # 包含所有导航按钮
        all_buttons = [
            self.btn_clipboard,
            self.btn_device,
            self.btn_login,
            self.btn_userinfo  # 添加用户信息按钮
        ]

        for btn in all_buttons:
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
        self.connect_login_signals()
        self.is_logged_in = False

        # 重写导航按钮的点击事件处理
        self.rebind_navigation_buttons()

    def rebind_navigation_buttons(self):
        """重新绑定导航按钮的点击事件，添加登录状态检查"""
        # 断开原有的连接
        self.ui.btn_clipboard.clicked.disconnect()
        self.ui.btn_device.clicked.disconnect()
        self.ui.btn_login.clicked.disconnect()

        # 重新连接，添加登录检查
        self.ui.btn_clipboard.clicked.connect(self.handle_clipboard_click)
        self.ui.btn_device.clicked.connect(self.handle_device_click)
        self.ui.btn_login.clicked.connect(self.ui.show_page_3)  # 登录按钮直接跳转

    def handle_clipboard_click(self):
        """处理剪切板按钮点击，检查登录状态"""
        if not self.is_logged_in:
            self.show_login_warning()
        else:
            self.ui.show_page_1()

    def handle_device_click(self):
        """处理设备按钮点击，检查登录状态"""
        if not self.is_logged_in:
            self.show_login_warning()
        else:
            self.ui.show_page_2()

    def show_login_warning(self):
        """显示登录警告"""
        QtWidgets.QMessageBox.warning(
            self,
            "请先登录",
            "请登录后查看此功能",
            QtWidgets.QMessageBox.Ok
        )

    def connect_login_signals(self):
        """连接登录成功的信号"""
        self.ui.login_dialog.accepted.connect(self.on_login_success)

    def on_login_success(self):
        """登录成功后设置用户信息"""
        self.is_logged_in = True

        login_dialog = self.ui.login_dialog
        api_url = login_dialog.api_url
        username = login_dialog.get_current_username()
        device_info = login_dialog.get_device_info()
        token = login_dialog.get_token()

        # 设置设备对话框的用户信息
        self.ui.device_dialog.set_user_info(api_url, username, device_info.get('device_id'), token)

        # 设置剪贴板对话框的用户信息
        self.ui.clipboard_dialog.set_user_info(
            api_url,
            username,
            device_info.get('device_id'),
            device_info.get('label', '当前设备'),
            token
        )

        # 设置用户信息页面 - 直接传入必要参数
        self.ui.userinfo_dialog.set_user_info(
            username,
            device_info.get('label', '当前设备')
        )

        # 连接退出登录信号
        self.ui.userinfo_dialog.logout_requested.connect(self.handle_logout)

        # 显示用户信息按钮
        self.ui.btn_userinfo.show()
        self.ui.btn_login.hide()
        self.ui.show_page_4()  # 切换到用户信息页面

    def handle_logout(self):
        """处理退出登录"""
        self.is_logged_in = False

        # 重置各页面状态
        self.reset_clipboard_page()
        self.reset_device_page()
        self.reset_login_page()
        self.reset_userinfo_page()  # 添加用户信息页面重置

        # 更新导航栏
        self.ui.btn_userinfo.hide()
        self.ui.btn_login.show()

        # 切换到登录页面
        self.ui.stackedWidget.setCurrentIndex(3)
        self.ui.update_nav_btn_style(self.ui.btn_login)

    def reset_clipboard_page(self):
        """重置剪贴板页面到初始状态"""
        # 停止任何正在运行的剪贴板同步
        self.ui.clipboard_dialog.stop_sync()

        # 清除剪贴板列表 - 直接访问 listWidget
        self.ui.clipboard_dialog.listWidget.clear()  # 修改这里

        # 重置用户信息
        self.ui.clipboard_dialog.set_user_info(None, None, None, None, None)

    def reset_device_page(self):
        """重置设备页面到初始状态"""
        # 停止任何设备刷新
        self.ui.device_dialog.stop_refresh()

        # 清除设备列表 - 使用正确的控件名称
        self.ui.device_dialog.ui.listWidget.clear()  # 修改这里

        # 重置用户信息
        self.ui.device_dialog.set_user_info(None, None, None, None)

    def reset_login_page(self):
        """重置登录页面到初始状态 - 完全重新初始化登录对话框"""
        # 从堆叠窗口移除旧登录页面
        self.ui.stackedWidget.removeWidget(self.ui.page_3)

        # 创建全新的登录页面
        self.ui.page_3 = QtWidgets.QWidget()
        self.ui.page_3.setObjectName("page_3")

        # 创建新的登录对话框实例
        self.ui.login_dialog = LoginDialog()

        # 将新登录对话框添加到页面
        layout = QtWidgets.QVBoxLayout(self.ui.page_3)
        layout.addWidget(self.ui.login_dialog)

        # 将新页面添加到堆叠窗口（保持原来的索引位置）
        self.ui.stackedWidget.insertWidget(3, self.ui.page_3)

        # 重新连接登录成功信号
        self.connect_login_signals()

        # 确保登录页面是初始状态
        self.ui.login_dialog.reset_state()

    def reset_userinfo_page(self):
        """重置用户信息页面"""
        # 重新创建用户信息对话框
        self.ui.stackedWidget.removeWidget(self.ui.page_4)

        self.ui.page_4 = QtWidgets.QWidget()
        self.ui.page_4.setObjectName("page_4")
        self.ui.userinfo_dialog = UserInfoDialog()
        layout = QtWidgets.QVBoxLayout(self.ui.page_4)
        layout.addWidget(self.ui.userinfo_dialog)
        self.ui.stackedWidget.insertWidget(4, self.ui.page_4)

        # 重新连接退出信号
        self.ui.userinfo_dialog.logout_requested.connect(self.handle_logout)


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

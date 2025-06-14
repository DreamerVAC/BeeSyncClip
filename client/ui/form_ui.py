# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from page1_clipboard import Ui_Dialog, ClipboardDialog
from page2_device import DeviceDialog
from page3_login import LoginDialog
from page5_userinfo import UserInfoDialog
from page6_adminitrator import AdministratorDialog  # 保留管理员功能


class Ui_app_ui(object):
    def setupUi(self, app_ui):
        app_ui.setObjectName("app_ui")
        app_ui.resize(1000, 700)

        # 设置窗口图标和标题
        app_ui.setWindowIcon(QtGui.QIcon(':/icons/app_icon.png'))

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

        # 导航按钮样式
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

        # 用户信息按钮
        self.btn_userinfo = QtWidgets.QPushButton("用户信息")
        self.btn_userinfo.setStyleSheet(nav_btn_style)
        self.btn_userinfo.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.nav_layout.addWidget(self.btn_userinfo)
        self.btn_userinfo.hide()
        self.btn_userinfo.clicked.connect(self.show_page_4)

        # 管理员按钮 (保留)
        self.btn_admin = QtWidgets.QPushButton("管理员")
        self.btn_admin.setStyleSheet(nav_btn_style)
        self.btn_admin.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_admin.hide()
        self.nav_layout.addWidget(self.btn_admin)
        self.btn_admin.clicked.connect(self.show_page_6)

        # 设置按钮样式
        for btn in [self.btn_clipboard, self.btn_device, self.btn_login]:
            btn.setStyleSheet(nav_btn_style)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        # 添加按钮到导航栏
        self.nav_layout.addWidget(self.btn_clipboard)
        self.nav_layout.addWidget(self.btn_device)
        self.nav_layout.addWidget(self.btn_login)
        self.nav_layout.addStretch()

        # 右侧内容区域
        self.content_frame = QtWidgets.QFrame()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        # 堆叠窗口部件
        self.stackedWidget = QtWidgets.QStackedWidget()
        self.stackedWidget.setObjectName("stackedWidget")

        # 空白页面
        self.blank_page = QtWidgets.QWidget()
        self.blank_page.setObjectName("blank_page")
        blank_layout = QtWidgets.QVBoxLayout(self.blank_page)
        blank_layout.setContentsMargins(0, 0, 0, 0)
        blank_layout.setSpacing(20)

        self.emoji_label = QtWidgets.QLabel()
        self.emoji_label.setAlignment(QtCore.Qt.AlignCenter)
        self.emoji_label.setStyleSheet("QLabel { font-size: 100px; }")
        self.emoji_label.setText("🐝")

        self.welcome_label = QtWidgets.QLabel("欢迎使用 BeeSyncClip")
        self.welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        self.welcome_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #555555;
            }
        """)

        self.hint_label = QtWidgets.QLabel("请点击左侧登录按钮开始使用")
        self.hint_label.setAlignment(QtCore.Qt.AlignCenter)
        self.hint_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #888888;
            }
        """)

        blank_layout.addStretch(1)
        blank_layout.addWidget(self.emoji_label)
        blank_layout.addWidget(self.welcome_label)
        blank_layout.addWidget(self.hint_label)
        blank_layout.addStretch(1)

        self.stackedWidget.addWidget(self.blank_page)
        self.init_pages()
        self.content_layout.addWidget(self.stackedWidget)
        self.main_layout.addWidget(self.nav_frame)
        self.main_layout.addWidget(self.content_frame)

        self.retranslateUi(app_ui)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(app_ui)

        # 绑定按钮点击事件
        self.btn_clipboard.clicked.connect(self.show_page_1)
        self.btn_device.clicked.connect(self.show_page_2)
        self.btn_login.clicked.connect(self.show_page_3)

    def init_pages(self):
        """初始化所有子页面(包括管理员页面)"""
        # 页面1 (剪切板)
        self.page_1 = QtWidgets.QWidget()
        self.page_1.setObjectName("page_1")
        self.clipboard_dialog = ClipboardDialog()
        layout = QtWidgets.QVBoxLayout(self.page_1)
        layout.addWidget(self.clipboard_dialog)
        self.stackedWidget.addWidget(self.page_1)

        # 页面2 (设备)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.device_dialog = DeviceDialog()
        layout = QtWidgets.QVBoxLayout(self.page_2)
        layout.addWidget(self.device_dialog)
        self.stackedWidget.addWidget(self.page_2)

        # 页面3 (登录)
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setObjectName("page_3")
        self.login_dialog = LoginDialog()
        layout = QtWidgets.QVBoxLayout(self.page_3)
        layout.addWidget(self.login_dialog)
        self.stackedWidget.addWidget(self.page_3)

        # 页面4 (用户信息)
        self.page_4 = QtWidgets.QWidget()
        self.page_4.setObjectName("page_4")
        self.userinfo_dialog = UserInfoDialog()
        layout = QtWidgets.QVBoxLayout(self.page_4)
        layout.addWidget(self.userinfo_dialog)
        self.stackedWidget.addWidget(self.page_4)

        # 页面6 (管理员页面 - 保留)
        # 页面6 (管理员页面 - 保留)
        self.page_6 = QtWidgets.QWidget()
        self.page_6.setObjectName("page_6")

        # 使用占位符文本创建初始内容
        placeholder = QtWidgets.QLabel("管理员功能需登录后使用")
        placeholder.setAlignment(QtCore.Qt.AlignCenter)
        placeholder.setStyleSheet("font-size: 16px; color: #888888;")

        layout = QtWidgets.QVBoxLayout(self.page_6)
        layout.addWidget(placeholder)
        self.stackedWidget.addWidget(self.page_6)

    def retranslateUi(self, app_ui):
        _translate = QtCore.QCoreApplication.translate
        app_ui.setWindowTitle(_translate("app_ui", "BeeSyncClip"))
        self.title_label.setText(_translate("app_ui", "BeeSyncClip"))
        self.btn_clipboard.setText(_translate("app_ui", "剪切板"))
        self.btn_device.setText(_translate("app_ui", "设备"))
        self.btn_login.setText(_translate("app_ui", "登录"))
        self.btn_userinfo.setText(_translate("app_ui", "用户信息"))
        self.btn_admin.setText(_translate("app_ui", "管理员"))

    def show_page_1(self):
        self.stackedWidget.setCurrentIndex(1)
        self.update_nav_btn_style(self.btn_clipboard)

    def show_page_2(self):
        self.stackedWidget.setCurrentIndex(2)
        self.update_nav_btn_style(self.btn_device)

    def show_page_3(self):
        self.stackedWidget.setCurrentIndex(3)
        self.update_nav_btn_style(self.btn_login)

    def show_page_4(self):
        self.stackedWidget.setCurrentIndex(4)
        self.update_nav_btn_style(self.btn_userinfo)

    def show_page_6(self):
        """显示管理员页面(保留)"""
        self.stackedWidget.setCurrentIndex(5)
        self.update_nav_btn_style(self.btn_admin)

    def update_nav_btn_style(self, active_btn):
        """更新导航按钮样式"""
        all_buttons = [
            self.btn_clipboard,
            self.btn_device,
            self.btn_login,
            self.btn_userinfo,
            self.btn_admin  # 保留管理员按钮
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
        self.is_logged_in = False
        self.connect_signals()
        self.rebind_navigation_buttons()
        self.admin_token = None  # 添加成员变量保存管理员token

    def connect_signals(self):
        """连接所有信号(包括管理员相关信号)"""
        self.ui.login_dialog.accepted.connect(self.on_user_login_success)
        self.ui.login_dialog.adminLoginRequested.connect(self.on_admin_login_success)
        self.ui.userinfo_dialog.logout_requested.connect(self.handle_logout)
        #self.ui.admin_dialog.backRequested.connect(self.handle_admin_back)

    def rebind_navigation_buttons(self):
        """重新绑定导航按钮"""
        self.ui.btn_clipboard.clicked.disconnect()
        self.ui.btn_device.clicked.disconnect()
        self.ui.btn_login.clicked.disconnect()

        self.ui.btn_clipboard.clicked.connect(self.handle_clipboard_click)
        self.ui.btn_device.clicked.connect(self.handle_device_click)
        self.ui.btn_login.clicked.connect(self.ui.show_page_3)

    def handle_clipboard_click(self):
        if not self.is_logged_in:
            self.show_login_warning()
        else:
            self.ui.show_page_1()

    def handle_device_click(self):
        if not self.is_logged_in:
            self.show_login_warning()
        else:
            self.ui.show_page_2()

    def show_login_warning(self):
        QtWidgets.QMessageBox.warning(
            self, "请先登录", "请登录后查看此功能", QtWidgets.QMessageBox.Ok
        )

    def on_user_login_success(self):
        """普通用户登录成功处理"""
        self.is_logged_in = True
        login_dialog = self.ui.login_dialog

        api_url = login_dialog.api_url
        username = login_dialog.get_current_username()
        device_info = login_dialog.get_device_info()
        token = login_dialog.get_token()

        self.ui.device_dialog.set_user_info(api_url, username, device_info.get('device_id'), token)
        self.ui.clipboard_dialog.set_user_info(
            api_url, username, device_info.get('device_id'), device_info.get('label', '当前设备'), token
        )
        self.ui.userinfo_dialog.set_user_info(username, device_info.get('label', '当前设备'))

        self.ui.btn_userinfo.show()
        self.ui.btn_login.hide()
        self.ui.btn_clipboard.show()
        self.ui.btn_device.show()
        self.ui.btn_admin.hide()
        self.ui.show_page_4()

    def on_admin_login_success(self, token):
        """管理员登录成功处理"""
        #print(f"[MAIN_WINDOW] 收到管理员Token: {token}")
        self.admin_token = token  # 保存token
        #print(f"[MAIN_WINDOW] 创建AdministratorDialog，传入Token: {token}")

        # 如果已有管理员对话框，先清除
        if hasattr(self.ui, 'admin_dialog') and self.ui.admin_dialog:
            layout = self.ui.page_6.layout()
            if layout:
                layout.removeWidget(self.ui.admin_dialog)
            self.ui.admin_dialog.deleteLater()
            self.ui.admin_dialog = None

        # 创建新的管理员对话框并传入 parent
        self.ui.admin_dialog = AdministratorDialog(token, parent=self)

        # 添加返回按钮的信号绑定
        self.ui.admin_dialog.backRequested.connect(self.handle_admin_back)

        # 获取 page_6 的 layout，如果没有则创建
        layout = self.ui.page_6.layout()
        if layout is None:
            layout = QtWidgets.QVBoxLayout(self.ui.page_6)
            self.ui.page_6.setLayout(layout)

        # 清空旧组件（保留 layout）
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 添加 admin 页面内容
        layout.addWidget(self.ui.admin_dialog)

        # 更新左侧导航栏按钮状态
        self.ui.btn_admin.show()
        self.ui.btn_login.hide()
        self.ui.btn_clipboard.hide()
        self.ui.btn_device.hide()
        self.ui.btn_userinfo.hide()
        self.ui.stackedWidget.setCurrentIndex(5)
        self.ui.update_nav_btn_style(self.ui.btn_admin)

        # 加载用户列表
        self.ui.admin_dialog.load_users()

    def handle_admin_back(self):
        """处理从管理员界面返回"""
        # 重置管理员页面
        self.admin_token = None  # 重置token

        # 清除管理员对话框
        if hasattr(self.ui, 'admin_dialog') and self.ui.admin_dialog:
            self.ui.page_6.layout().removeWidget(self.ui.admin_dialog)
            self.ui.admin_dialog.deleteLater()
            self.ui.admin_dialog = None

        # 重新创建空白管理员页面
        placeholder = QtWidgets.QLabel("管理员功能需登录后使用")
        placeholder.setAlignment(QtCore.Qt.AlignCenter)
        placeholder.setStyleSheet("font-size: 16px; color: #888888;")

        # 清除页面内容
        layout = self.ui.page_6.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 添加占位符
        layout.addWidget(placeholder)

        # 更新导航栏
        self.ui.nav_frame.show()
        self.ui.btn_admin.hide()
        self.ui.btn_login.show()
        self.ui.btn_clipboard.show()
        self.ui.btn_device.show()
        self.ui.stackedWidget.setCurrentIndex(3)  # 切换到登录页面
        self.ui.login_dialog.reset_state()
        self.ui.update_nav_btn_style(self.ui.btn_login)

    def handle_logout(self):
        """处理退出登录"""
        self.is_logged_in = False
        self.reset_all_pages()

        self.ui.btn_userinfo.hide()
        self.ui.btn_admin.hide()
        self.ui.btn_login.show()
        self.ui.stackedWidget.setCurrentIndex(3)
        self.ui.update_nav_btn_style(self.ui.btn_login)

    def reset_all_pages(self):
        """重置所有页面状态"""
        # 剪贴板页面
        self.ui.clipboard_dialog.stop_sync()
        self.ui.clipboard_dialog.listWidget.clear()
        self.ui.clipboard_dialog.set_user_info(None, None, None, None, None)

        # 设备页面
        self.ui.device_dialog.stop_refresh()
        self.ui.device_dialog.ui.listWidget.clear()
        self.ui.device_dialog.set_user_info(None, None, None, None)

        # 登录页面
        self.reset_login_page()

        # 用户信息页面
        self.reset_userinfo_page()

        # 管理员页面
        # 管理员页面
        self.admin_token = None  # 重置token
        self.ui.stackedWidget.removeWidget(self.ui.page_6)

        # 重新创建空白管理员页面
        self.ui.page_6 = QtWidgets.QWidget()
        self.ui.page_6.setObjectName("page_6")

        # 添加占位符
        placeholder = QtWidgets.QLabel("管理员功能需登录后使用")
        placeholder.setAlignment(QtCore.Qt.AlignCenter)
        placeholder.setStyleSheet("font-size: 16px; color: #888888;")

        layout = QtWidgets.QVBoxLayout(self.ui.page_6)
        layout.addWidget(placeholder)
        self.ui.stackedWidget.addWidget(self.ui.page_6)

    def reset_login_page(self):
        self.ui.stackedWidget.removeWidget(self.ui.page_3)
        self.ui.page_3 = QtWidgets.QWidget()
        self.ui.page_3.setObjectName("page_3")
        self.ui.login_dialog = LoginDialog()
        layout = QtWidgets.QVBoxLayout(self.ui.page_3)
        layout.addWidget(self.ui.login_dialog)
        self.ui.stackedWidget.insertWidget(3, self.ui.page_3)
        self.connect_signals()
        self.ui.login_dialog.reset_state()

    def reset_userinfo_page(self):
        self.ui.stackedWidget.removeWidget(self.ui.page_4)
        self.ui.page_4 = QtWidgets.QWidget()
        self.ui.page_4.setObjectName("page_4")
        self.ui.userinfo_dialog = UserInfoDialog()
        layout = QtWidgets.QVBoxLayout(self.ui.page_4)
        layout.addWidget(self.ui.userinfo_dialog)
        self.ui.stackedWidget.insertWidget(4, self.ui.page_4)
        self.ui.userinfo_dialog.logout_requested.connect(self.handle_logout)


if __name__ == "__main__":
    import sys
    import traceback


    def excepthook(exc_type, exc_value, exc_traceback):
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"发生未捕获的异常:\n{error_msg}")
        QtWidgets.QMessageBox.critical(None, "错误", f"程序发生错误:\n{str(exc_value)}")
        sys.exit(1)


    sys.excepthook = excepthook

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from page4_register import Ui_RegisterDialog  # 导入注册页面的UI类
import requests
import json
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
import platform
import uuid
import os
import socket

def get_local_ip():
    """获取本机局域网IP地址"""
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            ip = "127.0.0.1"
    finally:
        if s:
            s.close()
    return ip

class RegisterThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, api_url, data):
        super().__init__()
        self.api_url = api_url
        self.data = data

    def run(self):
        try:
            response = requests.post(f"{self.api_url}/register", json=self.data)
            self.finished.emit(response.json())
        except Exception as e:
            self.error.emit(str(e))

class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName("LoginDialog")
        LoginDialog.resize(400, 300)

        # 主垂直布局
        self.verticalLayout = QtWidgets.QVBoxLayout(LoginDialog)
        self.verticalLayout.setObjectName("verticalLayout")

        # 标题标签
        self.label_title = QtWidgets.QLabel(LoginDialog)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_title.setFont(font)
        self.label_title.setObjectName("label_title")
        self.verticalLayout.addWidget(self.label_title)

        # 添加间距
        self.verticalLayout.addSpacing(30)

        # 账号输入框
        self.horizontalLayout_username = QtWidgets.QHBoxLayout()
        self.horizontalLayout_username.setObjectName("horizontalLayout_username")
        self.label_username = QtWidgets.QLabel(LoginDialog)
        self.label_username.setObjectName("label_username")
        self.horizontalLayout_username.addWidget(self.label_username)
        self.lineEdit_username = QtWidgets.QLineEdit(LoginDialog)
        self.lineEdit_username.setObjectName("lineEdit_username")
        self.horizontalLayout_username.addWidget(self.lineEdit_username)
        self.verticalLayout.addLayout(self.horizontalLayout_username)

        # 添加间距
        self.verticalLayout.addSpacing(20)

        # 密码输入框
        self.horizontalLayout_password = QtWidgets.QHBoxLayout()
        self.horizontalLayout_password.setObjectName("horizontalLayout_password")
        self.label_password = QtWidgets.QLabel(LoginDialog)
        self.label_password.setObjectName("label_password")
        self.horizontalLayout_password.addWidget(self.label_password)
        self.lineEdit_password = QtWidgets.QLineEdit(LoginDialog)
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.horizontalLayout_password.addWidget(self.lineEdit_password)
        self.verticalLayout.addLayout(self.horizontalLayout_password)

        # 添加间距
        self.verticalLayout.addSpacing(30)

        # 登录按钮
        self.pushButton_login = QtWidgets.QPushButton(LoginDialog)
        self.pushButton_login.setObjectName("pushButton_login")
        self.verticalLayout.addWidget(self.pushButton_login)

        # 注册按钮
        self.pushButton_register = QtWidgets.QPushButton(LoginDialog)
        self.pushButton_register.setObjectName("pushButton_register")
        self.verticalLayout.addWidget(self.pushButton_register)

        # 登录反馈标签
        self.login_feedback_label = QtWidgets.QLabel(LoginDialog)
        self.login_feedback_label.setAlignment(QtCore.Qt.AlignCenter)
        self.login_feedback_label.setObjectName("login_feedback_label")
        self.verticalLayout.addWidget(self.login_feedback_label)

        # 底部弹簧
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(LoginDialog)
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)

    def retranslateUi(self, LoginDialog):
        """设置界面元素的文本内容"""
        _translate = QtCore.QCoreApplication.translate
        LoginDialog.setWindowTitle(_translate("LoginDialog", "登录"))
        self.label_title.setText(_translate("LoginDialog", "用户登录"))
        self.label_username.setText(_translate("LoginDialog", "账号:"))
        self.label_password.setText(_translate("LoginDialog", "密码:"))
        self.pushButton_login.setText(_translate("LoginDialog", "登录"))
        self.pushButton_register.setText(_translate("LoginDialog", "注册"))
        self.login_feedback_label.setText("")


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_LoginDialog()
        self.ui.setupUi(self)

        self.api_url = "http://47.110.154.99:8000"
        self.username = None
        self.device_info = None
        self.token = None
        self.device_id = self.get_persistent_device_id()

        # 连接按钮信号
        self.ui.pushButton_login.clicked.connect(self.on_login_clicked)
        self.ui.pushButton_register.clicked.connect(self.show_register_dialog)

    def show_register_dialog(self):
        """显示注册对话框"""
        register_dialog = RegisterDialog(self)
        register_dialog.api_url = self.api_url
        if register_dialog.exec_() == QtWidgets.QDialog.Accepted:
            username = register_dialog.get_username()
            if username:
                self.ui.lineEdit_username.setText(username)

    def get_device_info(self):
        """获取设备信息并生成唯一标识"""
        import platform
        import socket
        import uuid
        import hashlib

        # 获取基本设备信息
        hostname = socket.gethostname()
        os_info = platform.system()
        os_version = platform.release()
        ip_address = get_local_ip()  # 使用新的函数获取IP
        mac_address = ":".join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 8*6, 8)][::-1])

        return {
            "device_id": self.device_id, # 使用持久化ID
            "device_name": hostname,
            "platform": os_info,
            "version": os_version,
            "ip_address": ip_address,
            "mac_address": mac_address,
            "label": f"{hostname} ({os_info})"
        }

    def on_login_clicked(self):
        """处理登录按钮点击事件"""
        username = self.ui.lineEdit_username.text().strip()
        password = self.ui.lineEdit_password.text().strip()

        device_info = self.get_device_info()

        if not username or not password:
            self.ui.login_feedback_label.setText("请输入用户名和密码")
            return

        try:
            # 构造请求数据，包含设备信息
            login_data = {
                "username": username,
                "password": password,
                "device_info": device_info
            }

            # 发送登录请求
            response = requests.post(f"{self.api_url}/login", json=login_data, timeout=5)
            result = response.json()

            if response.status_code == 200 and result.get("success"):
                self.username = username
                self.device_info = result.get("current_device", {})
                self.token = result.get("token")  # 保存token
                self.current_username = username
                self.devices = result.get("devices", [])
                QMessageBox.information(self, "成功", "登录成功!")
                self.accept()
            else:
                error_msg = result.get("message", "登录失败，请检查账号和密码")
                QMessageBox.warning(self, "登录失败", error_msg)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "错误", f"网络错误: {str(e)}")
        except json.JSONDecodeError:
            QMessageBox.critical(self, "错误", "服务器响应格式错误")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"登录时发生未知错误: {str(e)}")

    def get_current_user_devices(self):
        """获取当前用户的设备列表"""
        return self.devices

    def get_current_username(self):
        """返回当前登录的用户名"""
        return self.username

    def get_token(self):
        """返回登录成功后获取的token"""
        return self.token

    def get_persistent_device_id(self):
        """获取持久化的设备ID，如果不存在则创建"""
        config_file = "device_id.conf"
        try:
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    device_id = f.read().strip()
                    if device_id:
                        return device_id
        except Exception as e:
            print(f"读取device_id失败: {e}")

        # 如果文件不存在或为空，则创建新的ID
        new_device_id = str(uuid.uuid4())
        try:
            with open(config_file, "w") as f:
                f.write(new_device_id)
        except Exception as e:
            print(f"保存device_id失败: {e}")
        
        return new_device_id


class RegisterDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_RegisterDialog()
        self.ui.setupUi(self)
        self.api_url = ""  # 初始化空属性

        # 存储注册成功的用户名
        self.registered_username = None

        # 连接按钮信号
        self.ui.pushButton_register.clicked.connect(self.handle_register)
        self.ui.pushButton_back.clicked.connect(self.close)

    def handle_register(self):
        """处理注册逻辑"""
        username = self.ui.lineEdit_username.text().strip()
        password = self.ui.lineEdit_password.text().strip()
        confirm_password = self.ui.lineEdit_confirm.text().strip()

        if not username or not password or not confirm_password:
            QMessageBox.warning(self, "警告", "所有字段不能为空!")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致!")
            return

        # 构造请求数据
        data = {
            "username": username,
            "password": password
        }

        # 创建并启动线程
        self.thread = RegisterThread(self.api_url, data)
        self.thread.finished.connect(self.handle_register_response)
        self.thread.error.connect(self.handle_register_error)
        self.thread.start()

    def handle_register_response(self, result):
        if result.get("success"):
            self.registered_username = self.ui.lineEdit_username.text().strip()
            QMessageBox.information(self, "成功", "注册成功!")
            self.accept()
        else:
            error_msg = result.get("message", "注册失败，请稍后重试")
            QMessageBox.warning(self, "注册失败", error_msg)

    def handle_register_error(self, error_msg):
        QMessageBox.critical(self, "错误", f"网络错误: {error_msg}")

    def get_username(self):
        """获取注册成功的用户名"""
        return self.registered_username

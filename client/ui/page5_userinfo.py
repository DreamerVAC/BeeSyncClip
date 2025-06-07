# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_UserInfoDialog(object):
    def setupUi(self, UserInfoDialog):
        UserInfoDialog.setObjectName("UserInfoDialog")
        UserInfoDialog.resize(500, 400)  # 增加窗口大小
        UserInfoDialog.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
        """)

        # 主垂直布局
        self.verticalLayout = QtWidgets.QVBoxLayout(UserInfoDialog)
        self.verticalLayout.setContentsMargins(30, 40, 30, 30)  # 增加上边距
        self.verticalLayout.setSpacing(25)

        # 欢迎标题
        self.label_welcome = QtWidgets.QLabel(UserInfoDialog)
        font = QtGui.QFont()
        font.setPointSize(22)  # 增大字体
        font.setWeight(QtGui.QFont.DemiBold)  # 使用半粗体
        self.label_welcome.setFont(font)
        self.label_welcome.setAlignment(QtCore.Qt.AlignCenter)
        self.label_welcome.setStyleSheet("""
            color: #2c3e50;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        """)
        self.verticalLayout.addWidget(self.label_welcome)

        # 用户信息框
        self.info_frame = QtWidgets.QFrame(UserInfoDialog)
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 25px;
                border: none;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            }
        """)
        self.info_layout = QtWidgets.QVBoxLayout(self.info_frame)
        self.info_layout.setContentsMargins(15, 15, 15, 15)
        self.info_layout.setSpacing(20)

        # 用户名
        self.username_frame = QtWidgets.QFrame(self.info_frame)
        self.username_layout = QtWidgets.QHBoxLayout(self.username_frame)
        self.username_layout.setContentsMargins(0, 0, 0, 0)

        self.username_icon = QtWidgets.QLabel(self.username_frame)
        self.username_icon.setFixedSize(24, 24)
        self.username_icon.setStyleSheet("""
            background-color: #3498db;
            border-radius: 12px;
        """)
        self.username_layout.addWidget(self.username_icon)

        self.label_username = QtWidgets.QLabel(self.username_frame)
        self.label_username.setStyleSheet("""
            font-size: 16px;
            color: #2c3e50;
            font-weight: 500;
        """)
        self.username_layout.addWidget(self.label_username, 1)
        self.info_layout.addWidget(self.username_frame)

        # 设备信息
        self.device_frame = QtWidgets.QFrame(self.info_frame)
        self.device_layout = QtWidgets.QHBoxLayout(self.device_frame)
        self.device_layout.setContentsMargins(0, 0, 0, 0)

        self.device_icon = QtWidgets.QLabel(self.device_frame)
        self.device_icon.setFixedSize(24, 24)
        self.device_icon.setStyleSheet("""
            background-color: #2ecc71;
            border-radius: 12px;
        """)
        self.device_layout.addWidget(self.device_icon)

        self.label_device = QtWidgets.QLabel(self.device_frame)
        self.label_device.setStyleSheet("""
            font-size: 16px;
            color: #2c3e50;
            font-weight: 500;
        """)
        self.device_layout.addWidget(self.label_device, 1)
        self.info_layout.addWidget(self.device_frame)

        self.verticalLayout.addWidget(self.info_frame)
        self.verticalLayout.addStretch(1)

        # 退出登录按钮
        self.btn_logout = QtWidgets.QPushButton(UserInfoDialog)
        self.btn_logout.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_logout.setFixedHeight(45)  # 增加按钮高度
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 25px;
                font-size: 16px;
                font-weight: 500;
                min-width: 150px;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.verticalLayout.addWidget(self.btn_logout, 0, QtCore.Qt.AlignHCenter)

        self.retranslateUi(UserInfoDialog)
        QtCore.QMetaObject.connectSlotsByName(UserInfoDialog)

    def retranslateUi(self, UserInfoDialog):
        _translate = QtCore.QCoreApplication.translate
        UserInfoDialog.setWindowTitle(_translate("UserInfoDialog", "用户信息"))
        self.label_welcome.setText(_translate("UserInfoDialog", "欢迎回来"))
        self.btn_logout.setText(_translate("UserInfoDialog", "退出登录"))


class UserInfoDialog(QtWidgets.QDialog):
    logout_requested = QtCore.pyqtSignal()  # 退出登录信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_UserInfoDialog()
        self.ui.setupUi(self)

        self.username = ""
        self.device_label = ""

        # 连接退出登录按钮信号
        self.ui.btn_logout.clicked.connect(self.logout)

    def set_user_info(self, username, device_label):
        self.username = username
        self.device_label = device_label

        # 更新界面显示
        self.ui.label_welcome.setText(f"欢迎回来, {username}")
        self.ui.label_username.setText(f"用户名: {username}")
        self.ui.label_device.setText(f"当前设备: {device_label}")

    def logout(self):
        # 发出退出登录信号
        self.logout_requested.emit()
        self.close()

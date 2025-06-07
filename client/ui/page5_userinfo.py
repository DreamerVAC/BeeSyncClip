# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_UserInfoDialog(object):
    def setupUi(self, UserInfoDialog):
        UserInfoDialog.setObjectName("UserInfoDialog")
        UserInfoDialog.resize(400, 300)
        UserInfoDialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
        """)

        # 主垂直布局
        self.verticalLayout = QtWidgets.QVBoxLayout(UserInfoDialog)
        self.verticalLayout.setContentsMargins(30, 30, 30, 30)
        self.verticalLayout.setSpacing(20)

        # 欢迎标题
        self.label_welcome = QtWidgets.QLabel(UserInfoDialog)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setWeight(QtGui.QFont.Bold)
        self.label_welcome.setFont(font)
        self.label_welcome.setAlignment(QtCore.Qt.AlignCenter)
        self.label_welcome.setStyleSheet("color: #333;")
        self.verticalLayout.addWidget(self.label_welcome)

        # 用户信息框
        self.info_frame = QtWidgets.QFrame(UserInfoDialog)
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.info_layout = QtWidgets.QVBoxLayout(self.info_frame)
        self.info_layout.setContentsMargins(10, 10, 10, 10)
        self.info_layout.setSpacing(15)

        # 用户名
        self.label_username = QtWidgets.QLabel(self.info_frame)
        self.label_username.setStyleSheet("font-size: 14px;")
        self.info_layout.addWidget(self.label_username)

        # 设备信息
        self.label_device = QtWidgets.QLabel(self.info_frame)
        self.label_device.setStyleSheet("font-size: 14px; color: #666;")
        self.info_layout.addWidget(self.label_device)

        self.verticalLayout.addWidget(self.info_frame)
        self.verticalLayout.addStretch(1)

        # 退出登录按钮
        self.btn_logout = QtWidgets.QPushButton(UserInfoDialog)
        self.btn_logout.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
            QPushButton:pressed {
                background-color: #d32f2f;
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
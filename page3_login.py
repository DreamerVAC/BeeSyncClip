# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


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

        # 提示文字
        self.label_hint = QtWidgets.QLabel(LoginDialog)
        self.label_hint.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_hint.setFont(font)
        self.label_hint.setObjectName("label_hint")
        self.verticalLayout.addWidget(self.label_hint)

        # 底部弹簧
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(LoginDialog)
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)

    def retranslateUi(self, LoginDialog):
        _translate = QtCore.QCoreApplication.translate
        LoginDialog.setWindowTitle(_translate("LoginDialog", "登录"))
        self.label_title.setText(_translate("LoginDialog", "用户登录"))
        self.label_username.setText(_translate("LoginDialog", "账号:"))
        self.label_password.setText(_translate("LoginDialog", "密码:"))
        self.pushButton_login.setText(_translate("LoginDialog", "登录"))
        self.label_hint.setText(_translate("LoginDialog", "提示: 如果没有账号将自动创建"))
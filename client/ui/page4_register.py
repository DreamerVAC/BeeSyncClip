# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import requests
import json

class Ui_RegisterDialog(object):
    def setupUi(self, RegisterDialog):
        RegisterDialog.setObjectName("RegisterDialog")
        RegisterDialog.resize(400, 350)

        # 主垂直布局
        self.verticalLayout = QtWidgets.QVBoxLayout(RegisterDialog)
        self.verticalLayout.setObjectName("verticalLayout")

        # 标题标签
        self.label_title = QtWidgets.QLabel(RegisterDialog)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_title.setFont(font)
        self.label_title.setObjectName("label_title")
        self.verticalLayout.addWidget(self.label_title)

        # 添加间距
        self.verticalLayout.addSpacing(20)

        # 用户名输入框
        self.horizontalLayout_username = QtWidgets.QHBoxLayout()
        self.horizontalLayout_username.setObjectName("horizontalLayout_username")
        self.label_username = QtWidgets.QLabel(RegisterDialog)
        self.label_username.setObjectName("label_username")
        self.horizontalLayout_username.addWidget(self.label_username)
        self.lineEdit_username = QtWidgets.QLineEdit(RegisterDialog)
        self.lineEdit_username.setObjectName("lineEdit_username")
        self.horizontalLayout_username.addWidget(self.lineEdit_username)
        self.verticalLayout.addLayout(self.horizontalLayout_username)

        # 添加间距
        self.verticalLayout.addSpacing(15)

        # 密码输入框
        self.horizontalLayout_password = QtWidgets.QHBoxLayout()
        self.horizontalLayout_password.setObjectName("horizontalLayout_password")
        self.label_password = QtWidgets.QLabel(RegisterDialog)
        self.label_password.setObjectName("label_password")
        self.horizontalLayout_password.addWidget(self.label_password)
        self.lineEdit_password = QtWidgets.QLineEdit(RegisterDialog)
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.horizontalLayout_password.addWidget(self.lineEdit_password)
        self.verticalLayout.addLayout(self.horizontalLayout_password)

        # 添加间距
        self.verticalLayout.addSpacing(15)

        # 确认密码输入框
        self.horizontalLayout_confirm = QtWidgets.QHBoxLayout()
        self.horizontalLayout_confirm.setObjectName("horizontalLayout_confirm")
        self.label_confirm = QtWidgets.QLabel(RegisterDialog)
        self.label_confirm.setObjectName("label_confirm")
        self.horizontalLayout_confirm.addWidget(self.label_confirm)
        self.lineEdit_confirm = QtWidgets.QLineEdit(RegisterDialog)
        self.lineEdit_confirm.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_confirm.setObjectName("lineEdit_confirm")
        self.horizontalLayout_confirm.addWidget(self.lineEdit_confirm)
        self.verticalLayout.addLayout(self.horizontalLayout_confirm)

        # 添加间距
        self.verticalLayout.addSpacing(20)

        # 注册按钮
        self.pushButton_register = QtWidgets.QPushButton(RegisterDialog)
        self.pushButton_register.setObjectName("pushButton_register")
        self.verticalLayout.addWidget(self.pushButton_register)

        # 返回登录按钮
        self.pushButton_back = QtWidgets.QPushButton(RegisterDialog)
        self.pushButton_back.setObjectName("pushButton_back")
        self.verticalLayout.addWidget(self.pushButton_back)

        # 底部弹簧
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(RegisterDialog)
        QtCore.QMetaObject.connectSlotsByName(RegisterDialog)

    def retranslateUi(self, RegisterDialog):
        _translate = QtCore.QCoreApplication.translate

        RegisterDialog.setWindowTitle(_translate("RegisterDialog", "用户注册"))
        self.label_title.setText(_translate("RegisterDialog", "用户注册"))
        self.label_username.setText(_translate("RegisterDialog", "用户名:"))
        self.label_password.setText(_translate("RegisterDialog", "密码:"))
        self.label_confirm.setText(_translate("RegisterDialog", "确认密码:"))
        self.pushButton_register.setText(_translate("RegisterDialog", "注册"))
        self.pushButton_back.setText(_translate("RegisterDialog", "返回登录"))

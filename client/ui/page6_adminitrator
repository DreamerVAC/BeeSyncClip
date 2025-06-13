# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import requests


class Ui_AdministratorDialog(object):
    def setupUi(self, AdministratorDialog):
        AdministratorDialog.setObjectName("AdministratorDialog")
        AdministratorDialog.resize(800, 600)
        AdministratorDialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton#btn_delete {
                background-color: #f44336;
            }
            QPushButton#btn_delete:hover {
                background-color: #d32f2f;
            }
            QPushButton#btn_delete:pressed {
                background-color: #b71c1c;
            }
            QFrame {
                background-color: white;
                border-radius: 4px;
                border: 1px solid #e0e0e0;
            }
        """)

        # 主布局
        self.verticalLayout = QtWidgets.QVBoxLayout(AdministratorDialog)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName("verticalLayout")

        # 标题
        self.label_title = QtWidgets.QLabel("用户管理")
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.label_title.setFont(font)
        self.label_title.setStyleSheet("color: #2c3e50;")
        self.verticalLayout.addWidget(self.label_title)

        # 可滚动区域
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setObjectName("scrollArea")

        # 滚动区域内容
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 760, 500))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        # 用户列表布局
        self.user_list_layout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.user_list_layout.setContentsMargins(0, 0, 0, 0)
        self.user_list_layout.setSpacing(10)
        self.user_list_layout.setObjectName("user_list_layout")

        # 添加伸缩空间使列表顶部对齐
        self.user_list_layout.addStretch()

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        # 底部按钮布局
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setContentsMargins(0, 10, 0, 0)
        self.button_layout.setSpacing(20)
        self.button_layout.setObjectName("button_layout")

        # 刷新按钮
        self.btn_refresh = QtWidgets.QPushButton("刷新列表")
        self.btn_refresh.setObjectName("btn_refresh")
        self.btn_refresh.setIcon(QtGui.QIcon.fromTheme("view-refresh"))
        self.button_layout.addWidget(self.btn_refresh)

        # 返回按钮
        self.btn_back = QtWidgets.QPushButton("返回")
        self.btn_back.setObjectName("btn_back")
        self.btn_back.setIcon(QtGui.QIcon.fromTheme("go-previous"))
        self.button_layout.addWidget(self.btn_back)

        self.verticalLayout.addLayout(self.button_layout)

        self.retranslateUi(AdministratorDialog)
        QtCore.QMetaObject.connectSlotsByName(AdministratorDialog)

    def retranslateUi(self, AdministratorDialog):
        _translate = QtCore.QCoreApplication.translate
        AdministratorDialog.setWindowTitle(_translate("AdministratorDialog", "用户管理"))
        self.label_title.setText(_translate("AdministratorDialog", "用户管理"))
        self.btn_refresh.setText(_translate("AdministratorDialog", "刷新列表"))
        self.btn_back.setText(_translate("AdministratorDialog", "返回"))


class AdministratorDialog(QtWidgets.QDialog):
    backRequested = QtCore.pyqtSignal()  # 添加信号

    def __init__(self, token, parent=None):  # 修改构造函数
        super().__init__(parent)
        self.ui = Ui_AdministratorDialog()
        self.ui.setupUi(self)
        self.token = token  # 保存token
        self.api_url = "http://47.110.154.99:8000"

        # 连接按钮信号
        self.ui.btn_back.clicked.connect(self.request_back)
        self.ui.btn_refresh.clicked.connect(self.load_users)

    def request_back(self):
        """请求返回登录页面"""
        self.backRequested.emit()
        self.clear_users()

    def load_users(self):
        """从服务器加载用户列表"""
        try:
            # 使用保存的token
            headers = {
                "Authorization": f"Bearer {self.token}"  # 使用实例变量
            }

            # 发送请求获取用户列表
            response = requests.get(
                f"{self.api_url}/admin/users",
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    users = data.get("users", [])
                    self.display_users(users)
                else:
                    QtWidgets.QMessageBox.critical(
                        self,
                        "错误",
                        f"获取用户列表失败: {data.get('message', '未知错误')}"
                    )
            elif response.status_code == 401:
                QtWidgets.QMessageBox.critical(
                    self,
                    "认证失败",
                    "管理员Token无效或已过期"
                )
            else:
                QtWidgets.QMessageBox.critical(
                    self,
                    "错误",
                    f"获取用户列表失败，状态码: {response.status_code}"
                )
        except requests.exceptions.ConnectionError:
            QtWidgets.QMessageBox.critical(
                self,
                "网络错误",
                "无法连接到服务器，请检查网络连接"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "错误",
                f"发生未知错误: {str(e)}"
            )

    def display_users(self, users):
        """显示用户列表"""
        self.clear_users()

        if not users:
            no_users_label = QtWidgets.QLabel("暂无用户数据")
            no_users_label.setAlignment(QtCore.Qt.AlignCenter)
            no_users_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
            self.ui.user_list_layout.addWidget(no_users_label)
            return

        for user in users:
            self.create_user_row(user)

    def create_user_row(self, user):
        """创建一个用户行"""
        user_frame = QtWidgets.QFrame()
        user_frame.setStyleSheet("""
            QFrame {
                padding: 12px;
            }
        """)

        # 水平布局
        layout = QtWidgets.QHBoxLayout(user_frame)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(20)

        # 用户名标签
        username = user.get('username', '未知用户')
        lbl_username = QtWidgets.QLabel(username)
        lbl_username.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #2c3e50;
                min-width: 120px;
            }
        """)
        layout.addWidget(lbl_username)

        # 添加弹性空间
        layout.addStretch()

        # 删除按钮
        btn_delete = QtWidgets.QPushButton("删除")
        btn_delete.setObjectName("btn_delete")
        btn_delete.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_delete.clicked.connect(lambda _, u=user: self.confirm_delete_user(u))
        layout.addWidget(btn_delete)

        # 添加用户行到列表
        self.ui.user_list_layout.insertWidget(0, user_frame)  # 插入到顶部

    def confirm_delete_user(self, user):
        """确认删除用户"""
        username = user.get('username', '该用户')
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("确认删除")
        msg_box.setText(f'确定要删除用户 "{username}" 吗？')
        msg_box.setInformativeText("此操作不可恢复！")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        reply = msg_box.exec_()
        if reply == QMessageBox.Yes:
            self.delete_user(user)

    def delete_user(self, user):
        """删除用户（API调用格式与load_users完全一致）"""
        user_id = user.get('user_id')
        if not user_id:
            QtWidgets.QMessageBox.warning(self, "错误", "无效的用户ID")
            return

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        try:
            response = requests.delete(
                f"{self.api_url}/admin/users/{user_id}",
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    QtWidgets.QMessageBox.information(
                        self,
                        "成功",
                        f"用户已删除\n删除设备: {data.get('deleted_devices', 0)}\n删除剪贴板: {data.get('deleted_clipboards', 0)}"
                    )
                    self.load_users()  # 刷新列表
                else:
                    QtWidgets.QMessageBox.critical(
                        self,
                        "错误",
                        f"删除失败: {data.get('message', '未知错误')}"
                    )
            elif response.status_code == 401:
                QtWidgets.QMessageBox.critical(
                    self,
                    "认证失败",
                    "管理员Token无效或已过期"
                )
            else:
                QtWidgets.QMessageBox.critical(
                    self,
                    "错误",
                    f"删除失败，状态码: {response.status_code}"
                )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", f"网络错误: {str(e)}")

    def clear_users(self):
        """清除用户列表"""
        while self.ui.user_list_layout.count():
            item = self.ui.user_list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

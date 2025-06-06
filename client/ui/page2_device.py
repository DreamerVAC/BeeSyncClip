# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
import requests
import json


class Ui_DeviceDialog(object):
    def setupUi(self, ClipboardDialog):
        ClipboardDialog.setObjectName("ClipboardDialog")
        ClipboardDialog.resize(800, 600)
        ClipboardDialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-family: 'Microsoft YaHei';
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-family: 'Microsoft YaHei';
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                outline: 0;
            }
            QListWidget::item {
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #f9f9f9;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
        """)

        # 主垂直布局
        self.verticalLayout = QtWidgets.QVBoxLayout(ClipboardDialog)
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")

        # 标题标签
        self.label = QtWidgets.QLabel(ClipboardDialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setWeight(QtGui.QFont.Bold)
        self.label.setFont(font)
        self.label.setStyleSheet("color: #333;")
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        # 添加分割线
        self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setStyleSheet("color: #ddd;")
        self.verticalLayout.addWidget(self.line)

        # 剪贴板记录列表
        self.listWidget = QtWidgets.QListWidget(ClipboardDialog)
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QListWidget::item {
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
            QScrollArea {
                border: none;
            }
        """)
        self.verticalLayout.addWidget(self.listWidget)

        # 状态标签
        self.statusLabel = QtWidgets.QLabel(ClipboardDialog)
        self.statusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.statusLabel.setStyleSheet("color: #666; font-size: 12px;")
        self.statusLabel.setObjectName("statusLabel")
        self.verticalLayout.addWidget(self.statusLabel)

        # 同步按钮
        self.syncButton = QtWidgets.QPushButton(ClipboardDialog)
        self.syncButton.setObjectName("syncButton")
        self.syncButton.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.verticalLayout.addWidget(self.syncButton)

        self.retranslateUi(ClipboardDialog)
        QtCore.QMetaObject.connectSlotsByName(ClipboardDialog)

    def add_device_item(self, device_info, is_current_device=False):
        """添加设备项 - 简化版本"""
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(QtCore.QSize(200, 80))  # 稍微增加高度以适应更大的字体
        item.setData(QtCore.Qt.UserRole, device_info)

        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background-color: transparent;")
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)  # 增加内边距
        layout.setSpacing(12)

        # 设备图标
        icon_label = QtWidgets.QLabel()
        icon = QtGui.QIcon(":/icons/device_icon.png")  # 如果有资源文件
        pixmap = icon.pixmap(44, 44) if not icon.isNull() else QtGui.QPixmap(44, 44)  # 增大图标
        pixmap.fill(QtGui.QColor("#2196F3" if is_current_device else "#9E9E9E"))
        icon_label.setPixmap(pixmap)
        icon_label.setStyleSheet("border-radius: 22px;")
        layout.addWidget(icon_label)

        # 设备信息垂直布局
        info_layout = QtWidgets.QVBoxLayout()
        info_layout.setSpacing(5)

        # 设备名称 - 增大字体
        name_label = QtWidgets.QLabel(device_info.get('label', '未知设备'))
        name_label.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                font-size: 15px;
                color: #333;
            }
        """)
        info_layout.addWidget(name_label)

        # 设备详细信息 - 增大字体
        details_text = f"系统: {device_info.get('os', '未知')} | IP: {device_info.get('ip_address', '未知')}"
        details = QtWidgets.QLabel(details_text)
        details.setStyleSheet("""
            QLabel {
                color: #666; 
                font-size: 13px;
            }
        """)
        info_layout.addWidget(details)

        layout.addLayout(info_layout, 1)  # 添加伸缩因子

        # 删除按钮 - 增大字体
        delete_btn = QtWidgets.QPushButton("删除")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                padding: 7px 14px;
                border-radius: 4px;
                min-width: 70px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
            QPushButton:pressed {
                background-color: #D32F2F;
            }
        """)
        delete_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        delete_btn.clicked.connect(lambda: self.parent_dialog.confirm_remove_device(item))
        layout.addWidget(delete_btn)

        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)

    def retranslateUi(self, DeviceDialog):
        _translate = QtCore.QCoreApplication.translate
        DeviceDialog.setWindowTitle(_translate("DeviceDialog", "设备管理"))
        self.label.setText(_translate("DeviceDialog", "已登录的设备"))
        self.syncButton.setText(_translate("DeviceDialog", "刷新列表"))
        self.statusLabel.setText(_translate("DeviceDialog", "点击刷新按钮加载设备"))


class DeviceDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(DeviceDialog, self).__init__(parent)
        self.ui = Ui_DeviceDialog()
        self.ui.setupUi(self)
        self.ui.parent_dialog = self  # 让UI可以访问主对话框
        self.api_url = ""
        self.username = ""
        self.device_id = ""
        self.token = ""
        self.ui.syncButton.clicked.connect(self.load_devices)
        self.ui.retranslateUi(self) # Ensure translations are applied

    def set_user_info(self, api_url, username, device_id, token):
        self.api_url = api_url
        self.username = username
        self.device_id = device_id
        self.token = token

    def load_devices(self):
        if not all([self.api_url, self.username, self.token]):
            self.show_message("无法加载设备：信息不完整")
            return

        try:
            self.ui.listWidget.clear()
            self.ui.statusLabel.setText("正在加载设备列表...")
            url = f"{self.api_url}/get_devices?username={self.username}"
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    devices = result.get("devices", [])
                    self.ui.statusLabel.setText(f"共找到 {len(devices)} 个设备")
                    for device in devices:
                        is_current = device.get('device_id') == self.device_id
                        self.ui.add_device_item(device, is_current_device=is_current)
                else:
                    self.show_message(f"加载失败: {result.get('message')}")
            else:
                self.show_message(f"加载失败: 服务器错误 {response.status_code}")
        except Exception as e:
            self.show_message(f"加载时出错: {e}")

    def confirm_remove_device(self, item):
        """确认删除设备"""
        device_info = item.data(QtCore.Qt.UserRole)
        device_name = device_info.get('label', '未知设备')

        is_current_device = device_info.get('device_id') == self.device_id
        if is_current_device:
            QtWidgets.QMessageBox.warning(self, "提示", "不能删除当前正在使用的设备！")
            return

        reply = QtWidgets.QMessageBox.question(
            self, "确认删除", f"确定要删除设备 '{device_name}' 吗？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.remove_device_item(item)

    def remove_device_item(self, item):
        """删除设备项"""
        device_info = item.data(QtCore.Qt.UserRole)
        device_id = device_info.get("device_id")

        if not all([self.api_url, self.username, device_id, self.token]):
            self.show_message("无法删除设备：信息不完整")
            return

        try:
            url = f"{self.api_url}/remove_device"
            headers = {"Authorization": f"Bearer {self.token}"}
            data = {"username": self.username, "device_id": device_id}
            response = requests.post(url, json=data, headers=headers, timeout=5)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.ui.listWidget.takeItem(self.ui.listWidget.row(item))
                    self.show_message(f"设备 '{device_info.get('label')}' 已删除")
                else:
                    self.show_message(f"删除失败: {result.get('message')}")
            else:
                self.show_message(f"删除失败: 服务器错误 {response.status_code}")
        except Exception as e:
            self.show_message(f"删除时出错: {e}")

    def show_message(self, message):
        self.ui.statusLabel.setText(message)

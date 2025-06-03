# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
import requests
import json


class Ui_DeviceDialog(object):
    def setupUi(self, DeviceDialog):
        DeviceDialog.setObjectName("DeviceDialog")
        DeviceDialog.resize(600, 400)  # 适当减小窗口尺寸
        DeviceDialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
        """)

        # 主垂直布局
        self.verticalLayout = QtWidgets.QVBoxLayout(DeviceDialog)
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")

        # 标题标签
        self.label = QtWidgets.QLabel(DeviceDialog)
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

        # 设备列表
        self.listWidget = QtWidgets.QListWidget(DeviceDialog)
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setStyleSheet("""
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
        self.verticalLayout.addWidget(self.listWidget)

        self.retranslateUi(DeviceDialog)
        QtCore.QMetaObject.connectSlotsByName(DeviceDialog)

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
        delete_btn.clicked.connect(lambda: self.confirm_remove_device(item, is_current_device))
        layout.addWidget(delete_btn)

        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)

    def confirm_remove_device(self, item, is_current_device):
        """确认删除设备"""
        device_info = item.data(QtCore.Qt.UserRole)
        device_name = device_info.get('label', '未知设备')

        if is_current_device:
            QtWidgets.QMessageBox.warning(None, "提示", "不能删除当前正在使用的设备！")
            return

        reply = QtWidgets.QMessageBox.question(
            None,
            "确认删除",
            f"确定要删除设备 '{device_name}' 吗？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.remove_device_item(item)

    def remove_device_item(self, item):
        """删除设备项"""
        device_info = item.data(QtCore.Qt.UserRole)

        try:
            response = requests.post(f"{self.api_url}/remove_device", json={
                "username": self.username,
                "device_id": device_info.get("device_id")
            })

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    row = self.listWidget.row(item)
                    self.listWidget.takeItem(row)

                    # 显示删除的剪贴板记录数量
                    removed_count = result.get("removed_clip_count", 0)
                    if removed_count > 0:
                        QtWidgets.QMessageBox.information(
                            None,
                            "删除成功",
                            f"设备删除成功，同时删除了{removed_count}条相关剪贴板记录"
                        )
                    else:
                        QtWidgets.QMessageBox.information(None, "成功", "设备删除成功")
                else:
                    QtWidgets.QMessageBox.warning(None, "错误", result.get("message", "删除设备失败"))
            else:
                QtWidgets.QMessageBox.warning(None, "错误", "删除设备失败")
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "错误", f"删除设备时出错: {str(e)}")

    def retranslateUi(self, DeviceDialog):
        _translate = QtCore.QCoreApplication.translate
        DeviceDialog.setWindowTitle(_translate("DeviceDialog", "设备管理"))
        self.label.setText(_translate("DeviceDialog", "我的设备"))


class DeviceDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_DeviceDialog()
        self.ui.setupUi(self)

        # 设置UI对象的api_url属性
        self.ui.api_url = ""
        self.ui.username = ""
        self.ui.current_device_id = ""

    def set_user_info(self, api_url, username, current_device_id):
        """设置用户信息后加载设备"""
        self.ui.api_url = api_url
        self.ui.username = username
        self.ui.current_device_id = current_device_id
        self.load_devices()

    def load_devices(self):
        """从服务器加载设备列表"""
        if not self.ui.username or not self.ui.api_url:
            QtWidgets.QMessageBox.warning(self, "警告", "请先登录后再查看设备列表")
            return

        try:
            response = requests.get(f"{self.ui.api_url}/get_devices?username={self.ui.username}")
            result = response.json()

            if response.status_code == 200 and result.get("success"):
                devices = result.get("devices", [])

                # 清空现有列表
                self.ui.listWidget.clear()

                for device in devices:
                    is_current = device.get('device_id') == self.ui.current_device_id
                    self.ui.add_device_item(device, is_current)
            else:
                QtWidgets.QMessageBox.warning(self, "错误", result.get("message", "获取设备列表失败"))

        except requests.exceptions.ConnectionError:
            QtWidgets.QMessageBox.critical(self, "连接错误", "无法连接到服务器，请检查网络连接")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", f"加载设备列表失败: {str(e)}")

# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
import requests
import json
import time  # 添加这行导入


class Ui_Dialog(object):
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

    def retranslateUi(self, ClipboardDialog):
        _translate = QtCore.QCoreApplication.translate
        ClipboardDialog.setWindowTitle(_translate("ClipboardDialog", "BeeSyncClip - 剪贴板"))
        self.label.setText(_translate("ClipboardDialog", "云端剪贴板记录"))
        self.statusLabel.setText(_translate("ClipboardDialog", "正在加载..."))
        self.syncButton.setText(_translate("ClipboardDialog", "手动同步"))


class ClipboardDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # 添加标志位，用于标记是否忽略剪贴板变化
        self.ignore_clipboard_change = False  # <-- 新增标志位

        self.api_url = None
        self.username = None
        self.device_id = None
        self.device_label = None
        self.token = None

        self.clipboard = QtWidgets.QApplication.clipboard()
        self.last_clipboard_text = self.clipboard.text()
        self.init_clipboard_monitor()

    def set_user_info(self, api_url, username, device_id, device_label, token):
        self.api_url = api_url
        self.username = username
        self.device_id = device_id
        self.device_label = device_label
        self.token = token
        self.load_clipboard_records()
        self.update_status(f"就绪 | 设备: {device_label}")

    def add_clipboard_item(self, record):
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(QtCore.QSize(600, 120))
        item.setData(QtCore.Qt.UserRole, record)

        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background-color: transparent;")
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)

        device_info_layout = QtWidgets.QHBoxLayout()
        icon_label = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(24, 24)
        pixmap.fill(QtGui.QColor("#2196F3"))
        icon_label.setPixmap(pixmap)
        device_info_layout.addWidget(icon_label)

        device_label = QtWidgets.QLabel(f"来自: {record.get('device_label', '未知设备')}")
        device_label.setStyleSheet("font-size: 12px; color: #666; font-weight: bold;")
        device_info_layout.addWidget(device_label)

        timestamp = record.get('created_at', '')
        if timestamp:
            time_label = QtWidgets.QLabel(f"时间: {timestamp}")
            time_label.setStyleSheet("font-size: 12px; color: #888;")
            device_info_layout.addWidget(time_label)

        device_info_layout.addStretch(1)
        layout.addLayout(device_info_layout)

        content_layout = QtWidgets.QHBoxLayout()
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")

        content_widget = QtWidgets.QWidget()
        content_widget_layout = QtWidgets.QVBoxLayout(content_widget)
        content_label = QtWidgets.QLabel(record.get('content', '无内容'))
        content_label.setWordWrap(True)
        content_widget_layout.addWidget(content_label)
        scroll_area.setWidget(content_widget)
        content_layout.addWidget(scroll_area, 1)

        btn_layout = QtWidgets.QVBoxLayout()

        # 新增的内容复制按钮
        content_copy_btn = QtWidgets.QPushButton("复制")
        content_copy_btn.setFixedSize(80, 30)
        content_copy_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        content_copy_btn.clicked.connect(lambda: self.copy_content_only(record.get('content', '')))
        btn_layout.addWidget(content_copy_btn)

        delete_btn = QtWidgets.QPushButton("删除")
        delete_btn.setFixedSize(80, 30)
        delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        delete_btn.clicked.connect(lambda: self.confirm_remove_record(item))
        btn_layout.addWidget(delete_btn)

        content_layout.addLayout(btn_layout)
        layout.addLayout(content_layout)
        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)

    def copy_content_only(self, content):
        # 设置忽略标志
        self.ignore_clipboard_change = True  # <-- 设置标志位

        # 执行复制操作
        self.clipboard.setText(content)
        self.update_status(f"已复制内容: {content[:20]}...")

        # 重置标志位（使用单次定时器，确保只忽略当前这次变化）
        QtCore.QTimer.singleShot(100, lambda: setattr(self, 'ignore_clipboard_change', False))

    def confirm_remove_record(self, item):
        record = item.data(QtCore.Qt.UserRole)
        reply = QtWidgets.QMessageBox.question(self, '确认删除', '确定要删除这条剪贴板记录吗？',
                                           QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                           QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.remove_record_item(item)

    def remove_record_item(self, item):
        record = item.data(QtCore.Qt.UserRole)
        record_id = record.get("clip_id")

        if not self.api_url or not record_id or not self.token:
            self.update_status("错误：无法删除记录，API信息不完整")
            return

        try:
            url = f"{self.api_url.rstrip('/')}/delete_clipboard"
            headers = {'Authorization': f'Bearer {self.token}'}
            data = {"username": self.username, "clip_id": record_id}
            response = requests.post(url, json=data, headers=headers, timeout=5)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.listWidget.takeItem(self.listWidget.row(item))
                    self.update_status("记录已删除")
                else:
                    self.update_status(f"删除失败: {result.get('message')}")
            else:
                self.update_status(f"删除失败: {response.json().get('detail', '未知错误')}")
        except Exception as e:
            self.update_status(f"删除时出错: {e}")

    def load_clipboard_records(self):
        if not self.api_url or not self.token:
            self.update_status("错误：用户信息未设置，无法加载记录")
            return

        try:
            self.update_status("正在从云端加载...")
            url = f"{self.api_url.rstrip('/')}/get_clipboards"
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(url, headers=headers, params={'username': self.username})

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    records = result.get("clipboards", [])
                    self.listWidget.clear()
                    if records:
                        for record in sorted(records, key=lambda x: x.get('created_at'), reverse=True):
                            self.add_clipboard_item(record)
                        self.update_status(f"加载了 {len(records)} 条记录")
                    else:
                        self.show_no_records_message()
                else:
                    self.update_status(f"加载失败: {result.get('message')}")
            else:
                self.update_status(f"加载失败: {response.status_code}")
        except Exception as e:
            self.update_status(f"加载错误: {e}")

    def show_no_records_message(self):
        self.listWidget.clear()
        item = QtWidgets.QListWidgetItem("没有可用的剪贴板记录。")
        self.listWidget.addItem(item)

    def init_clipboard_monitor(self):
        self.clipboard.dataChanged.connect(self.on_clipboard_changed)

    def on_clipboard_changed(self):
        # 如果设置了忽略标志，则不处理这次变化
        if self.ignore_clipboard_change:  # <-- 检查标志位
            return

        if self.clipboard.mimeData().hasText():
            current_text = self.clipboard.text()
            if current_text != self.last_clipboard_text:
                self.last_clipboard_text = current_text
                self.add_local_clipboard_item(current_text)

    def add_local_clipboard_item(self, content):
        if not self.username:
            return
        self.send_to_server(content)

    def send_to_server(self, content):
        if not self.api_url or not self.token:
            return

        try:
            url = f"{self.api_url.rstrip('/')}/add_clipboard"
            headers = {"Authorization": f"Bearer {self.token}"}
            data = {
                "username": self.username,
                "content": content,
                "device_id": self.device_id,
                "content_type": "text/plain"
            }
            response = requests.post(url, json=data, headers=headers, timeout=5)

            if response.status_code == 201:
                result = response.json()
                if result.get("success"):
                    self.update_status("新内容已同步到云端")
                    # 重新加载以显示新项目，包括来自服务器的ID
                    self.load_clipboard_records()
                else:
                    self.update_status(f"同步失败: {result.get('message')}")
            else:
                self.update_status(f"同步失败: 服务器错误 {response.status_code}")
        except Exception as e:
            self.update_status(f"同步错误: {e}")

    def update_status(self, message):
        self.statusLabel.setText(message)

    def stop_sync(self):
        """停止剪贴板同步"""
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()

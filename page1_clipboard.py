# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
import requests
import json


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
            QPushButton#copy_btn {
                background-color: #2196F3;
            }
            QPushButton#copy_btn:hover {
                background-color: #1976D2;
            }
            QPushButton#copy_btn:pressed {
                background-color: #0D47A1;
            }
            QPushButton#delete_btn {
                background-color: #f44336;
            }
            QPushButton#delete_btn:hover {
                background-color: #d32f2f;
            }
            QPushButton#delete_btn:pressed {
                background-color: #b71c1c;
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

        # 按钮水平布局
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

    def set_user_info(self, api_url, username):
        """设置用户信息"""
        self.api_url = api_url  # 去掉 self.ui. 直接使用 self
        self.username = username
        self.load_clipboard_records()  # 自动加载数据

    def add_clipboard_item(self, record):
        """添加剪贴板记录项（带滚动条和操作按钮）"""
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(QtCore.QSize(600, 100))
        item.setData(QtCore.Qt.UserRole, record)  # 设置记录数据

        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background-color: transparent;")
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # --- 左侧：可滚动的内容区域 ---
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")

        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        content_layout = QtWidgets.QVBoxLayout(content_widget)

        content_label = QtWidgets.QLabel(record.get('content', '无内容'))
        content_label.setWordWrap(True)
        content_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
                padding: 5px;
            }
        """)
        content_layout.addWidget(content_label)
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area, 1)

        # --- 右侧：操作按钮 ---
        btn_layout = QtWidgets.QVBoxLayout()
        btn_layout.setSpacing(5)

        # 复制按钮
        copy_btn = QtWidgets.QPushButton("复制")
        copy_btn.setObjectName("copy_btn")
        copy_btn.setFixedSize(80, 30)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        copy_btn.clicked.connect(lambda: self.copy_content(record.get('content', '')))
        btn_layout.addWidget(copy_btn)

        # 删除按钮
        delete_btn = QtWidgets.QPushButton("删除")
        delete_btn.setObjectName("delete_btn")
        delete_btn.setFixedSize(80, 30)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        delete_btn.clicked.connect(lambda: self.confirm_remove_record(item))
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)
        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)

    def copy_content(self, content):
        """复制纯文本内容到剪贴板"""
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(content)

        # 修复后的正确调用方式
        QtWidgets.QToolTip.showText(
            QtGui.QCursor.pos(),  # 鼠标当前位置
            "已复制到剪贴板",  # 提示文本
            self.listWidget,  # 父控件（使用列表控件）
            QtCore.QRect(),  # 显示区域（空矩形表示默认位置）
            2000  # 显示时间（毫秒）
        )

    def confirm_remove_record(self, item):
        """确认删除记录"""
        record = item.data(QtCore.Qt.UserRole)
        if not record:  # 添加检查
            QtWidgets.QMessageBox.warning(None, "错误", "无法获取记录数据")
            return

        content_preview = record.get('content', '无内容')[:30] + "..." if len(
            record.get('content', '')) > 30 else record.get('content', '无内容')

        reply = QtWidgets.QMessageBox.question(
            None,
            "确认删除",
            f"确定要删除记录 '{content_preview}' 吗？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.remove_record_item(item)

    def remove_record_item(self, item):
        """删除记录项"""
        record = item.data(QtCore.Qt.UserRole)
        if not record:  # 添加检查
            QtWidgets.QMessageBox.warning(None, "错误", "无法获取记录数据")
            return

        try:
            response = requests.post(f"{self.api_url}/delete_clipboard", json={
                "username": self.username,
                "clip_id": record.get("clip_id")
            })

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    row = self.listWidget.row(item)
                    self.listWidget.takeItem(row)
                    QtWidgets.QMessageBox.information(None, "成功", "记录删除成功")
                else:
                    QtWidgets.QMessageBox.warning(None, "错误", result.get("message", "删除记录失败"))
            else:
                QtWidgets.QMessageBox.warning(None, "错误", f"删除记录失败，状态码: {response.status_code}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "错误", f"删除记录时出错: {str(e)}")





    def retranslateUi(self, ClipboardDialog):
        _translate = QtCore.QCoreApplication.translate
        ClipboardDialog.setWindowTitle(_translate("ClipboardDialog", "剪贴板历史"))
        self.label.setText(_translate("ClipboardDialog", "剪贴板历史记录"))
        self.syncButton.setText(_translate("ClipboardDialog", "同步剪贴板"))  # 更新按钮文本

    def show_no_records_message(self):
        """显示无记录的提示"""
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(QtCore.QSize(200, 60))

        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background-color: transparent;")
        layout = QtWidgets.QHBoxLayout(widget)

        label = QtWidgets.QLabel("暂无剪贴板记录")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("color: #999; font-size: 14px;")
        layout.addWidget(label)

        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)

class ClipboardDialog(QtWidgets.QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.ui = Ui_Dialog()
            self.ui.setupUi(self)

            # 设置默认值（登录后会覆盖）
            self.ui.api_url = "http://localhost:8000"
            self.ui.username = "testuser"

            # 绑定同步按钮事件
            self.ui.syncButton.clicked.connect(self.load_clipboard_records)

            # 初始加载数据
            self.load_clipboard_records()

        def set_user_info(self, api_url, username):
            """设置用户信息（登录后调用）"""
            self.ui.api_url = api_url
            self.ui.username = username
            self.load_clipboard_records()  # 登录后自动刷新

        def load_clipboard_records(self):
            """从服务器加载剪贴板记录（点击同步按钮时触发）"""
            try:
                # 获取设备信息
                devices_response = requests.get(f"{self.ui.api_url}/get_devices?username={self.ui.username}")
                devices_result = devices_response.json()

                if devices_response.status_code != 200 or not devices_result.get("success"):
                    QtWidgets.QMessageBox.warning(self, "警告", "获取设备信息失败")
                    return

                device_map = {d['device_id']: d['label'] for d in devices_result.get("devices", [])}

                # 获取剪贴板记录
                response = requests.get(f"{self.ui.api_url}/get_clipboards?username={self.ui.username}")
                result = response.json()

                if response.status_code == 200 and result.get("success"):
                    records = result.get("clipboards", [])
                    self.ui.listWidget.clear()

                    if not records:
                        self.ui.show_no_records_message()
                    else:
                        for record in records:
                            record['device_label'] = device_map.get(record.get('device_id'), '未知设备')
                            self.ui.add_clipboard_item(record)
                else:
                    QtWidgets.QMessageBox.warning(self, "错误", result.get("message", "获取剪贴板记录失败"))

            except requests.exceptions.ConnectionError:
                QtWidgets.QMessageBox.critical(self, "连接错误", "无法连接到服务器，请检查网络连接")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "错误", f"加载剪贴板记录失败: {str(e)}")

        def show_no_records_message(self):
            """显示无记录提示"""
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(QtCore.QSize(200, 60))
            widget = QtWidgets.QWidget()
            widget.setStyleSheet("background-color: transparent;")
            layout = QtWidgets.QHBoxLayout(widget)
            label = QtWidgets.QLabel("暂无剪贴板记录")
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("color: #999; font-size: 14px;")
            layout.addWidget(label)
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)



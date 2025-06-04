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

    def update_status(self, message):
        """更新状态标签文本"""
        self.statusLabel.setText(message)

    def set_user_info(self, api_url, username, device_id, device_label):
        """设置用户信息和设备信息"""
        self.api_url = api_url
        self.username = username
        self.device_id = device_id
        self.device_label = device_label
        self.load_clipboard_records()  # 自动加载数据

        # 更新状态标签
        self.update_status("就绪 | 设备: " + device_label)

    def add_clipboard_item(self, record):
        """添加剪贴板记录项（带滚动条和操作按钮）"""
        item = QtWidgets.QListWidgetItem()
        # 增加高度以容纳设备信息
        item.setSizeHint(QtCore.QSize(600, 120))
        item.setData(QtCore.Qt.UserRole, record)  # 设置记录数据

        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background-color: transparent;")
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)

        # --- 设备信息行 ---
        device_info_layout = QtWidgets.QHBoxLayout()

        # 设备图标
        icon_label = QtWidgets.QLabel()
        icon = QtGui.QIcon(":/icons/device_icon.png")  # 如果有资源文件
        pixmap = icon.pixmap(24, 24) if not icon.isNull() else QtGui.QPixmap(24, 24)
        pixmap.fill(QtGui.QColor("#2196F3"))
        icon_label.setPixmap(pixmap)
        icon_label.setStyleSheet("border-radius: 12px;")
        device_info_layout.addWidget(icon_label)

        # 设备标签
        device_label = QtWidgets.QLabel(f"来自: {record.get('device_label', '未知设备')}")
        device_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
                font-weight: bold;
            }
        """)
        device_info_layout.addWidget(device_label)

        # 时间标签
        timestamp = record.get('timestamp', '')
        if timestamp:
            time_label = QtWidgets.QLabel(f"时间: {timestamp}")
            time_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #888;
                }
            """)
            device_info_layout.addWidget(time_label)

        device_info_layout.addStretch(1)  # 添加伸缩因子使设备信息靠左
        layout.addLayout(device_info_layout)

        # --- 内容区域 ---
        content_layout = QtWidgets.QHBoxLayout()

        # 可滚动的内容区域
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")

        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        content_widget_layout = QtWidgets.QVBoxLayout(content_widget)

        content_label = QtWidgets.QLabel(record.get('content', '无内容'))
        content_label.setWordWrap(True)
        content_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
                padding: 5px;
            }
        """)
        content_widget_layout.addWidget(content_label)
        scroll_area.setWidget(content_widget)
        content_layout.addWidget(scroll_area, 1)

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

        content_layout.addLayout(btn_layout)
        layout.addLayout(content_layout)

        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)

    def copy_content(self, content):
        """复制纯文本内容到剪贴板"""
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(content)

        # 显示复制成功提示
        QtWidgets.QToolTip.showText(
            QtGui.QCursor.pos(),
            "已复制到剪贴板",
            self.listWidget,
            QtCore.QRect(),
            2000
        )

    def confirm_remove_record(self, item):
        """确认删除记录"""
        record = item.data(QtCore.Qt.UserRole)
        if not record:
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
        if not record:
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
        self.syncButton.setText(_translate("ClipboardDialog", "同步剪贴板"))

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
    def __init__(self, parent=None):  # 移除必需的参数
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # 初始化空属性
        self.api_url = None
        self.username = None
        self.device_id = None
        self.device_label = None

        # 绑定同步按钮事件
        self.ui.syncButton.clicked.connect(self.load_clipboard_records)

        # 初始时不加载数据
        # 更新状态
        self.ui.update_status("请先登录")

        # 初始化剪贴板监听
        self.init_clipboard_monitor()

        # 设置定时器
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(30000)

        # 记录上次剪贴板内容
        self.last_clipboard_content = ""

    def init_clipboard_monitor(self):
        """初始化剪贴板监听器"""
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_changed)

    def on_clipboard_changed(self):
        """剪贴板内容变化时的处理"""
        # 获取剪贴板内容
        clipboard_text = self.clipboard.text().strip()

        # 忽略空内容或与上次相同的内容
        if not clipboard_text or clipboard_text == self.last_clipboard_content:
            return

        # 更新上次内容
        self.last_clipboard_content = clipboard_text

        # 添加到本地剪贴板历史
        self.add_local_clipboard_item(clipboard_text)

        # 发送到服务器
        self.send_to_server(clipboard_text)

        # 更新状态
        self.ui.update_status(f"已添加新内容 | 设备: {self.device_label} | 长度: {len(clipboard_text)}字符")

        # 显示提示
        QtWidgets.QToolTip.showText(
            QtGui.QCursor.pos(),
            "已添加到剪贴板历史",
            self,
            QtCore.QRect(),
            2000
        )

    def check_clipboard(self):
        """定时检查剪贴板内容（备用方法）"""
        current_text = self.clipboard.text().strip()
        if current_text and current_text != self.last_clipboard_content:
            self.on_clipboard_changed()

    def add_local_clipboard_item(self, content):
        """在本地添加剪贴板记录项"""
        # 创建记录对象
        record = {
            "clip_id": str(int(time.time())),  # 使用时间戳作为临时ID
            "content": content,
            "content_type": "text/plain",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_modified": time.strftime("%Y-%m-%d %H:%M:%S"),
            "device_id": self.device_id,
            "device_label": self.device_label
        }

        # 添加到列表顶部
        self.ui.add_clipboard_item(record)

    def send_to_server(self, content):
        """将剪贴板内容发送到服务器"""
        try:
            response = requests.post(f"{self.api_url}/add_clipboard", json={
                "username": self.username,
                "content": content,
                "device_id": self.device_id,
                "content_type": "text/plain"
            })

            if response.status_code == 201:
                result = response.json()
                if result.get("success"):
                    # 更新状态
                    self.ui.update_status(f"已同步到服务器 | 设备: {self.device_label}")
                else:
                    self.ui.update_status(f"同步失败: {result.get('message', '未知错误')}")
            else:
                self.ui.update_status(f"服务器错误: {response.status_code}")
        except Exception as e:
            self.ui.update_status(f"网络错误: {str(e)}")

    def set_user_info(self, api_url, username, device_id, device_label):
        """设置用户信息（登录后调用）"""
        self.api_url = api_url
        self.username = username
        self.device_id = device_id
        self.device_label = device_label

        # 设置后加载数据
        self.load_clipboard_records()

        # 更新状态
        self.ui.update_status(f"就绪 | 设备: {device_label} | 正在监听剪贴板...")

    def load_clipboard_records(self):
        """从服务器加载剪贴板记录（点击同步按钮时触发）"""
        self.ui.update_status("正在同步剪贴板记录...")
        try:
            # 获取设备信息
            devices_response = requests.get(f"{self.api_url}/get_devices?username={self.username}")
            devices_result = devices_response.json()

            if devices_response.status_code != 200 or not devices_result.get("success"):
                QtWidgets.QMessageBox.warning(self, "警告", "获取设备信息失败")
                self.ui.update_status("同步失败: 无法获取设备信息")
                return

            device_map = {d['device_id']: d['label'] for d in devices_result.get("devices", [])}

            # 获取剪贴板记录
            response = requests.get(f"{self.api_url}/get_clipboards?username={self.username}")
            result = response.json()

            if response.status_code == 200 and result.get("success"):
                records = result.get("clipboards", [])
                self.ui.listWidget.clear()

                if not records:
                    self.ui.show_no_records_message()
                    self.ui.update_status("同步完成 | 无剪贴板记录")
                else:
                    # 按时间倒序排序
                    sorted_records = sorted(records, key=lambda x: x.get('created_at', ''), reverse=True)

                    for record in sorted_records:
                        # 添加设备标签信息
                        record['device_label'] = device_map.get(record.get('device_id'), '未知设备')
                        self.ui.add_clipboard_item(record)

                    self.ui.update_status(f"同步完成 | 共 {len(records)} 条记录")
            else:
                QtWidgets.QMessageBox.warning(self, "错误", result.get("message", "获取剪贴板记录失败"))
                self.ui.update_status(f"同步失败: {result.get('message', '未知错误')}")

        except requests.exceptions.ConnectionError:
            QtWidgets.QMessageBox.critical(self, "连接错误", "无法连接到服务器，请检查网络连接")
            self.ui.update_status("同步失败: 无法连接到服务器")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", f"加载剪贴板记录失败: {str(e)}")
            self.ui.update_status(f"同步失败: {str(e)}")

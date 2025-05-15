# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DeviceDialog(object):
    def setupUi(self, DeviceDialog):
        DeviceDialog.setObjectName("DeviceDialog")
        DeviceDialog.resize(600, 400)

        # 主垂直布局
        self.verticalLayout = QtWidgets.QVBoxLayout(DeviceDialog)
        self.verticalLayout.setObjectName("verticalLayout")

        # 标题标签
        self.label = QtWidgets.QLabel(DeviceDialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        # 添加间距
        self.verticalLayout.addSpacing(20)

        # 设备列表
        self.listWidget = QtWidgets.QListWidget(DeviceDialog)
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                height: 40px;
            }
        """)
        self.verticalLayout.addWidget(self.listWidget)

        # 添加示例设备
        self.add_device_item("我的手机 (192.168.1.100)")
        self.add_device_item("办公室电脑 (192.168.1.101)")
        self.add_device_item("家庭平板 (192.168.1.102)")

        # 底部弹簧
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(DeviceDialog)
        QtCore.QMetaObject.connectSlotsByName(DeviceDialog)

    def add_device_item(self, device_name):
        """添加带有删除按钮的设备项"""
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(QtCore.QSize(200, 40))  # 设置项的大小

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(10, 0, 10, 0)

        # 设备名称标签
        label = QtWidgets.QLabel(device_name)
        label.setStyleSheet("font-size: 14px;")
        layout.addWidget(label)

        # 弹簧，将删除按钮推到右侧
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addItem(spacer)

        # 删除按钮
        delete_btn = QtWidgets.QPushButton("删除")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
        """)
        delete_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        delete_btn.clicked.connect(lambda: self.remove_device_item(item))
        layout.addWidget(delete_btn)

        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)

    def remove_device_item(self, item):
        """删除设备项"""
        row = self.listWidget.row(item)
        self.listWidget.takeItem(row)

    def retranslateUi(self, DeviceDialog):
        _translate = QtCore.QCoreApplication.translate
        DeviceDialog.setWindowTitle(_translate("DeviceDialog", "设备管理"))
        self.label.setText(_translate("DeviceDialog", "我的设备"))
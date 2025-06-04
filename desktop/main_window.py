"""
BeeSyncClip 主窗口
参考 EcoPaste 的简洁设计风格
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit, QPushButton, QLabel,
    QSystemTrayIcon, QMenu, QSplitter, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QIcon, QFont, QPixmap, QAction, QPalette, QColor
import pyperclip
from datetime import datetime


class ClipboardItem:
    """剪贴板条目数据类"""
    def __init__(self, content, content_type="text", timestamp=None):
        self.content = content
        self.content_type = content_type
        self.timestamp = timestamp or datetime.now()
        self.favorite = False
        self.tags = []
    
    def __str__(self):
        preview = str(self.content)[:50]
        if len(str(self.content)) > 50:
            preview += "..."
        return f"[{self.content_type}] {preview}"


class ClipboardMonitor(QThread):
    """剪贴板监控线程"""
    new_item = pyqtSignal(ClipboardItem)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.last_content = ""
    
    def run(self):
        while self.running:
            try:
                current_content = pyperclip.paste()
                if current_content != self.last_content and current_content.strip():
                    self.last_content = current_content
                    item = ClipboardItem(current_content, "text")
                    self.new_item.emit(item)
                self.msleep(500)  # 500ms检查间隔
            except Exception as e:
                print(f"剪贴板监控错误: {e}")
                self.msleep(1000)
    
    def stop(self):
        self.running = False


class ClipboardListWidget(QListWidget):
    """自定义剪贴板列表组件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.items_data = []
    
    def setup_ui(self):
        """设置UI样式"""
        self.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: #f8f9fa;
                alternate-background-color: #ffffff;
                selection-background-color: #007AFF;
                selection-color: white;
                font-size: 14px;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #e9ecef;
                margin: 2px;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
            QListWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
        """)
        self.setAlternatingRowColors(True)
    
    def add_item(self, clipboard_item):
        """添加剪贴板条目"""
        self.items_data.insert(0, clipboard_item)  # 最新的在前面
        
        # 创建列表项
        item = QListWidgetItem()
        
        # 设置显示内容
        display_text = self.format_item_text(clipboard_item)
        item.setText(display_text)
        
        # 插入到列表顶部
        self.insertItem(0, item)
        
        # 限制历史记录数量
        if self.count() > 100:
            self.takeItem(self.count() - 1)
            self.items_data.pop()
    
    def format_item_text(self, clipboard_item):
        """格式化显示文本"""
        content = str(clipboard_item.content)
        
        # 处理多行文本
        lines = content.split('\n')
        preview = lines[0][:60]
        if len(lines) > 1:
            preview += f" ... (+{len(lines)-1} 行)"
        elif len(content) > 60:
            preview += "..."
        
        # 添加时间戳
        time_str = clipboard_item.timestamp.strftime("%H:%M")
        
        return f"{preview}\n{time_str} · {clipboard_item.content_type}"
    
    def get_selected_item_data(self):
        """获取选中项的数据"""
        current_row = self.currentRow()
        if 0 <= current_row < len(self.items_data):
            return self.items_data[current_row]
        return None


class SearchBar(QLineEdit):
    """搜索栏组件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        self.setPlaceholderText("🔍 搜索剪贴板历史...")
        self.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #e9ecef;
                border-radius: 25px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #007AFF;
                outline: none;
            }
        """)


class PreviewPanel(QFrame):
    """预览面板"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # 标题
        self.title_label = QLabel("预览")
        self.title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #333; margin-bottom: 10px;")
        
        # 内容显示
        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        self.content_text.setStyleSheet("""
            QTextEdit {
                border: none;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.content_text)
    
    def update_preview(self, clipboard_item):
        """更新预览内容"""
        if not clipboard_item:
            self.content_text.clear()
            self.title_label.setText("预览")
            return
        
        self.title_label.setText(f"预览 - {clipboard_item.content_type}")
        self.content_text.setPlainText(str(clipboard_item.content))


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.clipboard_monitor = None
        self.setup_ui()
        self.setup_tray()
        self.start_clipboard_monitoring()
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("BeeSyncClip - 跨平台剪贴板同步")
        self.setGeometry(100, 100, 1000, 700)
        
        # 设置现代化样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
        """)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 顶部搜索栏
        self.search_bar = SearchBar()
        self.search_bar.textChanged.connect(self.filter_items)
        main_layout.addWidget(self.search_bar)
        
        # 分割器 - 左边列表，右边预览
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧剪贴板列表
        self.clipboard_list = ClipboardListWidget()
        self.clipboard_list.itemSelectionChanged.connect(self.on_item_selected)
        self.clipboard_list.itemDoubleClicked.connect(self.copy_to_clipboard)
        splitter.addWidget(self.clipboard_list)
        
        # 右侧预览面板
        self.preview_panel = PreviewPanel()
        splitter.addWidget(self.preview_panel)
        
        # 设置分割器比例
        splitter.setSizes([400, 300])
        main_layout.addWidget(splitter)
        
        # 底部状态栏
        self.setup_status_bar()
    
    def setup_status_bar(self):
        """设置状态栏"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2c3e50;
                color: white;
                font-size: 12px;
            }
        """)
        status_bar.showMessage("就绪 - 正在监控剪贴板...")
    
    def setup_tray(self):
        """设置系统托盘"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        self.tray_icon = QSystemTrayIcon(self)
        # 这里需要一个图标文件，先用默认图标
        # self.tray_icon.setIcon(QIcon("path/to/icon.png"))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # 双击托盘图标显示窗口
        self.tray_icon.activated.connect(self.on_tray_activated)
    
    def on_tray_activated(self, reason):
        """托盘图标激活处理"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
    
    def show_window(self):
        """显示主窗口"""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def start_clipboard_monitoring(self):
        """开始剪贴板监控"""
        self.clipboard_monitor = ClipboardMonitor()
        self.clipboard_monitor.new_item.connect(self.on_new_clipboard_item)
        self.clipboard_monitor.start()
    
    def on_new_clipboard_item(self, item):
        """处理新的剪贴板条目"""
        self.clipboard_list.add_item(item)
        self.statusBar().showMessage(f"新增剪贴板条目: {item.content_type}", 2000)
    
    def on_item_selected(self):
        """处理列表项选择"""
        selected_item = self.clipboard_list.get_selected_item_data()
        self.preview_panel.update_preview(selected_item)
    
    def copy_to_clipboard(self):
        """复制选中项到剪贴板"""
        selected_item = self.clipboard_list.get_selected_item_data()
        if selected_item:
            pyperclip.copy(str(selected_item.content))
            self.statusBar().showMessage("已复制到剪贴板", 1000)
    
    def filter_items(self, text):
        """过滤列表项"""
        # TODO: 实现搜索过滤功能
        pass
    
    def closeEvent(self, event):
        """关闭事件处理"""
        if self.tray_icon and self.tray_icon.isVisible():
            # 最小化到托盘而不是退出
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "BeeSyncClip", 
                "应用已最小化到系统托盘",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            event.accept()
    
    def __del__(self):
        """析构函数"""
        if self.clipboard_monitor:
            self.clipboard_monitor.stop()
            self.clipboard_monitor.wait()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出应用
    
    # 设置应用信息
    app.setApplicationName("BeeSyncClip")
    app.setApplicationVersion("1.0.0")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 
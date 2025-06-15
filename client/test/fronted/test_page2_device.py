import unittest
import sys
import time
import logging
import os
from unittest.mock import patch, Mock
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from client.ui.page2_device import DeviceDialog
from tqdm import tqdm
from termcolor import colored
import matplotlib.pyplot as plt

# 调整模块路径以找到 client.ui
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'ui'))

# 配置日志
logging.basicConfig(
    filename='device_test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestDeviceDialog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication(sys.argv)
        cls.test_results = {'passed': 0, 'failed': 0, 'errors': 0}
        cls.total_tests = 0
        cls.test_names = []
        cls.test_statuses = []
        cls.start_time = time.time()

    def setUp(self):
        self.dialog = DeviceDialog()
        self.dialog.device_id = "dev1"  # 初始化 device_id 以匹配测试数据
        self.dialog.show()
        QTest.qWaitForWindowExposed(self.dialog, 1000)
        # 确保事件循环处理
        QtWidgets.QApplication.processEvents()

    def run(self, result=None):
        if result is None:
            result = self.defaultTestResult()
        self.total_tests += 1
        test_name = self._testMethodName
        self.test_names.append(test_name)
        print(f"\nRunning test: {test_name}")
        logging.info(f"Starting test: {test_name}")

        with tqdm(total=1, desc="Progress", bar_format='{l_bar}{bar:20}{r_bar}') as pbar:
            super().run(result)
            pbar.update(1)

        if result.wasSuccessful():
            self.test_results['passed'] += 1
            self.test_statuses.append('passed')
            print(colored(f"Test {test_name} PASSED", 'green'))
            logging.info(f"Test {test_name} PASSED")
        else:
            if result.failures:
                self.test_results['failed'] += 1
                self.test_statuses.append('failed')
                print(colored(f"Test {test_name} FAILED", 'red'))
                for _, failure in result.failures:
                    print(colored(f"Failure details: {failure}", 'red'))
                    logging.error(f"Test {test_name} FAILED: {failure}")
            if result.errors:
                self.test_results['errors'] += 1
                self.test_statuses.append('error')
                print(colored(f"Test {test_name} ERROR", 'yellow'))
                for _, error in result.errors:
                    print(colored(f"Error details: {error}", 'yellow'))
                    logging.error(f"Test {test_name} ERROR: {error}")

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
        total_time = time.time() - cls.start_time
        print(f"\nTest Summary:")
        print(colored(f"Total Tests: {cls.total_tests}", 'cyan'))
        print(colored(f"Passed: {cls.test_results['passed']}", 'green'))
        print(colored(f"Failed: {cls.test_results['failed']}", 'red'))
        print(colored(f"Errors: {cls.test_results['errors']}", 'yellow'))
        print(f"Total Time: {total_time:.2f} seconds")
        logging.info(
            f"Test Summary: Total={cls.total_tests}, "
            f"Passed={cls.test_results['passed']}, "
            f"Failed={cls.test_results['failed']}, "
            f"Errors={cls.test_results['errors']}, "
            f"Time={total_time:.2f}s"
        )

        labels = ['Passed', 'Failed', 'Errors']
        sizes = [cls.test_results['passed'], cls.test_results['failed'], cls.test_results['errors']]
        colors = ['#00ff00', '#ff0000', '#ffff00']
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=None, colors=colors, autopct='%1.1f%%', startangle=90,
                pctdistance=0.85, labeldistance=1.1)
        plt.legend(labels, loc="best", bbox_to_anchor=(1, 0.5))
        plt.title('DeviceDialog Test Results')
        plt.axis('equal')

        script_dir = os.path.dirname(os.path.abspath(__file__))
        result_dir = os.path.join(script_dir, 'result')
        os.makedirs(result_dir, exist_ok=True)
        output_path = os.path.join(result_dir, 'device_test_results.png')
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(colored(f"Test result pie chart saved as '{output_path}'", 'cyan'))

    def test_setup_ui(self):
        self.assertIsInstance(self.dialog.ui.label, QtWidgets.QLabel)
        self.assertIsInstance(self.dialog.ui.syncButton, QtWidgets.QPushButton)

    @patch('requests.get')
    def test_load_devices_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "success": True,
            "devices": [{"device_id": "dev1", "label": "Device1", "os": "Windows", "ip_address": "192.168.1.1"}]
        }
        self.dialog.set_user_info("http://testserver", "testuser", "dev1", "token")
        self.dialog.load_devices()
        self.assertEqual(self.dialog.ui.listWidget.count(), 1)
        self.assertIn("共找到 1 个设备", self.dialog.ui.statusLabel.text())

    @patch('PyQt5.QtWidgets.QMessageBox.warning')
    def test_confirm_remove_current_device(self, mock_warning):
        self.dialog.device_id = "dev1"
        # 模拟 item.data(QtCore.Qt.UserRole) 返回的 device_info
        mock_item = Mock()
        mock_item.data = Mock(return_value={"device_id": "dev1", "label": "Device1"})
        self.dialog.confirm_remove_device(mock_item)
        QTest.qWait(500)  # 增加等待时间以确保事件处理
        mock_warning.assert_called_with(self.dialog, "提示", "不能删除当前正在使用的设备！")

    @patch('requests.post')
    def test_remove_device_item_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}
        self.dialog.set_user_info("http://testserver", "testuser", "dev2", "token")
        item = QtWidgets.QListWidgetItem()
        item.setData(Qt.UserRole, {"device_id": "dev1", "label": "Device1"})
        self.dialog.ui.listWidget.addItem(item)
        self.dialog.remove_device_item(item)
        mock_post.assert_called_once()
        self.assertEqual(self.dialog.ui.listWidget.count(), 0)
        self.assertIn("设备 'Device1' 已删除", self.dialog.ui.statusLabel.text())

    def test_set_user_info(self):
        self.dialog.set_user_info("http://testserver", "testuser", "dev1", "token")
        self.assertEqual(self.dialog.api_url, "http://testserver")
        self.assertEqual(self.dialog.username, "testuser")
        self.assertEqual(self.dialog.device_id, "dev1")
        self.assertEqual(self.dialog.token, "token")

if __name__ == '__main__':
    unittest.main()
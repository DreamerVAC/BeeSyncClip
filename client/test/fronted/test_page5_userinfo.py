


import unittest
import sys
import time
import logging
import os
from unittest.mock import Mock
from PyQt5 import QtWidgets
from PyQt5.QtTest import QTest  # 用于等待窗口显示
from client.ui.page5_userinfo import UserInfoDialog
from tqdm import tqdm
from termcolor import colored
import matplotlib.pyplot as plt

# 调整模块路径以找到 client.ui
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'ui'))

# 配置日志
logging.basicConfig(
    filename='userinfo_test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestUserInfoDialog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication(sys.argv)  # 初始化 QApplication
        cls.test_results = {'passed': 0, 'failed': 0, 'errors': 0}
        cls.total_tests = 0
        cls.test_names = []
        cls.test_statuses = []
        cls.start_time = time.time()

    def setUp(self):
        self.dialog = UserInfoDialog()
        self.dialog.show()  # 模拟显示窗口
        QTest.qWaitForWindowExposed(self.dialog, 1000)  # 等待窗口显示

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
        plt.title('UserInfoDialog Test Results')
        plt.axis('equal')

        script_dir = os.path.dirname(os.path.abspath(__file__))
        result_dir = os.path.join(script_dir, 'result')
        os.makedirs(result_dir, exist_ok=True)
        output_path = os.path.join(result_dir, 'userinfo_test_results.png')
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(colored(f"Test result pie chart saved as '{output_path}'", 'cyan'))

    def test_setup_ui(self):
        self.assertIsInstance(self.dialog.ui.label_welcome, QtWidgets.QLabel)
        self.assertIsInstance(self.dialog.ui.btn_logout, QtWidgets.QPushButton)

    def test_set_user_info(self):
        self.dialog.set_user_info("testuser", "Device1")
        self.assertEqual(self.dialog.ui.label_welcome.text(), "欢迎回来, testuser")
        self.assertEqual(self.dialog.ui.label_username.text(), "用户名: testuser")
        self.assertEqual(self.dialog.ui.label_device.text(), "当前设备: Device1")

    def test_logout(self):
        mock_callback = Mock()
        self.dialog.logout_requested.connect(mock_callback)
        self.dialog.logout()
        QTest.qWait(500)  # 等待信号触发
        mock_callback.assert_called_once()
        self.assertFalse(self.dialog.isVisible())

if __name__ == '__main__':
    unittest.main()

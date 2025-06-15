


import unittest
import time
import logging
import os
from unittest.mock import patch, Mock
from client.api.http_client import HTTPClient
from client.api.clipboard_api import ClipboardAPI
from tqdm import tqdm
from termcolor import colored
import matplotlib.pyplot as plt


# 配置日志
logging.basicConfig(
    filename='clipboard_api_test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class TestClipboardAPI(unittest.TestCase):
    def setUp(self):
        self.http_client = Mock(spec=HTTPClient)
        self.clipboard_api = ClipboardAPI(self.http_client)

    @classmethod
    def setUpClass(cls):
        cls.test_results = {'passed': 0, 'failed': 0, 'errors': 0}
        cls.total_tests = 0
        cls.test_names = []
        cls.test_statuses = []
        cls.start_time = time.time()  # 将 start_time 移到类级别

    def run(self, result=None):
        """重写 run 方法以添加进度条和可视化"""
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
        """在所有测试完成后显示统计信息和饼图"""
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

        # 绘制饼图，优化标签布局
        labels = ['Passed', 'Failed', 'Errors']
        sizes = [cls.test_results['passed'], cls.test_results['failed'], cls.test_results['errors']]
        colors = ['#00ff00', '#ff0000', '#ffff00']
        plt.figure(figsize=(8, 8))  # 增大图表大小
        plt.pie(sizes, labels=None, colors=colors, autopct='%1.1f%%', startangle=90,
                pctdistance=0.85, labeldistance=1.1)  # 调整百分比和标签距离
        plt.legend(labels, loc="best", bbox_to_anchor=(1, 0.5))  # 将标签移到右侧
        plt.title('ClipboardAPI Test Results')
        plt.axis('equal')  # 确保饼图为圆形

        # 动态构造保存路径并创建 result 目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        result_dir = os.path.join(script_dir, 'result')
        os.makedirs(result_dir, exist_ok=True)  # 创建 result 目录，如果不存在则自动创建
        output_path = os.path.join(result_dir, 'clipboard_api_test_results.png')
        plt.savefig(output_path, bbox_inches='tight')  # 保存到 result 目录
        plt.close()
        print(colored(f"Test result pie chart saved as '{output_path}'", 'cyan'))

    def test_get_clipboards_success(self):
        self.http_client.get.return_value = {
            "success": True,
            "clipboards": [{"clip_id": "clip1", "content": "Hello"}]
        }
        username = "testuser"
        result = self.clipboard_api.get_clipboards(username)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["clipboards"]), 1)
        self.http_client.get.assert_called_with(
            "/get_clipboards",
            params={"username": username}
        )

    def test_get_clipboards_empty_username(self):
        self.http_client.get.return_value = {
            "success": False,
            "message": "Username is required"
        }
        username = ""
        result = self.clipboard_api.get_clipboards(username)
        self.assertFalse(result["success"])
        self.http_client.get.assert_called_with(
            "/get_clipboards",
            params={"username": ""}
        )

    def test_get_clipboards_server_error(self):
        self.http_client.get.return_value = {
            "success": False,
            "message": "Server error",
            "status": 500
        }
        username = "testuser"
        result = self.clipboard_api.get_clipboards(username)
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], 500)

    def test_add_clipboard_success(self):
        self.http_client.post.return_value = {
            "success": True,
            "message": "Clipboard added"
        }
        username = "testuser"
        content = "Test content"
        device_id = "device1"
        content_type = "text/plain"
        result = self.clipboard_api.add_clipboard(username, content, device_id, content_type)
        self.assertTrue(result["success"])
        self.http_client.post.assert_called_with(
            "/add_clipboard",
            {
                "username": username,
                "content": content,
                "device_id": device_id,
                "content_type": content_type
            }
        )

    def test_add_clipboard_empty_content(self):
        self.http_client.post.return_value = {
            "success": False,
            "message": "Content cannot be empty"
        }
        username = "testuser"
        content = ""
        device_id = "device1"
        content_type = "text/plain"
        result = self.clipboard_api.add_clipboard(username, content, device_id, content_type)
        self.assertFalse(result["success"])
        self.http_client.post.assert_called_with(
            "/add_clipboard",
            {
                "username": username,
                "content": content,
                "device_id": device_id,
                "content_type": content_type
            }
        )

    def test_add_clipboard_large_content(self):
        self.http_client.post.return_value = {
            "success": True,
            "message": "Clipboard added"
        }
        username = "testuser"
        content = "x" * 10_000_000
        device_id = "device1"
        content_type = "text/plain"
        result = self.clipboard_api.add_clipboard(username, content, device_id, content_type)
        self.assertTrue(result["success"])
        self.http_client.post.assert_called_with(
            "/add_clipboard",
            {
                "username": username,
                "content": content,
                "device_id": device_id,
                "content_type": content_type
            }
        )

    def test_add_clipboard_unicode_content(self):
        self.http_client.post.return_value = {
            "success": True,
            "message": "Clipboard added"
        }
        username = "testuser"
        content = "Hello 世界 😊"
        device_id = "device1"
        content_type = "text/plain"
        result = self.clipboard_api.add_clipboard(username, content, device_id, content_type)
        self.assertTrue(result["success"])
        self.http_client.post.assert_called_with(
            "/add_clipboard",
            {
                "username": username,
                "content": content,
                "device_id": device_id,
                "content_type": content_type
            }
        )

    def test_add_clipboard_invalid_content_type(self):
        self.http_client.post.return_value = {
            "success": False,
            "message": "Invalid content type"
        }
        username = "testuser"
        content = "Test content"
        device_id = "device1"
        content_type = "invalid/type"
        result = self.clipboard_api.add_clipboard(username, content, device_id, content_type)
        self.assertFalse(result["success"])
        self.http_client.post.assert_called_with(
            "/add_clipboard",
            {
                "username": username,
                "content": content,
                "device_id": device_id,
                "content_type": content_type
            }
        )

    def test_add_clipboard_missing_device_id(self):
        self.http_client.post.return_value = {
            "success": False,
            "message": "Device ID is required"
        }
        username = "testuser"
        content = "Test content"
        device_id = ""
        content_type = "text/plain"
        result = self.clipboard_api.add_clipboard(username, content, device_id, content_type)
        self.assertFalse(result["success"])
        self.http_client.post.assert_called_with(
            "/add_clipboard",
            {
                "username": username,
                "content": content,
                "device_id": device_id,
                "content_type": content_type
            }
        )

    def test_delete_clipboard_success(self):
        self.http_client.post.return_value = {
            "success": True,
            "message": "Clipboard deleted"
        }
        username = "testuser"
        clip_id = "clip1"
        result = self.clipboard_api.delete_clipboard(username, clip_id)
        self.assertTrue(result["success"])
        self.http_client.post.assert_called_with(
            "/delete_clipboard",
            {
                "username": username,
                "clip_id": clip_id
            }
        )

    def test_delete_clipboard_invalid_clip_id(self):
        self.http_client.post.return_value = {
            "success": False,
            "message": "Invalid clip ID"
        }
        username = "testuser"
        clip_id = ""
        result = self.clipboard_api.delete_clipboard(username, clip_id)
        self.assertFalse(result["success"])
        self.http_client.post.assert_called_with(
            "/delete_clipboard",
            {
                "username": username,
                "clip_id": clip_id
            }
        )

    def test_delete_clipboard_nonexistent_clip(self):
        self.http_client.post.return_value = {
            "success": False,
            "message": "Clipboard not found",
            "status": 404
        }
        username = "testuser"
        clip_id = "nonexistent_clip"
        result = self.clipboard_api.delete_clipboard(username, clip_id)
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], 404)
        self.http_client.post.assert_called_with(
            "/delete_clipboard",
            {
                "username": username,
                "clip_id": clip_id
            }
        )

    def test_clear_clipboards_success(self):
        self.http_client.post.return_value = {
            "success": True,
            "message": "Clipboards cleared"
        }
        username = "testuser"
        result = self.clipboard_api.clear_clipboards(username)
        self.assertTrue(result["success"])
        self.http_client.post.assert_called_with(
            "/clear_clipboards",
            {
                "username": username
            }
        )

    def test_clear_clipboards_empty_username(self):
        self.http_client.post.return_value = {
            "success": False,
            "message": "Username is required"
        }
        username = ""
        result = self.clipboard_api.clear_clipboards(username)
        self.assertFalse(result["success"])
        self.http_client.post.assert_called_with(
            "/clear_clipboards",
            {
                "username": username
            }
        )

    def test_clear_clipboards_no_clipboards(self):
        self.http_client.post.return_value = {
            "success": True,
            "message": "No clipboards to clear"
        }
        username = "testuser"
        result = self.clipboard_api.clear_clipboards(username)
        self.assertTrue(result["success"])
        self.http_client.post.assert_called_with(
            "/clear_clipboards",
            {
                "username": username
            }
        )

    @patch('requests.Session.post')
    def test_add_clipboard_non_json_response(self, mock_post):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.side_effect = Exception("Server error")
        mock_post.return_value = mock_response
        # 模拟 HTTPClient 的 _handle_response 返回值
        self.http_client.post.return_value = {
            "success": False,
            "message": "HTTP错误: Server error",
            "status": 500
        }
        username = "testuser"
        content = "Test content"
        device_id = "device1"
        content_type = "text/plain"

        # Act
        result = self.clipboard_api.add_clipboard(username, content, device_id, content_type)

        # Assert
        self.assertFalse(result["success"])
        self.assertIn("HTTP错误", result["message"])
        self.assertEqual(result["status"], 500)


if __name__ == '__main__':
    unittest.main()

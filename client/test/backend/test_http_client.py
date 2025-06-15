import unittest
import time
import logging
import os
from unittest.mock import patch, Mock
from client.api.http_client import HTTPClient
from tqdm import tqdm
from termcolor import colored
import matplotlib.pyplot as plt


# 配置日志
logging.basicConfig(
    filename='http_client_test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class TestHTTPClient(unittest.TestCase):
    def setUp(self):
        self.client = HTTPClient(base_url="http://testserver")

    @classmethod
    def setUpClass(cls):
        cls.test_results = {'passed': 0, 'failed': 0, 'errors': 0}
        cls.total_tests = 0
        cls.test_names = []
        cls.test_statuses = []
        cls.start_time = time.time()

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
        plt.title('HTTPClient Test Results')
        plt.axis('equal')

        script_dir = os.path.dirname(os.path.abspath(__file__))
        result_dir = os.path.join(script_dir, 'result')
        os.makedirs(result_dir, exist_ok=True)
        output_path = os.path.join(result_dir, 'http_client_test_results.png')
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(colored(f"Test result pie chart saved as '{output_path}'", 'cyan'))

    @patch('requests.Session.get')
    def test_get_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": "test"}
        mock_get.return_value = mock_response

        result = self.client.get("/test_endpoint", params={"key": "value"})

        self.assertTrue(result["success"])
        self.assertEqual(result["data"], "test")
        mock_get.assert_called_with(
            "http://testserver/test_endpoint",
            params={"key": "value"},
            timeout=30
        )

    @patch('requests.Session.post')
    def test_post_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"success": True, "message": "created"}
        mock_post.return_value = mock_response
        data = {"key": "value"}

        result = self.client.post("/create", data)

        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "created")
        mock_post.assert_called_with(
            "http://testserver/create",
            json=data,
            timeout=30
        )

    @patch('requests.Session.get')
    def test_get_http_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.side_effect = ValueError
        mock_response.raise_for_status.side_effect = Exception("Not Found")
        mock_get.return_value = mock_response

        result = self.client.get("/not_found")

        self.assertFalse(result["success"])
        self.assertIn("请求失败", result["message"])
        self.assertEqual(result["status"], 0)

    def test_set_auth_token(self):
        self.client.set_auth_token("test_token")
        self.assertEqual(
            self.client.session.headers["Authorization"],
            "Bearer test_token"
        )

    def test_clear_auth_token(self):
        self.client.set_auth_token("test_token")
        self.client.clear_auth_token()
        self.assertNotIn("Authorization", self.client.session.headers)


if __name__ == '__main__':
    unittest.main()

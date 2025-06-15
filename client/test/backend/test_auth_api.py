import unittest
import time
import logging
import os
from unittest.mock import patch, Mock
from client.api.http_client import HTTPClient
from client.api.auth_api import AuthAPI
from tqdm import tqdm
from termcolor import colored
import matplotlib.pyplot as plt


# 配置日志
logging.basicConfig(
    filename='auth_api_test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class TestAuthAPI(unittest.TestCase):
    def setUp(self):
        self.http_client = Mock(spec=HTTPClient)
        self.auth_api = AuthAPI(self.http_client)

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
        plt.title('AuthAPI Test Results')
        plt.axis('equal')

        script_dir = os.path.dirname(os.path.abspath(__file__))
        result_dir = os.path.join(script_dir, 'result')
        os.makedirs(result_dir, exist_ok=True)
        output_path = os.path.join(result_dir, 'auth_api_test_results.png')
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(colored(f"Test result pie chart saved as '{output_path}'", 'cyan'))

    def test_login_success(self):
        self.http_client.post.return_value = {"success": True, "token": "test_token"}
        username = "testuser"
        password = "testpass"
        device_info = {"device_id": "device1"}

        result = self.auth_api.login(username, password, device_info)

        self.assertTrue(result["success"])
        self.assertEqual(result["token"], "test_token")
        self.http_client.post.assert_called_with(
            "/login",
            {
                "username": username,
                "password": password,
                "device_info": device_info
            }
        )

    def test_register_success(self):
        self.http_client.post.return_value = {"success": True, "message": "User registered"}
        username = "newuser"
        password = "newpass"

        result = self.auth_api.register(username, password)

        self.assertTrue(result["success"])
        self.http_client.post.assert_called_with(
            "/register",
            {
                "username": username,
                "password": password
            }
        )

    def test_logout(self):
        result = self.auth_api.logout()

        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "已登出")
        self.http_client.clear_auth_token.assert_called_once()

    def test_set_token(self):
        self.auth_api.set_token("new_token")

        self.http_client.set_auth_token.assert_called_with("new_token")


if __name__ == '__main__':
    unittest.main()

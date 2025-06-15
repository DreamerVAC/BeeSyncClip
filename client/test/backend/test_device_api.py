import unittest
import time
import logging
import os
from unittest.mock import patch, Mock
from client.api.http_client import HTTPClient
from client.api.device_api import DeviceAPI
from tqdm import tqdm
from termcolor import colored
import matplotlib.pyplot as plt


# 配置日志
logging.basicConfig(
    filename='device_api_test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class TestDeviceAPI(unittest.TestCase):
    def setUp(self):
        self.http_client = Mock(spec=HTTPClient)
        self.device_api = DeviceAPI(self.http_client)

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
        plt.title('DeviceAPI Test Results')
        plt.axis('equal')

        script_dir = os.path.dirname(os.path.abspath(__file__))
        result_dir = os.path.join(script_dir, 'result')
        os.makedirs(result_dir, exist_ok=True)
        output_path = os.path.join(result_dir, 'device_api_test_results.png')
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(colored(f"Test result pie chart saved as '{output_path}'", 'cyan'))

    def test_get_devices(self):
        self.http_client.get.return_value = {
            "success": True,
            "devices": [{"device_id": "device1", "label": "Test Device"}]
        }
        username = "testuser"

        result = self.device_api.get_devices(username)

        self.assertTrue(result["success"])
        self.assertEqual(len(result["devices"]), 1)
        self.http_client.get.assert_called_with(
            "/get_devices",
            params={"username": username}
        )

    def test_update_device_label(self):
        self.http_client.post.return_value = {
            "success": True,
            "message": "Label updated"
        }
        username = "testuser"
        device_id = "device1"
        new_label = "New Label"

        result = self.device_api.update_device_label(username, device_id, new_label)

        self.assertTrue(result["success"])
        self.http_client.post.assert_called_with(
            "/update_device_label",
            {
                "username": username,
                "device_id": device_id,
                "new_label": new_label
            }
        )

    def test_remove_device(self):
        self.http_client.post.return_value = {
            "success": True,
            "message": "Device removed"
        }
        username = "testuser"
        device_id = "device1"

        result = self.device_api.remove_device(username, device_id)

        self.assertTrue(result["success"])
        self.http_client.post.assert_called_with(
            "/remove_device",
            {
                "username": username,
                "device_id": device_id
            }
        )


if __name__ == '__main__':
    unittest.main()

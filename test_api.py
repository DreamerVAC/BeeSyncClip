#!/usr/bin/env python3
"""
BeeSyncClip API 测试脚本
"""

import requests
import json
from datetime import datetime
import time

def test_api_endpoint(url, endpoint, method='GET', data=None, headers=None):
    """测试API端点"""
    full_url = f"{url}{endpoint}"
    print(f"\n{'='*50}")
    print(f"测试: {method} {full_url}")
    print(f"时间: {datetime.now()}")
    
    try:
        if method == 'GET':
            response = requests.get(full_url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(full_url, json=data, headers=headers, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.text:
            try:
                json_data = response.json()
                print(f"JSON响应: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"文本响应: {response.text[:500]}")
        else:
            print("空响应")
            
        return response
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")
    
    return None

def main():
    server_url = "http://47.110.154.99:8000"
    
    print("🚀 BeeSyncClip API 测试开始")
    print(f"服务器地址: {server_url}")
    
    # 测试根路径
    test_api_endpoint(server_url, "/")
    
    # 测试健康检查
    test_api_endpoint(server_url, "/health")
    
    # 测试API文档
    test_api_endpoint(server_url, "/docs")
    
    # 生成唯一用户名
    unique_username = f"testuser_{int(time.time())}"
    
    # 测试注册接口
    register_data = {
        "username": unique_username,
        "password": "test123",
        "email": f"{unique_username}@example.com"
    }
    test_api_endpoint(server_url, "/register", method='POST', data=register_data)
    
    # 测试登录接口
    login_data = {
        "username": unique_username,
        "password": "test123",
        "device_info": {
            "device_id": "test_device_123",
            "device_name": "Test Device",
            "platform": "Test Platform",
            "version": "1.0.0"
        }
    }
    test_api_endpoint(server_url, "/login", method='POST', data=login_data)
    
    print("\n✅ API 测试完成")

if __name__ == "__main__":
    main() 
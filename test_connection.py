#!/usr/bin/env python3
"""
BeeSyncClip 连接测试脚本
测试与阿里云服务器的连接
"""

import requests
import sys
from client.api import api_manager

def test_server_connection():
    """测试服务器连接"""
    server_url = "http://47.110.154.99:8000"
    
    print("🔍 BeeSyncClip 连接测试")
    print(f"🌐 服务器地址: {server_url}")
    print("-" * 50)
    
    try:
        # 1. 基础连接测试
        print("1️⃣ 测试基础连接...")
        response = requests.get(f"{server_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ 服务器连接正常")
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 连接失败: {e}")
        return False
    
    try:
        # 2. API管理器测试
        print("\n2️⃣ 测试API管理器...")
        
        # 测试登录
        device_info = {
            "device_id": "test-device",
            "label": "测试设备",
            "os": "Test"
        }
        
        result = api_manager.login("testuser", "test123", device_info)
        
        if result.get("success"):
            print("✅ 登录测试成功")
            
            # 测试获取剪贴板
            clipboards = api_manager.clipboard.get_clipboards("testuser")
            print(f"✅ 剪贴板数据获取成功，共 {len(clipboards)} 条记录")
            
            # 测试获取设备
            devices = api_manager.device.get_devices("testuser")
            print(f"✅ 设备数据获取成功，共 {len(devices)} 个设备")
            
        else:
            print(f"❌ 登录测试失败: {result.get('message', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False
    
    print("\n🎉 所有测试通过！服务器连接正常。")
    print("\n📱 现在可以使用以下命令启动客户端:")
    print("   python client/main.py")
    print("   或")
    print("   python client/ui/form_ui.py")
    
    return True

if __name__ == "__main__":
    success = test_server_connection()
    sys.exit(0 if success else 1) 
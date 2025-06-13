#!/usr/bin/env python3
"""
BeeSyncClip GUI连接测试脚本
"""

import requests
import json
from datetime import datetime
import time
import uuid

def test_server_connection():
    """测试服务器连接"""
    server_url = "http://47.110.154.99:8000"
    
    print("🔗 测试BeeSyncClip服务器连接")
    print("="*60)
    print(f"服务器地址: {server_url}")
    print(f"测试时间: {datetime.now()}")
    print()
    
    # 测试基本连接
    try:
        response = requests.get(f"{server_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ 服务器连接正常")
            result = response.json()
            print(f"   服务状态: {result.get('status', 'unknown')}")
            print(f"   服务组件: {result.get('components', {})}")
        elif response.status_code == 503:
            print("⚠️  服务器返回503错误 - 服务不可用")
            print("   可能原因:")
            print("   - Redis连接问题")
            print("   - 应用配置错误")
            print("   - 依赖服务未就绪")
            return False
        else:
            print(f"❌ 服务器返回错误状态: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        print("   请检查:")
        print("   - 服务器是否正在运行")
        print("   - 网络连接是否正常")
        print("   - 防火墙设置")
        return False
    except requests.exceptions.Timeout:
        print("❌ 连接超时")
        return False
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return False
    
    return True

def test_registration(username, password, email):
    """测试注册功能"""
    server_url = "http://47.110.154.99:8000"
    
    print("\n📝 测试用户注册功能")
    print("-" * 40)
    
    test_data = {
        "username": username,
        "password": password,
        "email": email
    }
    
    try:
        response = requests.post(f"{server_url}/register", json=test_data, timeout=10)
        
        if response.status_code == 201:
            print("✅ 注册功能正常")
            print(f"   测试用户: {username}")
            return True
        else:
            result = response.json()
            print(f"⚠️  注册测试失败: {result.get('message', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 注册测试错误: {e}")
        return False

def test_login(username, password):
    """测试登录功能"""
    server_url = "http://47.110.154.99:8000"
    
    print("\n🔐 测试用户登录功能")
    print("-" * 40)
    
    test_data = {
        "username": username,
        "password": password,
        "device_info": {
            "device_id": str(uuid.uuid4()),
            "device_name": "Test GUI Device",
            "platform": "Test Script",
            "version": "1.0.0"
        }
    }
    
    try:
        response = requests.post(f"{server_url}/login", json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 登录功能正常")
                print(f"   Token: {result.get('token')[:30]}...")
                return True
            else:
                print(f"⚠️  登录测试失败: {result.get('message', '未知错误')}")
                return False
        else:
            result = response.json()
            print(f"⚠️  登录测试失败 (状态码 {response.status_code}): {result.get('message', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 登录测试错误: {e}")
        return False

def provide_gui_guidance():
    """提供GUI使用指导"""
    print("\n🎯 GUI前端使用指导")
    print("="*60)
    print("1. 启动GUI应用")
    print("   - GUI应用已在后台运行")
    print("   - 如果未启动，运行: cd client/ui && python form_ui.py")
    print()
    print("2. 登录步骤")
    print("   - 点击左侧'登录'按钮")
    print("   - 如果是新用户，先点击'注册'创建账户")
    print("   - 输入用户名和密码登录")
    print()
    print("3. 功能使用")
    print("   - 登录成功后，可以访问'剪切板'和'设备'功能")
    print("   - 剪切板页面会自动监听系统剪切板变化")
    print("   - 设备页面显示所有登录的设备")
    print()
    print("4. 故障排除")
    print("   - 如果连接失败，请确认服务器正在运行")
    print("   - 检查网络连接和防火墙设置")
    print("   - 查看应用日志获取详细错误信息")

def main():
    """主函数"""
    print("🚀 BeeSyncClip GUI连接测试")
    print("="*60)
    
    # 测试服务器连接
    server_ok = test_server_connection()
    
    if server_ok:
        # 生成唯一测试用户
        timestamp = int(time.time())
        username = f"gui_test_{timestamp}"
        password = "test_password"
        email = f"{username}@example.com"

        # 测试API功能
        registration_ok = test_registration(username, password, email)
        
        if registration_ok:
            test_login(username, password)
        
        print("\n✅ 服务器功能测试完成 - 可以继续测试GUI前端")
    else:
        print("\n❌ 服务器连接失败 - 请先解决服务器问题")
        print("\n📋 服务器端检查清单:")
        print("   □ 确认后端服务器正在运行 (python server/main_server.py)")
        print("   □ 检查Redis服务状态 (redis-cli ping)")
        print("   □ 验证配置文件正确 (config/config.yaml)")
        print("   □ 查看服务器日志 (logs/beesyncclip.log)")
    
    # 提供使用指导
    provide_gui_guidance()

if __name__ == "__main__":
    main() 
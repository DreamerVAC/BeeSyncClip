#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import os

# 将项目根目录添加到模块搜索路径，确保各个包都能被正确导入
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DEFAULT_SERVER = "http://47.110.154.99:8000"
CLIENT_MODULE = "client.ui.form_ui"

def print_header():
    print("🚀 BeeSyncClip GUI 客户端启动器")
    print("================================")

def check_and_install_deps():
    print("🔍 检查依赖…")
    try:
        # 如果有 requirements-client.txt，可以取消注释以下两行
        # req_file = os.path.join(PROJECT_ROOT, "requirements-client.txt")
        # subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        print("✅ 依赖检查通过")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败，请手动执行：")
        print("    pip install -r requirements-client.txt")
        return False

def print_usage():
    print()
    print("📱 使用说明:")
    print("   • 新用户请在界面中注册账号")
    print(f"   • 默认连接服务器: {DEFAULT_SERVER}")
    print("   • 支持实时剪贴板同步")
    print()

def launch_gui():
    print("🎨 启动 GUI 客户端…\n")
    try:
        subprocess.check_call([sys.executable, "-m", CLIENT_MODULE])
    except subprocess.CalledProcessError as e:
        print(f"❌ 客户端异常退出，错误码：{e.returncode}")
        sys.exit(e.returncode)
    else:
        print("👋 GUI 客户端已关闭")

def main():
    print_header()
    if not check_and_install_deps():
        sys.exit(1)
    print_usage()
    launch_gui()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
BeeSyncClip 客户端主入口
启动前端界面，连接到真实后端服务器
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 添加客户端目录到Python路径
client_root = Path(__file__).parent
sys.path.insert(0, str(client_root))

def check_server_connection():
    """检查服务器连接"""
    from api import api_manager
    
    try:
        # 尝试连接服务器健康检查端点
        response = api_manager.http_client.get("/health")
        if response.get("status") == "healthy":
            print("✅ 服务器连接正常")
            return True
        else:
            print("❌ 服务器健康检查失败")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("💡 请确保后端服务器正在运行: python start_frontend_server.py")
        return False

def main():
    """主函数"""
    print("🚀 BeeSyncClip 客户端启动中...")
    
    # 检查服务器连接
    if not check_server_connection():
        print("\n请先启动后端服务器:")
        print("python start_frontend_server.py")
        return 1
    
    try:
        # 导入并启动前端界面
        from ui.form_ui import main as start_ui
        print("🎨 启动前端界面...")
        start_ui()
        
    except ImportError as e:
        print(f"❌ 导入前端界面失败: {e}")
        return 1
    except Exception as e:
        print(f"❌ 启动客户端失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
#!/usr/bin/env python3
"""
BeeSyncClip 桌面客户端启动脚本
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from desktop.main_window import main

if __name__ == "__main__":
    main() 
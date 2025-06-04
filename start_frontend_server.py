#!/usr/bin/env python3
"""
启动BeeSyncClip前端兼容服务器
替换Mock服务器，使用真实后端逻辑但保持相同的API接口
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loguru import logger
from server.redis_manager import redis_manager
from server.auth import auth_manager


def check_dependencies():
    """检查依赖服务"""
    logger.info("🔍 检查系统依赖...")
    
    # 检查Redis连接
    if not redis_manager.is_connected():
        logger.error("❌ Redis连接失败！请确保Redis服务正在运行")
        logger.info("💡 启动Redis: brew services start redis (macOS) 或 sudo systemctl start redis (Linux)")
        return False
    
    logger.info("✅ Redis连接正常")
    
    # 初始化测试用户
    try:
        test_user = auth_manager.register_user("testuser", "test123")
        if test_user:
            logger.info("✅ 测试用户创建成功")
        else:
            logger.info("ℹ️ 测试用户已存在")
    except Exception as e:
        logger.warning(f"测试用户创建警告: {e}")
    
    return True


def main():
    """主函数"""
    logger.info("🚀 BeeSyncClip 前端兼容服务器启动中...")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 启动服务器
    try:
        import uvicorn
        from server.frontend_compatible_server import app
        
        logger.info("🌐 服务器信息:")
        logger.info("   地址: http://47.110.154.99:8000")
        logger.info("   测试账号: testuser")
        logger.info("   测试密码: test123")
        logger.info("📱 现在可以使用前端界面连接到真实后端服务器！")
        
        # 启动uvicorn服务器
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=False
        )
        
    except KeyboardInterrupt:
        logger.info("👋 服务器已停止")
    except Exception as e:
        logger.error(f"❌ 服务器启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
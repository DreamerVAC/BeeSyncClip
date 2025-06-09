#!/usr/bin/env python3
"""
启动BeeSyncClip模块化服务器
支持加密、JWT认证、速率限制等安全功能
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loguru import logger
from server.redis_manager import redis_manager


def check_dependencies():
    """检查依赖服务"""
    logger.info("🔍 检查系统依赖...")
    
    # 检查Redis连接
    if not redis_manager.is_connected():
        logger.error("❌ Redis连接失败！请确保Redis服务正在运行")
        logger.info("💡 启动Redis: brew services start redis (macOS) 或 sudo systemctl start redis (Linux)")
        return False
    
    logger.info("✅ Redis连接正常")
    
    return True


def main():
    """主函数"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                BeeSyncClip 模块化服务器 v2.0                  ║
    ║                                                              ║
    ║  🔐 AES-256 加密    🎫 JWT 认证    🛡️ 安全中间件             ║
    ║  🌐 WebSocket 同步  📊 速率限制    📱 跨平台支持             ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    logger.info("🚀 BeeSyncClip 模块化服务器启动中...")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 启动服务器
    try:
        import uvicorn
        from server.modular_server import app
        
        logger.info("🌐 服务器信息:")
        logger.info("   地址: http://47.110.154.99:8000")
        logger.info("   API文档: http://47.110.154.99:8000/docs")
        logger.info("   健康检查: http://47.110.154.99:8000/health")
        logger.info("   安全信息: http://47.110.154.99:8000/security/info")
        logger.info("📱 新用户请在客户端界面进行注册")
        logger.info("🔐 所有数据传输均已加密")
        
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
"""
BeeSyncClip 主服务器启动脚本
"""

import asyncio
import uvicorn
from multiprocessing import Process
from loguru import logger
from datetime import datetime

from shared.utils import config_manager
from server.redis_manager import redis_manager
from server.websocket_server import start_websocket_server
from server.api_server import app


def setup_logging():
    """配置日志系统"""
    logger.add(
        config_manager.get('logging.file_path', 'logs/beesyncclip.log'),
        rotation=config_manager.get('logging.file_rotation', '10 MB'),
        retention=config_manager.get('logging.file_retention', '30 days'),
        level=config_manager.get('logging.level', 'INFO'),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )


def start_api_server():
    """启动HTTP API服务器"""
    host = config_manager.get('api.host', '0.0.0.0')  # 阿里云使用0.0.0.0
    port = config_manager.get('api.port', 8000)
    
    logger.info(f"启动 API 服务器: {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=config_manager.get('logging.level', 'info').lower(),
        access_log=True
    )


async def start_websocket_server_async():
    """启动WebSocket服务器（异步）"""
    server = await start_websocket_server()
    await server.wait_closed()


def start_websocket_server_process():
    """启动WebSocket服务器进程"""
    logger.info("启动 WebSocket 服务器进程")
    asyncio.run(start_websocket_server_async())


def check_dependencies():
    """检查依赖服务"""
    logger.info("检查服务依赖...")
    
    # 检查Redis连接
    if not redis_manager.connect():
        logger.error("Redis连接失败，无法启动服务")
        return False
    
    logger.info(f"Redis连接成功: {redis_manager.redis_client.ping()}")
    
    # 检查配置文件
    required_configs = [
        'redis.host',
        'websocket.host',
        'websocket.port',
        'api.host',
        'api.port'
    ]
    
    for config_key in required_configs:
        if not config_manager.get(config_key):
            logger.error(f"缺少必要配置: {config_key}")
            return False
    
    logger.info("所有依赖检查通过")
    return True


def create_deployment_info():
    """创建部署信息文件"""
    try:
        deployment_info = {
            "service_name": "BeeSyncClip",
            "version": config_manager.get('app.version', '1.0.0'),
            "deployment_time": datetime.now().isoformat(),
            "api_endpoint": f"http://{config_manager.get('api.host')}:{config_manager.get('api.port')}",
            "websocket_endpoint": f"ws://{config_manager.get('websocket.host')}:{config_manager.get('websocket.port')}",
            "environment": "production" if config_manager.get('api.host') != 'localhost' else "development"
        }
        
        import json
        with open('deployment.json', 'w', encoding='utf-8') as f:
            json.dump(deployment_info, f, indent=2, ensure_ascii=False)
        
        logger.info("部署信息文件已创建: deployment.json")
        
    except Exception as e:
        logger.warning(f"创建部署信息文件失败: {e}")


def main():
    """主启动函数"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                     BeeSyncClip 服务器                        ║
    ║                  跨平台同步剪切板应用                          ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 设置日志
    setup_logging()
    logger.info("BeeSyncClip 服务器启动中...")
    
    # 检查依赖
    if not check_dependencies():
        logger.error("依赖检查失败，服务器退出")
        return
    
    # 创建部署信息
    create_deployment_info()
    
    try:
        # 启动WebSocket服务器进程
        ws_process = Process(target=start_websocket_server_process)
        ws_process.start()
        logger.info(f"WebSocket 服务器进程已启动 (PID: {ws_process.pid})")
        
        # 在主进程中启动API服务器
        logger.info("启动 API 服务器...")
        start_api_server()
        
    except KeyboardInterrupt:
        logger.info("接收到中断信号，正在关闭服务器...")
        
        # 终止WebSocket进程
        if 'ws_process' in locals() and ws_process.is_alive():
            ws_process.terminate()
            ws_process.join(timeout=5)
            if ws_process.is_alive():
                ws_process.kill()
            logger.info("WebSocket 服务器进程已关闭")
        
        logger.info("服务器已关闭")
        
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        
        # 清理进程
        if 'ws_process' in locals() and ws_process.is_alive():
            ws_process.terminate()
            ws_process.join()
    
    finally:
        # 关闭Redis连接
        if redis_manager.is_connected():
            redis_manager.close()
            logger.info("Redis连接已关闭")


if __name__ == "__main__":
    main() 
"""
BeeSyncClip API 模块
包含所有的API路由和控制器
"""

from .auth_routes import auth_router
from .clipboard_routes import clipboard_router
from .device_routes import device_router
from .websocket_routes import websocket_router

__all__ = ['auth_router', 'clipboard_router', 'device_router', 'websocket_router'] 
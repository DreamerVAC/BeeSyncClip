"""
BeeSyncClip Client API Package
客户端API通信层
"""

from .http_client import HTTPClient
from .clipboard_api import ClipboardAPI
from .auth_api import AuthAPI
from .device_api import DeviceAPI
from .api_manager import APIManager, api_manager

__all__ = [
    'HTTPClient', 
    'ClipboardAPI', 
    'AuthAPI', 
    'DeviceAPI', 
    'APIManager',
    'api_manager'  # 全局API管理器实例
] 
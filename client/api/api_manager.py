"""
BeeSyncClip API管理器
统一管理所有API客户端
"""

from typing import Optional
from .http_client import HTTPClient
from .auth_api import AuthAPI
from .device_api import DeviceAPI
from .clipboard_api import ClipboardAPI


class APIManager:
    """API管理器 - 统一的API访问入口"""
    
    def __init__(self, base_url: str = "http://47.110.154.99:8000"):
        """
        API管理器
        
        Args:
            base_url: 服务器基础URL
        """
        # 创建HTTP客户端
        self.http_client = HTTPClient(base_url)
        
        # 创建各个API客户端
        self.auth = AuthAPI(self.http_client)
        self.device = DeviceAPI(self.http_client)
        self.clipboard = ClipboardAPI(self.http_client)
        
        # 用户状态
        self.current_user: Optional[str] = None
        self.current_token: Optional[str] = None
        self.current_device_id: Optional[str] = None
    
    def set_server_url(self, url: str):
        """设置服务器URL"""
        self.http_client.base_url = url.rstrip('/')
    
    def login(self, username: str, password: str, device_info: dict) -> dict:
        """用户登录"""
        result = self.auth.login(username, password, device_info)
        
        if result.get("success"):
            self.current_user = username
            self.current_token = result.get("token")
            self.current_device_id = device_info.get("device_id")
            
            # 设置认证令牌
            if self.current_token:
                self.auth.set_token(self.current_token)
        
        return result
    
    def logout(self) -> dict:
        """用户登出"""
        result = self.auth.logout()
        
        # 清除用户状态
        self.current_user = None
        self.current_token = None
        self.current_device_id = None
        
        return result
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.current_user is not None and self.current_token is not None
    
    def get_current_user(self) -> Optional[str]:
        """获取当前用户名"""
        return self.current_user
    
    def get_current_device_id(self) -> Optional[str]:
        """获取当前设备ID"""
        return self.current_device_id


# 全局API管理器实例
api_manager = APIManager() 
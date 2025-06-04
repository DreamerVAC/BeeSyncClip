"""
BeeSyncClip 认证API客户端
"""

from typing import Dict, Any
from .http_client import HTTPClient


class AuthAPI:
    """认证API客户端"""
    
    def __init__(self, http_client: HTTPClient):
        self.client = http_client
    
    def login(self, username: str, password: str, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """用户登录"""
        data = {
            "username": username,
            "password": password,
            "device_info": device_info
        }
        return self.client.post("/login", data)
    
    def register(self, username: str, password: str) -> Dict[str, Any]:
        """用户注册"""
        data = {
            "username": username,
            "password": password
        }
        return self.client.post("/register", data)
    
    def logout(self) -> Dict[str, Any]:
        """用户登出"""
        self.client.clear_auth_token()
        return {"success": True, "message": "已登出"}
    
    def set_token(self, token: str):
        """设置认证令牌"""
        self.client.set_auth_token(token) 
"""
BeeSyncClip HTTP客户端
与前端兼容服务器通信的基础类
"""

import requests
import json
from typing import Dict, Any, Optional
from urllib.parse import urljoin


class HTTPClient:
    """HTTP客户端基础类"""
    
    def __init__(self, base_url: str = "http://47.110.154.99:8000"):
        """
        初始化HTTP客户端
        
        Args:
            base_url: 服务器基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # 设置超时时间
        self.timeout = 30
        
        # 设置请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'BeeSyncClip-Client/1.0'
        })
    
    def _make_url(self, endpoint: str) -> str:
        """构造完整URL"""
        return urljoin(self.base_url + '/', endpoint.lstrip('/'))
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """处理HTTP响应"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # 尝试解析错误响应
            try:
                error_data = response.json()
                return error_data
            except:
                return {
                    "success": False,
                    "message": f"HTTP错误: {e}",
                    "status": response.status_code
                }
        except json.JSONDecodeError:
            return {
                "success": False,
                "message": "服务器响应格式错误",
                "status": response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"请求失败: {str(e)}",
                "status": 0
            }
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送GET请求"""
        url = self._make_url(endpoint)
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            return {
                "success": False,
                "message": f"GET请求失败: {str(e)}",
                "status": 0
            }
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送POST请求"""
        url = self._make_url(endpoint)
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            return {
                "success": False,
                "message": f"POST请求失败: {str(e)}",
                "status": 0
            }
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送PUT请求"""
        url = self._make_url(endpoint)
        try:
            response = self.session.put(url, json=data, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            return {
                "success": False,
                "message": f"PUT请求失败: {str(e)}",
                "status": 0
            }
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """发送DELETE请求"""
        url = self._make_url(endpoint)
        try:
            response = self.session.delete(url, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            return {
                "success": False,
                "message": f"DELETE请求失败: {str(e)}",
                "status": 0
            }
    
    def set_auth_token(self, token: str):
        """设置认证令牌"""
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
    
    def clear_auth_token(self):
        """清除认证令牌"""
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization'] 
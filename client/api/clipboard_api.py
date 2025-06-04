"""
BeeSyncClip 剪贴板API客户端
"""

from typing import Dict, Any, Optional
from .http_client import HTTPClient


class ClipboardAPI:
    """剪贴板API客户端"""
    
    def __init__(self, http_client: HTTPClient):
        self.client = http_client
    
    def get_clipboards(self, username: str) -> Dict[str, Any]:
        """获取用户剪贴板内容"""
        return self.client.get("/get_clipboards", params={"username": username})
    
    def add_clipboard(self, username: str, content: str, device_id: str, 
                     content_type: str = "text/plain") -> Dict[str, Any]:
        """添加剪贴板内容"""
        data = {
            "username": username,
            "content": content,
            "device_id": device_id,
            "content_type": content_type
        }
        return self.client.post("/add_clipboard", data)
    
    def delete_clipboard(self, username: str, clip_id: str) -> Dict[str, Any]:
        """删除剪贴板内容"""
        data = {
            "username": username,
            "clip_id": clip_id
        }
        return self.client.post("/delete_clipboard", data)
    
    def clear_clipboards(self, username: str) -> Dict[str, Any]:
        """清空所有剪贴板内容"""
        data = {
            "username": username
        }
        return self.client.post("/clear_clipboards", data) 
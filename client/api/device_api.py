"""
BeeSyncClip 设备API客户端
"""

from typing import Dict, Any, List
from .http_client import HTTPClient


class DeviceAPI:
    """设备API客户端"""
    
    def __init__(self, http_client: HTTPClient):
        self.client = http_client
    
    def get_devices(self, username: str) -> Dict[str, Any]:
        """获取用户设备列表"""
        return self.client.get("/get_devices", params={"username": username})
    
    def update_device_label(self, username: str, device_id: str, new_label: str) -> Dict[str, Any]:
        """更新设备标签"""
        data = {
            "username": username,
            "device_id": device_id,
            "new_label": new_label
        }
        return self.client.post("/update_device_label", data)
    
    def remove_device(self, username: str, device_id: str) -> Dict[str, Any]:
        """删除设备"""
        data = {
            "username": username,
            "device_id": device_id
        }
        return self.client.post("/remove_device", data) 
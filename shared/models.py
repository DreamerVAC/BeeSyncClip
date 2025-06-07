"""
BeeSyncClip 数据模型定义
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import uuid


class ClipboardType(str, Enum):
    """剪切板内容类型"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    HTML = "html"
    RTF = "rtf"


class ClipboardItem(BaseModel):
    """剪切板项模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: ClipboardType
    content: str  # 内容或base64编码的数据
    metadata: Dict[str, Any] = Field(default_factory=dict)  # 元数据
    size: int = 0  # 数据大小（字节）
    created_at: datetime = Field(default_factory=datetime.now)
    device_id: str
    user_id: str
    checksum: Optional[str] = None  # 数据校验和
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Device(BaseModel):
    """设备模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    os_info: str  # e.g., "macOS 12.4" or "Windows 11"
    ip_address: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_seen: datetime = Field(default_factory=datetime.now)
    is_online: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class User(BaseModel):
    """用户模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: Optional[str] = None
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    devices: List[Device] = Field(default_factory=list)
    total_clips: int = 0  # 用户剪贴板总数
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SyncEvent(BaseModel):
    """同步事件模型"""
    event_type: str  # created, updated, deleted
    clipboard_item: ClipboardItem
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WebSocketMessage(BaseModel):
    """WebSocket消息模型"""
    type: str  # sync, auth, ping, pong, error
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AuthRequest(BaseModel):
    """认证请求模型"""
    username: str
    password: str
    device_info: Dict[str, str]


class AuthResponse(BaseModel):
    """认证响应模型"""
    success: bool
    token: Optional[str] = None
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    message: str = ""


class ClipboardHistory(BaseModel):
    """剪切板历史模型"""
    items: List[ClipboardItem]
    total: int
    page: int = 1
    per_page: int = 50 
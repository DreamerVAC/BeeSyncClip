"""
BeeSyncClip 用户认证模块
"""

import jwt
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from loguru import logger

from shared.models import User, Device, AuthRequest, AuthResponse
from shared.utils import config_manager, get_device_info
from server.redis_manager import redis_manager


class AuthManager:
    """认证管理器"""
    
    def __init__(self):
        self.secret_key = config_manager.get('security.secret_key', 'default-secret-key-beesyncclip-2024')
        self.algorithm = "HS256"
        self.access_token_expire = config_manager.get('security.access_token_expire', 3600)
    
    def hash_password(self, password: str) -> str:
        """生成密码哈希 - 使用PBKDF2"""
        if not password:
            return ""
        # 使用PBKDF2进行密码哈希
        salt = self.secret_key.encode('utf-8')
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return hashed.hex()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        if not plain_password or not hashed_password:
            return False
        return self.hash_password(plain_password) == hashed_password
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(seconds=self.access_token_expire)
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"创建访问令牌失败: {e}")
            return ""
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证访问令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已过期")
            return None
        except jwt.JWTError as e:
            logger.warning(f"无效令牌: {e}")
            return None
    
    def register_user(self, username: str, password: str, email: str = None) -> Optional[User]:
        """注册新用户"""
        try:
            if not redis_manager.is_connected():
                logger.error("Redis未连接")
                return None
            
            # 检查输入参数
            if not username or not password:
                logger.error("用户名或密码为空")
                return None
            
            # 检查用户是否已存在
            user_key = f"user:username:{username}"
            if redis_manager.redis_client.exists(user_key):
                logger.warning(f"用户已存在: {username}")
                return redis_manager.get_user_by_username(username)  # 返回已存在的用户而不是None
            
            # 创建用户
            user = User(
                username=username,
                email=email or f"{username}@beesyncclip.local",
                password_hash=self.hash_password(password)
            )
            
            # 保存用户到Redis
            user_data = user.dict()
            user_data['created_at'] = user.created_at.isoformat()
            
            # 转换布尔值为字符串，确保Redis兼容性
            for key, value in user_data.items():
                if isinstance(value, bool):
                    user_data[key] = str(value)
                elif isinstance(value, list):
                    user_data[key] = str(value)  # 将列表转换为字符串
            
            # 保存用户信息
            redis_manager.redis_client.hset(f"user:{user.id}", mapping=user_data)
            redis_manager.redis_client.set(user_key, user.id)
            
            logger.info(f"用户注册成功: {username}")
            return user
            
        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            return None
    
    def authenticate_user(self, auth_request: AuthRequest) -> AuthResponse:
        """用户认证"""
        try:
            if not redis_manager.is_connected():
                return AuthResponse(success=False, message="服务器连接失败")
            
            # 查找用户
            user_key = f"user:username:{auth_request.username}"
            user_id = redis_manager.redis_client.get(user_key)
            
            if not user_id:
                return AuthResponse(success=False, message="用户不存在")
            
            # 获取用户信息
            user_data = redis_manager.redis_client.hgetall(f"user:{user_id}")
            if not user_data:
                return AuthResponse(success=False, message="用户数据不存在")
            
            # 验证密码
            if not self.verify_password(auth_request.password, user_data['password_hash']):
                return AuthResponse(success=False, message="密码错误")
            
            # 创建或更新设备信息
            device_info = auth_request.device_info
            logger.info(f"接收到的设备信息: {device_info}")
            device_id = device_info.get('device_id')

            # 检查设备是否已存在
            device_key = f"device:{device_id}"
            existing_device_data = redis_manager.redis_client.hgetall(device_key)
            
            if existing_device_data:
                # 更新现有设备信息
                device_data = existing_device_data
                device_data['last_seen'] = datetime.now().isoformat()
                device_data['is_online'] = 'True'
                device_data['ip_address'] = device_info.get('ip_address', device_data.get('ip_address', '0.0.0.0'))
                device_data['os_info'] = f"{device_info.get('platform', 'Unknown')} {device_info.get('version', '')}".strip()
                redis_manager.redis_client.hset(device_key, mapping=device_data)
                device_id_to_use = device_id
            else:
                # 创建新设备
                os_info = f"{device_info.get('platform', 'Unknown')} {device_info.get('version', '')}".strip()
                device = Device(
                    id=device_id, # 使用客户端传来的ID
                    name=device_info.get('hostname') or device_info.get('device_name', 'Unknown Device'),
                    os_info=os_info,
                    ip_address=device_info.get('ip_address', '0.0.0.0'),
                    user_id=user_id,
                    is_online=True
                )
                
                # 保存设备信息
                device_data = device.dict()
                device_data['created_at'] = device.created_at.isoformat()
                device_data['last_seen'] = device.last_seen.isoformat()
                
                # 转换布尔值为字符串
                for key, value in device_data.items():
                    if isinstance(value, bool):
                        device_data[key] = str(value)
                    elif isinstance(value, list):
                        device_data[key] = str(value)
                
                redis_manager.redis_client.hset(device_key, mapping=device_data)
                device_id_to_use = device.id

            # 将设备ID添加到用户的设备列表中
            redis_manager.redis_client.sadd(f"devices:{user_id}", device_id_to_use)
            
            # 设置设备在线状态
            redis_manager.set_device_online(user_id, device_id_to_use)
            
            # 创建访问令牌
            token_data = {
                "user_id": user_id,
                "device_id": device_id_to_use,
                "username": auth_request.username
            }
            access_token = self.create_access_token(token_data)
            
            if not access_token:
                return AuthResponse(success=False, message="令牌创建失败")
            
            logger.info(f"用户认证成功: {auth_request.username}")
            return AuthResponse(
                success=True,
                token=access_token,
                user_id=user_id,
                device_id=device_id_to_use,
                message="认证成功"
            )
            
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            return AuthResponse(success=False, message="认证过程中发生错误")
    
    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """通过令牌获取用户信息"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        try:
            user_id = payload.get('user_id')
            device_id = payload.get('device_id')
            
            if not user_id or not device_id:
                return None
            
            # 更新设备在线状态
            redis_manager.set_device_online(user_id, device_id)
            
            return {
                "user_id": user_id,
                "device_id": device_id,
                "username": payload.get('username')
            }
            
        except Exception as e:
            logger.error(f"通过令牌获取用户信息失败: {e}")
            return None

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """通过用户名获取用户信息"""
        try:
            if not redis_manager.is_connected():
                return None
            
            # 查找用户
            user_key = f"user:username:{username}"
            user_id = redis_manager.redis_client.get(user_key)
            
            if not user_id:
                return None
            
            # 获取用户信息
            user_data = redis_manager.redis_client.hgetall(f"user:{user_id}")
            if not user_data:
                return None
            
            return {
                "id": user_id,
                "username": user_data.get('username'),
                "email": user_data.get('email'),
                "created_at": user_data.get('created_at'),
                "is_active": user_data.get('is_active', 'True') == 'True'
            }
            
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    def logout_user(self, token: str) -> bool:
        """用户登出"""
        try:
            payload = self.verify_token(token)
            if not payload:
                return False
            
            user_id = payload.get('user_id')
            device_id = payload.get('device_id')
            
            if user_id and device_id:
                # 设置设备离线
                device_key = f"device:{device_id}"
                redis_manager.redis_client.hset(device_key, 'is_online', 'false')
                
                # 从在线设备集合中移除
                online_devices_key = f"online_devices:{user_id}"
                redis_manager.redis_client.srem(online_devices_key, device_id)
                
                logger.info(f"用户登出成功: {payload.get('username')}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"用户登出失败: {e}")
            return False


# 全局认证管理器实例
auth_manager = AuthManager() 
"""
BeeSyncClip 用户认证模块
"""

import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from loguru import logger

from shared.models import User, Device, AuthRequest, AuthResponse
from shared.utils import config_manager, get_device_info
from server.redis_manager import redis_manager


class AuthManager:
    """认证管理器"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = config_manager.get('security.secret_key', 'default-secret-key')
        self.algorithm = "HS256"
        self.access_token_expire = config_manager.get('security.access_token_expire', 3600)
    
    def hash_password(self, password: str) -> str:
        """生成密码哈希"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
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
            
            # 检查用户是否已存在
            user_key = f"user:username:{username}"
            if redis_manager.redis_client.exists(user_key):
                logger.warning(f"用户已存在: {username}")
                return None
            
            # 创建用户
            user = User(
                username=username,
                email=email,
                password_hash=self.hash_password(password)
            )
            
            # 保存用户到Redis
            user_data = user.dict()
            user_data['created_at'] = user.created_at.isoformat()
            
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
            device = Device(
                name=device_info.get('hostname', 'Unknown Device'),
                platform=device_info.get('platform', 'Unknown'),
                version=device_info.get('platform_version', 'Unknown'),
                user_id=user_id,
                is_online=True
            )
            
            # 保存设备信息
            device_data = device.dict()
            device_data['last_seen'] = device.last_seen.isoformat()
            redis_manager.redis_client.hset(f"device:{device.id}", mapping=device_data)
            
            # 设置设备在线状态
            redis_manager.set_device_online(user_id, device.id)
            
            # 创建访问令牌
            token_data = {
                "user_id": user_id,
                "device_id": device.id,
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
                device_id=device.id,
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
                'user_id': user_id,
                'device_id': device_id,
                'username': payload.get('username')
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
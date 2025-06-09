"""
JWT Token 管理器
提供JWT token的生成、验证、刷新功能
"""

import jwt
import time
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger


class TokenManager:
    """JWT Token管理器"""
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        初始化Token管理器
        
        Args:
            secret_key: JWT签名密钥，如果不提供则自动生成
        """
        self.secret_key = secret_key or os.environ.get('JWT_SECRET_KEY') or self._generate_secret_key()
        self.algorithm = 'HS256'
        self.access_token_expire_hours = 24  # 访问token过期时间（小时）
        self.refresh_token_expire_days = 30   # 刷新token过期时间（天）
        
        # Token黑名单（用于登出）
        self.token_blacklist = set()
        
        logger.info("JWT Token管理器初始化完成")
    
    def _generate_secret_key(self) -> str:
        """生成随机密钥"""
        import secrets
        return secrets.token_hex(32)
    
    def generate_tokens(self, user_id: str, username: str, device_id: str) -> Dict[str, str]:
        """
        生成访问token和刷新token
        
        Args:
            user_id: 用户ID
            username: 用户名
            device_id: 设备ID
            
        Returns:
            包含access_token和refresh_token的字典
        """
        try:
            now = datetime.utcnow()
            
            # 访问token payload
            access_payload = {
                'user_id': user_id,
                'username': username,
                'device_id': device_id,
                'type': 'access',
                'iat': now,
                'exp': now + timedelta(hours=self.access_token_expire_hours)
            }
            
            # 刷新token payload
            refresh_payload = {
                'user_id': user_id,
                'username': username,
                'device_id': device_id,
                'type': 'refresh',
                'iat': now,
                'exp': now + timedelta(days=self.refresh_token_expire_days)
            }
            
            # 生成tokens
            access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
            refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
            
            logger.debug(f"为用户 {username} 生成了新的token对")
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': self.access_token_expire_hours * 3600
            }
            
        except Exception as e:
            logger.error(f"生成token失败: {e}")
            raise
    
    def verify_token(self, token: str, token_type: str = 'access') -> Optional[Dict[str, Any]]:
        """
        验证token
        
        Args:
            token: JWT token
            token_type: token类型 ('access' 或 'refresh')
            
        Returns:
            解码后的payload，如果验证失败返回None
        """
        try:
            # 检查token是否在黑名单中
            if token in self.token_blacklist:
                logger.warning("Token已被吊销")
                return None
            
            # 解码并验证token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 验证token类型
            if payload.get('type') != token_type:
                logger.warning(f"Token类型不匹配: 期望 {token_type}, 实际 {payload.get('type')}")
                return None
            
            # 检查是否过期
            exp = payload.get('exp')
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                logger.warning("Token已过期")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效的token: {e}")
            return None
        except Exception as e:
            logger.error(f"验证token失败: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """
        使用刷新token生成新的访问token
        
        Args:
            refresh_token: 刷新token
            
        Returns:
            新的token对，如果失败返回None
        """
        try:
            # 验证刷新token
            payload = self.verify_token(refresh_token, 'refresh')
            if not payload:
                return None
            
            # 生成新的token对
            new_tokens = self.generate_tokens(
                user_id=payload['user_id'],
                username=payload['username'],
                device_id=payload['device_id']
            )
            
            logger.info(f"为用户 {payload['username']} 刷新了token")
            return new_tokens
            
        except Exception as e:
            logger.error(f"刷新token失败: {e}")
            return None
    
    def revoke_token(self, token: str):
        """
        吊销token（加入黑名单）
        
        Args:
            token: 要吊销的token
        """
        try:
            self.token_blacklist.add(token)
            logger.debug("Token已加入黑名单")
        except Exception as e:
            logger.error(f"吊销token失败: {e}")
    
    def clean_expired_blacklist(self):
        """清理过期的黑名单token"""
        try:
            current_time = datetime.utcnow()
            expired_tokens = set()
            
            for token in self.token_blacklist:
                try:
                    payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
                    exp = payload.get('exp')
                    if exp and datetime.utcfromtimestamp(exp) < current_time:
                        expired_tokens.add(token)
                except:
                    # 如果无法解码，也认为是过期的
                    expired_tokens.add(token)
            
            self.token_blacklist -= expired_tokens
            if expired_tokens:
                logger.debug(f"清理了 {len(expired_tokens)} 个过期的黑名单token")
                
        except Exception as e:
            logger.error(f"清理黑名单失败: {e}")
    
    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """
        获取token信息（不验证过期时间）
        
        Args:
            token: JWT token
            
        Returns:
            token信息
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            
            exp_timestamp = payload.get('exp')
            iat_timestamp = payload.get('iat')
            
            return {
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'device_id': payload.get('device_id'),
                'type': payload.get('type'),
                'issued_at': datetime.utcfromtimestamp(iat_timestamp).isoformat() if iat_timestamp else None,
                'expires_at': datetime.utcfromtimestamp(exp_timestamp).isoformat() if exp_timestamp else None,
                'is_expired': exp_timestamp and datetime.utcfromtimestamp(exp_timestamp) < datetime.utcnow(),
                'is_blacklisted': token in self.token_blacklist
            }
            
        except Exception as e:
            logger.error(f"获取token信息失败: {e}")
            return None


# 全局token管理器实例
token_manager = TokenManager() 
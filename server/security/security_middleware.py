"""
安全中间件
处理请求认证、加密、安全头等
"""

from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional, Callable
import time
from loguru import logger

from .token_manager import token_manager
from .encryption import encryption_manager


class SecurityMiddleware:
    """安全中间件"""
    
    def __init__(self):
        self.security = HTTPBearer(auto_error=False)
        self.rate_limit_cache: Dict[str, list] = {}
        self.max_requests_per_minute = 60
        logger.info("安全中间件初始化完成")
    
    def add_security_headers(self, response: Response) -> Response:
        """添加安全头"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
    
    def check_rate_limit(self, client_ip: str) -> bool:
        """检查速率限制"""
        try:
            current_time = time.time()
            minute_ago = current_time - 60
            
            # 清理过期记录
            if client_ip in self.rate_limit_cache:
                self.rate_limit_cache[client_ip] = [
                    req_time for req_time in self.rate_limit_cache[client_ip] 
                    if req_time > minute_ago
                ]
            else:
                self.rate_limit_cache[client_ip] = []
            
            # 检查请求数量
            if len(self.rate_limit_cache[client_ip]) >= self.max_requests_per_minute:
                logger.warning(f"IP {client_ip} 超过速率限制")
                return False
            
            # 记录当前请求
            self.rate_limit_cache[client_ip].append(current_time)
            return True
            
        except Exception as e:
            logger.error(f"速率限制检查失败: {e}")
            return True  # 出错时允许通过
    
    async def authenticate_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """认证请求"""
        try:
            # 获取Authorization头
            authorization = request.headers.get("Authorization")
            if not authorization:
                return None
            
            # 解析Bearer token
            if not authorization.startswith("Bearer "):
                return None
            
            token = authorization[7:]  # 移除 "Bearer " 前缀
            
            # 验证token
            payload = token_manager.verify_token(token, 'access')
            if not payload:
                return None
            
            logger.debug(f"用户 {payload['username']} 认证成功")
            return payload
            
        except Exception as e:
            logger.error(f"请求认证失败: {e}")
            return None
    
    def create_authenticated_user_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """创建认证用户信息"""
        return {
            'user_id': payload.get('user_id'),
            'username': payload.get('username'),
            'device_id': payload.get('device_id'),
            'is_authenticated': True
        }
    
    async def encrypt_response_data(self, data: Any, user_id: str) -> Dict[str, Any]:
        """加密响应数据"""
        try:
            if not isinstance(data, (str, dict, list)):
                return data
            
            # 将数据转换为JSON字符串
            import json
            data_str = json.dumps(data, ensure_ascii=False) if not isinstance(data, str) else data
            
            # 加密数据
            encrypted_data = encryption_manager.encrypt_clipboard_content(data_str, user_id)
            
            return {
                'encrypted': True,
                'data': encrypted_data
            }
            
        except Exception as e:
            logger.error(f"响应数据加密失败: {e}")
            # 加密失败时返回原数据
            return data
    
    async def decrypt_request_data(self, encrypted_data: Dict[str, Any], user_id: str) -> Any:
        """解密请求数据"""
        try:
            if not encrypted_data.get('encrypted'):
                return encrypted_data
            
            data_dict = encrypted_data.get('data', {})
            decrypted_str = encryption_manager.decrypt_clipboard_content(data_dict, user_id)
            
            # 尝试解析JSON
            import json
            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str
                
        except Exception as e:
            logger.error(f"请求数据解密失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数据解密失败"
            )
    
    def validate_device_access(self, user_payload: Dict[str, Any], requested_device_id: str) -> bool:
        """验证设备访问权限"""
        try:
            # 检查是否是用户自己的设备
            token_device_id = user_payload.get('device_id')
            if token_device_id == requested_device_id:
                return True
            
            # 这里可以添加更复杂的设备权限检查逻辑
            # 比如检查设备是否属于同一用户等
            
            logger.warning(f"设备访问权限验证失败: token_device={token_device_id}, requested_device={requested_device_id}")
            return False
            
        except Exception as e:
            logger.error(f"设备访问权限验证失败: {e}")
            return False
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], request: Request):
        """记录安全事件"""
        try:
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("User-Agent", "unknown")
            
            log_data = {
                'event_type': event_type,
                'client_ip': client_ip,
                'user_agent': user_agent,
                'timestamp': time.time(),
                **details
            }
            
            logger.warning(f"安全事件: {log_data}")
            
        except Exception as e:
            logger.error(f"记录安全事件失败: {e}")
    
    def create_secure_session(self, user_id: str, username: str, device_id: str) -> Dict[str, Any]:
        """创建安全会话"""
        try:
            # 生成JWT tokens
            tokens = token_manager.generate_tokens(user_id, username, device_id)
            
            # 生成会话密钥
            session_key = encryption_manager.generate_session_key(user_id)
            
            # 获取服务器公钥
            server_public_key = encryption_manager.get_server_public_key_pem()
            
            return {
                **tokens,
                'server_public_key': server_public_key,
                'encryption_enabled': True,
                'session_created_at': time.time()
            }
            
        except Exception as e:
            logger.error(f"创建安全会话失败: {e}")
            raise
    
    def cleanup_user_session(self, user_id: str, access_token: str):
        """清理用户会话"""
        try:
            # 吊销token
            token_manager.revoke_token(access_token)
            
            # 删除会话密钥
            encryption_manager.remove_session_key(user_id)
            
            logger.info(f"用户 {user_id} 会话已清理")
            
        except Exception as e:
            logger.error(f"清理用户会话失败: {e}")


# 全局安全中间件实例
security_middleware = SecurityMiddleware() 
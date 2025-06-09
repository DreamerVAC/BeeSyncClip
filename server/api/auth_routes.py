"""
认证相关的API路由
"""

from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from loguru import logger

from server.auth import auth_manager
from server.security import security_middleware, encryption_manager, token_manager
from shared.utils import get_device_info


auth_router = APIRouter(prefix="/auth", tags=["认证"])


class LoginRequest(BaseModel):
    username: str
    password: str
    device_info: Optional[Dict[str, Any]] = None


class RegisterRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class KeyExchangeRequest(BaseModel):
    encrypted_session_key: str  # 用服务器公钥加密的会话密钥


def success_response(data: Dict[str, Any], status_code: int = 200) -> JSONResponse:
    """返回成功响应"""
    return JSONResponse(content=data, status_code=status_code)


def error_response(message: str, status_code: int = 400) -> JSONResponse:
    """返回错误响应"""
    return JSONResponse(content={"error": message}, status_code=status_code)


@auth_router.get("/public-key")
async def get_public_key():
    """获取服务器公钥（用于密钥交换）"""
    try:
        public_key = encryption_manager.get_server_public_key_pem()
        return success_response({
            "public_key": public_key,
            "algorithm": "RSA-2048",
            "key_format": "PEM"
        })
    except Exception as e:
        logger.error(f"获取公钥失败: {e}")
        return error_response("获取公钥失败", 500)


@auth_router.post("/key-exchange")
async def key_exchange(request: KeyExchangeRequest, req: Request):
    """密钥交换"""
    try:
        # 解密客户端发送的会话密钥
        session_key = encryption_manager.decrypt_with_server_key(
            request.encrypted_session_key
        )
        
        # 这里应该有用户身份验证，为简化直接返回成功
        # 实际应用中需要验证用户身份后再建立会话密钥
        
        return success_response({
            "status": "success",
            "message": "密钥交换成功"
        })
        
    except Exception as e:
        logger.error(f"密钥交换失败: {e}")
        security_middleware.log_security_event(
            "key_exchange_failed",
            {"error": str(e)},
            req
        )
        return error_response("密钥交换失败", 400)


@auth_router.post("/register")
async def register(request: RegisterRequest, req: Request):
    """用户注册"""
    try:
        # 验证速率限制
        client_ip = req.client.host if req.client else "unknown"
        if not security_middleware.check_rate_limit(client_ip):
            return error_response("请求过于频繁，请稍后再试", 429)
        
        # 验证输入
        if len(request.username) < 3:
            return error_response("用户名至少需要3个字符")
        
        if len(request.password) < 6:
            return error_response("密码至少需要6个字符")
        
        # 注册用户（auth_manager会自己处理密码哈希）
        user = auth_manager.register_user(
            username=request.username,
            password=request.password,  # 传入明文密码，让auth_manager处理
            email=None
        )
        
        if user:
            logger.info(f"用户注册成功: {request.username}")
            return success_response({
                "success": True,
                "user_id": user.id,
                "message": "注册成功"
            })
        else:
            return error_response("用户已存在或注册失败")
            
    except Exception as e:
        logger.error(f"用户注册错误: {e}")
        security_middleware.log_security_event(
            "registration_failed",
            {"username": request.username, "error": str(e)},
            req
        )
        return error_response("注册过程中发生错误", 500)


@auth_router.post("/login")
async def login(request: LoginRequest, req: Request):
    """用户登录"""
    try:
        # 验证速率限制
        client_ip = req.client.host if req.client else "unknown"
        if not security_middleware.check_rate_limit(client_ip):
            return error_response("请求过于频繁，请稍后再试", 429)
        
        # 如果没有提供设备信息，使用服务器检测的信息
        if not request.device_info:
            request.device_info = get_device_info()
        
        # 获取用户信息进行密码验证
        user = auth_manager.get_user_by_username(request.username)
        if not user:
            security_middleware.log_security_event(
                "login_failed",
                {"username": request.username, "reason": "user_not_found"},
                req
            )
            return error_response("用户名或密码错误")
        
        # 验证密码（使用auth_manager的验证方法）
        password_valid = auth_manager.verify_password(request.password, user['password'])
        
        if not password_valid:
            security_middleware.log_security_event(
                "login_failed",
                {"username": request.username, "reason": "invalid_password"},
                req
            )
            return error_response("用户名或密码错误")
        
        # 创建或获取设备
        device = auth_manager.create_or_update_device(user['id'], request.device_info)
        
        # 创建安全会话
        session_data = security_middleware.create_secure_session(
            user_id=user['id'],
            username=user['username'],
            device_id=device['id']
        )
        
        logger.info(f"用户登录成功: {request.username}")
        return success_response({
            "success": True,
            "user_id": user['id'],
            "username": user['username'],
            "device_id": device['id'],
            "message": "登录成功",
            **session_data
        })
        
    except Exception as e:
        logger.error(f"用户登录错误: {e}")
        security_middleware.log_security_event(
            "login_error",
            {"username": request.username, "error": str(e)},
            req
        )
        return error_response("登录过程中发生错误", 500)


@auth_router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest, req: Request):
    """刷新访问token"""
    try:
        new_tokens = token_manager.refresh_access_token(
            request.refresh_token
        )
        
        if new_tokens:
            return success_response(new_tokens)
        else:
            security_middleware.log_security_event(
                "token_refresh_failed",
                {"refresh_token": request.refresh_token[:20] + "..."},
                req
            )
            return error_response("刷新token无效或已过期", 401)
            
    except Exception as e:
        logger.error(f"刷新token失败: {e}")
        return error_response("刷新token失败", 500)


@auth_router.post("/logout")
async def logout(req: Request):
    """用户登出"""
    try:
        # 认证用户
        user_payload = await security_middleware.authenticate_request(req)
        if not user_payload:
            return error_response("未认证的请求", 401)
        
        # 获取access token
        authorization = req.headers.get("Authorization", "")
        access_token = authorization[7:] if authorization.startswith("Bearer ") else ""
        
        # 清理会话
        security_middleware.cleanup_user_session(
            user_payload['user_id'], 
            access_token
        )
        
        logger.info(f"用户登出成功: {user_payload['username']}")
        return success_response({"message": "登出成功"})
        
    except Exception as e:
        logger.error(f"用户登出错误: {e}")
        return error_response("登出过程中发生错误", 500)


@auth_router.get("/profile")
async def get_profile(req: Request):
    """获取用户信息"""
    try:
        # 认证用户
        user_payload = await security_middleware.authenticate_request(req)
        if not user_payload:
            return error_response("未认证的请求", 401)
        
        user_info = security_middleware.create_authenticated_user_info(user_payload)
        
        return success_response({
            "user": user_info,
            "encryption_enabled": True
        })
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return error_response("获取用户信息失败", 500) 
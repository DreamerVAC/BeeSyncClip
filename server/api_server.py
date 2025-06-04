"""
BeeSyncClip HTTP API 服务器
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from loguru import logger

from shared.models import (
    AuthRequest, AuthResponse, ClipboardHistory, 
    ClipboardItem, Device, User
)
from shared.utils import config_manager, get_device_info
from server.auth import auth_manager
from server.redis_manager import redis_manager


# 创建FastAPI应用
app = FastAPI(
    title="BeeSyncClip API",
    description="跨平台同步剪切板 API 服务",
    version="1.0.0"
)

# 配置CORS（用于阿里云部署）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP Bearer认证
security = HTTPBearer()


# API请求模型
class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class StatusResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    version: str


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前认证用户"""
    token = credentials.credentials
    user_info = auth_manager.get_user_by_token(token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info


@app.get("/", response_model=StatusResponse)
async def root():
    """API根路径，返回服务状态"""
    from datetime import datetime
    return StatusResponse(
        status="running",
        message="BeeSyncClip API 服务正常运行",
        timestamp=datetime.now().isoformat(),
        version=config_manager.get('app.version', '1.0.0')
    )


@app.get("/health")
async def health_check():
    """健康检查接口"""
    redis_status = "connected" if redis_manager.is_connected() else "disconnected"
    
    return {
        "status": "healthy",
        "services": {
            "redis": redis_status,
            "api": "running"
        },
        "timestamp": str(datetime.now())
    }


@app.post("/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """用户注册"""
    try:
        # 检查用户名长度
        if len(request.username) < 3:
            return AuthResponse(success=False, message="用户名至少需要3个字符")
        
        if len(request.password) < 6:
            return AuthResponse(success=False, message="密码至少需要6个字符")
        
        # 注册用户
        user = auth_manager.register_user(
            username=request.username,
            password=request.password,
            email=request.email
        )
        
        if user:
            logger.info(f"用户注册成功: {request.username}")
            return AuthResponse(
                success=True,
                user_id=user.id,
                message="注册成功"
            )
        else:
            return AuthResponse(success=False, message="用户已存在或注册失败")
            
    except Exception as e:
        logger.error(f"用户注册错误: {e}")
        return AuthResponse(success=False, message="注册过程中发生错误")


@app.post("/auth/login", response_model=AuthResponse)
async def login(request: AuthRequest):
    """用户登录"""
    try:
        # 如果没有提供设备信息，使用服务器检测的信息
        if not request.device_info:
            request.device_info = get_device_info()
        
        # 进行认证
        auth_response = auth_manager.authenticate_user(request)
        
        if auth_response.success:
            logger.info(f"用户登录成功: {request.username}")
        else:
            logger.warning(f"用户登录失败: {request.username}, 原因: {auth_response.message}")
        
        return auth_response
        
    except Exception as e:
        logger.error(f"用户登录错误: {e}")
        return AuthResponse(success=False, message="登录过程中发生错误")


@app.post("/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """用户登出"""
    try:
        # 这里应该从请求头获取token，但为了简化，我们从用户信息获取
        # 实际实现中需要传递完整的token
        success = True  # auth_manager.logout_user(token)
        
        if success:
            logger.info(f"用户登出成功: {current_user['username']}")
            return {"message": "登出成功"}
        else:
            raise HTTPException(status_code=400, detail="登出失败")
            
    except Exception as e:
        logger.error(f"用户登出错误: {e}")
        raise HTTPException(status_code=500, detail="登出过程中发生错误")


@app.get("/clipboard/history", response_model=ClipboardHistory)
async def get_clipboard_history(
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """获取剪切板历史记录"""
    try:
        if per_page > 100:
            per_page = 100  # 限制每页最大数量
        
        history = redis_manager.get_user_clipboard_history(
            current_user['user_id'], 
            page, 
            per_page
        )
        
        logger.debug(f"获取历史记录: user={current_user['username']}, page={page}")
        return history
        
    except Exception as e:
        logger.error(f"获取历史记录错误: {e}")
        raise HTTPException(status_code=500, detail="获取历史记录失败")


@app.get("/clipboard/latest")
async def get_latest_clipboard(current_user: dict = Depends(get_current_user)):
    """获取最新的剪切板项"""
    try:
        latest_item = redis_manager.get_latest_clipboard_item(current_user['user_id'])
        
        if latest_item:
            return {"item": latest_item.dict()}
        else:
            return {"item": None, "message": "没有剪切板记录"}
            
    except Exception as e:
        logger.error(f"获取最新剪切板项错误: {e}")
        raise HTTPException(status_code=500, detail="获取最新剪切板项失败")


@app.delete("/clipboard/{item_id}")
async def delete_clipboard_item(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """删除指定的剪切板项"""
    try:
        success = redis_manager.delete_clipboard_item(current_user['user_id'], item_id)
        
        if success:
            logger.info(f"删除剪切板项: user={current_user['username']}, item_id={item_id}")
            return {"message": "删除成功"}
        else:
            raise HTTPException(status_code=404, detail="剪切板项不存在")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除剪切板项错误: {e}")
        raise HTTPException(status_code=500, detail="删除剪切板项失败")


@app.get("/devices")
async def get_user_devices(current_user: dict = Depends(get_current_user)):
    """获取用户的设备列表"""
    try:
        online_devices = redis_manager.get_online_devices(current_user['user_id'])
        
        return {
            "current_device": current_user['device_id'],
            "online_devices": online_devices,
            "total_online": len(online_devices)
        }
        
    except Exception as e:
        logger.error(f"获取设备列表错误: {e}")
        raise HTTPException(status_code=500, detail="获取设备列表失败")


@app.get("/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """获取用户统计信息"""
    try:
        history = redis_manager.get_user_clipboard_history(current_user['user_id'], 1, 1)
        online_devices = redis_manager.get_online_devices(current_user['user_id'])
        
        return {
            "total_items": history.total,
            "online_devices": len(online_devices),
            "username": current_user['username'],
            "user_id": current_user['user_id']
        }
        
    except Exception as e:
        logger.error(f"获取用户统计错误: {e}")
        raise HTTPException(status_code=500, detail="获取统计信息失败")


if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    
    # 配置日志
    logger.add(
        config_manager.get('logging.file_path', 'logs/beesyncclip.log'),
        rotation=config_manager.get('logging.file_rotation', '10 MB'),
        retention=config_manager.get('logging.file_retention', '30 days'),
        level=config_manager.get('logging.level', 'INFO')
    )
    
    host = config_manager.get('api.host', '0.0.0.0')  # 阿里云服务器使用0.0.0.0
    port = config_manager.get('api.port', 8000)
    
    logger.info(f"启动 BeeSyncClip API 服务器: {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=config_manager.get('logging.level', 'info').lower()
    ) 
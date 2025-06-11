"""
BeeSyncClip 模块化服务器
标准化架构，支持加密和安全功能
"""

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from loguru import logger
from datetime import datetime, timedelta

# 导入模块化组件
from server.security import security_middleware, encryption_manager, token_manager
from server.api import auth_router, clipboard_router, device_router, websocket_router
from server.redis_manager import redis_manager
from server.auth import auth_manager
from shared.models import ClipboardItem, ClipboardType
from shared.utils import calculate_checksum
import hashlib
import json


# 创建FastAPI应用
app = FastAPI(
    title="BeeSyncClip Modular API",
    description="模块化、标准化、加密的跨平台同步剪切板 API 服务",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 硬编码管理员配置
ADMIN_CONFIG = {
    "username": "admin",
    "password": "beesync2024!",  # 生产环境应使用强密码
    "password_hash": None  # 将在启动时生成
}

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_middleware_handler(request: Request, call_next):
    """安全中间件处理器"""
    start_time = time.time()
    
    try:
        # 检查速率限制
        client_ip = request.client.host if request.client else "unknown"
        if not security_middleware.check_rate_limit(client_ip):
            return JSONResponse(
                content={"error": "请求过于频繁，请稍后再试"},
                status_code=429
            )
        
        # 处理请求
        response = await call_next(request)
        
        # 添加安全头
        response = security_middleware.add_security_headers(response)
        
        # 添加处理时间头
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        logger.error(f"安全中间件处理失败: {e}")
        return JSONResponse(
            content={"error": "服务器内部错误"},
            status_code=500
        )


# 注册路由
app.include_router(auth_router)
app.include_router(clipboard_router)
app.include_router(device_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    """API根路径，返回服务状态"""
    return {
        "service": "BeeSyncClip Modular API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "JWT认证",
            "AES-256加密",
            "RSA密钥交换",
            "WebSocket实时同步",
            "速率限制",
            "安全头"
        ],
        "timestamp": datetime.now().isoformat(),
        "encryption_enabled": True
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 检查Redis连接
        redis_status = "connected" if redis_manager.is_connected() else "disconnected"
        
        # 检查加密管理器
        encryption_status = "initialized" if encryption_manager else "error"
        
        # 检查token管理器
        token_status = "initialized" if token_manager else "error"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "redis": redis_status,
                "encryption": encryption_status,
                "token_manager": token_status,
                "api": "running"
            },
            "security": {
                "encryption_enabled": True,
                "jwt_enabled": True,
                "rate_limiting": True
            }
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            status_code=503
        )


@app.get("/security/info")
async def security_info():
    """获取安全配置信息"""
    return {
        "encryption": {
            "algorithm": "AES-256-CBC",
            "key_exchange": "RSA-2048",
            "enabled": True
        },
        "authentication": {
            "method": "JWT",
            "token_expiry": "24 hours",
            "refresh_token_expiry": "30 days"
        },
        "security_headers": {
            "x_content_type_options": "nosniff",
            "x_frame_options": "DENY",
            "x_xss_protection": "1; mode=block",
            "strict_transport_security": "max-age=31536000; includeSubDomains"
        },
        "rate_limiting": {
            "enabled": True,
            "max_requests_per_minute": 60
        }
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {exc}")
    
    # 记录安全事件
    security_middleware.log_security_event(
        "unhandled_exception",
        {"error": str(exc), "path": str(request.url)},
        request
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "服务器内部错误",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("🚀 BeeSyncClip 模块化服务器启动中...")
    
    # 检查依赖服务
    if not redis_manager.is_connected():
        logger.error("❌ Redis连接失败！")
        raise RuntimeError("Redis连接失败")
    
    # 初始化管理员密码哈希
    ADMIN_CONFIG["password_hash"] = hashlib.sha256(
        ADMIN_CONFIG["password"].encode()
    ).hexdigest()
    
    logger.info("✅ Redis连接正常")
    logger.info("🔐 加密管理器已初始化")
    logger.info("🎫 Token管理器已初始化")
    logger.info("🛡️ 安全中间件已启用")
    logger.info("👑 管理员账户已初始化")
    logger.info("🌐 模块化服务器启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("🛑 BeeSyncClip 模块化服务器关闭中...")
    
    # 清理资源
    try:
        # 清理过期的token黑名单
        token_manager.clean_expired_blacklist()
        
        # 关闭Redis连接
        if redis_manager.is_connected():
            redis_manager.close()
            logger.info("✅ Redis连接已关闭")
        
        logger.info("👋 模块化服务器已关闭")
        
    except Exception as e:
        logger.error(f"关闭服务器时发生错误: {e}")


# 兼容性路由 - 保持与前端的兼容性
@app.post("/login")
async def login_compat(request: Request):
    """兼容性登录接口"""
    try:
        # 获取请求数据
        request_data = await request.json()
        
        username = request_data.get('username')
        password = request_data.get('password')
        device_info = request_data.get('device_info', {})
        
        if not username or not password:
            return JSONResponse(content={
                "success": False,
                "message": "用户名和密码不能为空"
            }, status_code=400)
        
        # 创建认证请求对象
        from shared.models import AuthRequest
        auth_request = AuthRequest(
            username=username,
            password=password,
            device_info=device_info
        )
        
        # 验证用户
        auth_response = auth_manager.authenticate_user(auth_request)
        if not auth_response.success:
            return JSONResponse(content={
                "success": False,
                "message": auth_response.message
            }, status_code=401)
        
        # 获取用户信息（用于后续处理）
        user = auth_manager.get_user_info(username)
        
        # 生成tokens
        tokens = token_manager.generate_tokens(
            user_id=auth_response.user_id,
            username=username,
            device_id=auth_response.device_id
        )
        
        # 创建安全会话
        session_data = security_middleware.create_secure_session(
            user_id=auth_response.user_id,
            username=username,
            device_id=auth_response.device_id
        )
        
        # 获取用户设备列表（与1.0版本兼容）
        user_devices = redis_manager.get_user_devices(auth_response.user_id)
        
        # 获取用户剪贴板历史（与1.0版本兼容）
        clipboard_history = redis_manager.get_user_clipboard_history(
            auth_response.user_id, page=1, per_page=50
        )
        
        # 查找当前设备信息
        current_device = None
        for device in user_devices:
            if device['device_id'] == device_info['device_id']:
                current_device = {
                    "device_id": device['device_id'],
                    "label": device['name'],
                    "os": device['os_info'],
                    "ip_address": device['ip_address'],
                    "first_login": device['created_at'].strftime("%Y-%m-%d %H:%M:%S"),
                    "last_login": device['last_seen'].strftime("%Y-%m-%d %H:%M:%S")
                }
                break
        
        # 转换设备列表格式
        devices_list = []
        for device in user_devices:
            devices_list.append({
                "device_id": device['device_id'],
                "label": device['name'],
                "os": device['os_info'],
                "ip_address": device['ip_address'],
                "first_login": device['created_at'].strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": device['last_seen'].strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # 转换剪贴板格式
        clipboards_list = []
        for item in clipboard_history.items:
            # 映射枚举类型到前端期望的content_type格式
            content_type_map = {
                'text': 'text/plain',
                'image': 'image/png', 
                'file': 'application/octet-stream',
                'html': 'text/html',
                'rtf': 'text/rtf'
            }
            content_type = content_type_map.get(item.type, 'text/plain')
            
            clipboards_list.append({
                "clip_id": item.id,
                "content": item.content,
                "content_type": content_type,
                "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "last_modified": item.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                "device_id": item.device_id
            })
        
        return JSONResponse(content={
            "success": True,
            "user_id": auth_response.user_id,
            "username": username,
            "device_id": auth_response.device_id,
            "message": "登录成功",
            "token": tokens.get("access_token"),  # 兼容1.0版本的token字段
            "devices": devices_list,
            "current_device": current_device,
            "clipboards": clipboards_list,
            **tokens,
            **session_data
        })
        
    except Exception as e:
        logger.error(f"兼容性登录失败: {e}")
        return JSONResponse(content={
            "success": False,
            "message": "登录过程中发生错误"
        }, status_code=500)


@app.post("/register")
async def register_compat(request: Request):
    """兼容性注册接口"""
    try:
        # 获取请求数据
        request_data = await request.json()
        
        username = request_data.get('username')
        password = request_data.get('password')
        email = request_data.get('email')
        
        if not username or not password:
            return JSONResponse(content={
                "success": False,
                "message": "用户名和密码不能为空"
            }, status_code=400)
        
        # 检查用户是否已存在
        existing_user = auth_manager.get_user_info(username)
        if existing_user:
            return JSONResponse(content={
                "success": False,
                "message": "用户名已存在"
            }, status_code=409)
        
        # 注册用户
        user = auth_manager.register_user(
            username=username,
            password=password,
            email=email
        )
        
        if user:
            return JSONResponse(content={
                "success": True,
                "user_id": user.id,
                "username": user.username,
                "message": "注册成功"
            }, status_code=201)
        else:
            return JSONResponse(content={
                "success": False,
                "message": "注册失败"
            }, status_code=500)
            
    except Exception as e:
        logger.error(f"兼容性注册失败: {e}")
        return JSONResponse(content={
            "success": False,
            "message": "注册过程中发生错误"
        }, status_code=500)


@app.get("/get_devices")
async def get_devices_compat(request: Request):
    """兼容性获取设备接口"""
    try:
        # 获取username参数
        username = request.query_params.get("username")
        if not username:
            return JSONResponse(content={
                "error": "缺少username参数"
            }, status_code=400)
        
        # 获取用户信息
        user = redis_manager.get_user_by_username(username)
        if not user:
            return JSONResponse(content={
                "error": "用户不存在"
            }, status_code=404)
        
        user_id = user['id']
        
        # 获取用户设备列表
        devices = redis_manager.get_user_devices(user_id)
        
        # 转换为兼容性格式（与登录接口保持一致）
        device_list = []
        for device in devices:
            device_info = {
                "device_id": device.get('device_id'),
                "label": device.get('name'),  # 与登录接口一致
                "os": device.get('os_info'),  # 与登录接口一致
                "ip_address": device.get('ip_address'),  # 与登录接口一致
                "first_login": device.get('created_at').strftime("%Y-%m-%d %H:%M:%S") if device.get('created_at') else None,
                "last_login": device.get('last_seen').strftime("%Y-%m-%d %H:%M:%S") if device.get('last_seen') else None,
                "is_online": redis_manager.is_device_online(user_id, device.get('device_id', ''))
            }
            device_list.append(device_info)
        
        logger.debug(f"获取设备列表成功: user={username}, count={len(device_list)}")
        
        return JSONResponse(content={
            "success": True,
            "devices": device_list,
            "total": len(device_list)
        })
        
    except Exception as e:
        import traceback
        logger.error(f"获取设备列表失败: {e}")
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        return JSONResponse(content={
            "error": f"获取设备列表失败: {str(e)}"
        }, status_code=500)


@app.get("/get_clipboards")
async def get_clipboards_compat(username: str):
    """兼容性获取剪切板接口（优化版本）"""
    try:
        if not username:
            return JSONResponse(content={
                "success": False,
                "message": "缺少username参数"
            }, status_code=400)
        
        # 获取用户信息
        user = redis_manager.get_user_by_username(username)
        if not user:
            return JSONResponse(content={
                "success": False,
                "message": "用户未找到"
            }, status_code=404)
        
        # 🚀 优化：移除每次调用的orphaned cleanup，改为定期任务
        # cleaned_count = redis_manager.clean_orphaned_clipboard_items(user['id'])
        
        # 🚀 优化：获取用户剪切板历史（使用批量查询）
        history = redis_manager.get_user_clipboard_history(user['id'], page=1, per_page=100)
        
        # 转换格式以兼容原始API
        clipboards_list = []
        for item in history.items:
            # 获取原始content_type
            content_type = item.metadata.get('original_content_type', 'text/plain')
            
            clipboards_list.append({
                "clip_id": item.id,
                "content": item.content,
                "content_type": content_type,
                "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "last_modified": item.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                "device_id": item.device_id,
                "device_label": f"设备-{item.device_id[:8]}"  # 简化设备标签处理
            })
        
        return JSONResponse(content={
            "success": True,
            "clipboards": clipboards_list,
            "count": len(clipboards_list)
        })
        
    except Exception as e:
        logger.error(f"获取剪贴板内容错误: {e}")
        return JSONResponse(content={
            "success": False,
            "message": "获取剪贴板内容过程中发生错误"
        }, status_code=500)


@app.post("/add_clipboard")
async def add_clipboard_compat(request: dict):
    """兼容性添加剪切板接口"""
    try:
        username = request.get('username')
        content = request.get('content')
        device_id = request.get('device_id')
        content_type = request.get('content_type', 'text/plain')
        
        if not username or not content or not device_id:
            return JSONResponse(content={
                "success": False,
                "message": "缺少必要参数"
            }, status_code=400)
        
        # 获取用户信息
        user = redis_manager.get_user_by_username(username)
        if not user:
            return JSONResponse(content={
                "success": False,
                "message": "用户不存在"
            }, status_code=404)
        
        # 创建剪切板项
        clipboard_item = ClipboardItem(
            type=ClipboardType.TEXT,
            content=content,
            metadata={
                "source": "compat_api",
                "original_content_type": content_type
            },
            size=len(content.encode('utf-8')),
            device_id=device_id,
            user_id=user['id'],
            checksum=calculate_checksum(content)
        )
        
        # 保存到Redis
        if redis_manager.save_clipboard_item(clipboard_item):
            return JSONResponse(content={
                "success": True,
                "message": "剪贴板记录已添加",
                "clip_id": clipboard_item.id
            }, status_code=201)
        else:
            return JSONResponse(content={
                "success": False,
                "message": "保存失败"
            }, status_code=500)
            
    except Exception as e:
        logger.error(f"添加剪切板内容失败: {e}")
        return JSONResponse(content={
            "success": False,
            "message": "添加剪切板内容过程中发生错误"
        }, status_code=500)


# =============================================================================
# 管理员功能 API
# =============================================================================

def verify_admin_credentials(username: str, password: str) -> bool:
    """验证管理员凭据"""
    if username != ADMIN_CONFIG["username"]:
        return False
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash == ADMIN_CONFIG["password_hash"]


@app.post("/admin/login")
async def admin_login(request: Request):
    """管理员登录接口"""
    try:
        # 获取请求数据
        request_data = await request.json()
        
        username = request_data.get('username')
        password = request_data.get('password')
        
        if not username or not password:
            return JSONResponse(content={
                "success": False,
                "message": "用户名和密码不能为空"
            }, status_code=400)
        
        # 验证管理员凭据
        if not verify_admin_credentials(username, password):
            logger.warning(f"管理员登录失败: {username}")
            return JSONResponse(content={
                "success": False,
                "message": "用户名或密码错误"
            }, status_code=401)
        
        # 生成管理员Token
        admin_token = token_manager.generate_admin_token(username)
        
        logger.info(f"管理员登录成功: {username}")
        
        return JSONResponse(content={
            "success": True,
            "message": "管理员登录成功",
            "admin_token": admin_token,
            "username": username,
            "role": "admin"
        })
        
    except Exception as e:
        logger.error(f"管理员登录失败: {e}")
        return JSONResponse(content={
            "success": False,
            "message": "登录过程中发生错误"
        }, status_code=500)


def verify_admin_token(token: str) -> bool:
    """验证管理员Token"""
    try:
        payload = token_manager.verify_admin_token(token)
        return payload is not None
    except:
        return False


@app.get("/admin/users")
async def admin_get_users(request: Request):
    """管理员获取所有用户列表"""
    try:
        # 获取Authorization头中的token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(content={
                "success": False,
                "message": "缺少认证token"
            }, status_code=401)
        
        token = auth_header.split("Bearer ")[1]
        
        # 验证管理员token
        if not verify_admin_token(token):
            return JSONResponse(content={
                "success": False,
                "message": "无效的管理员token"
            }, status_code=401)
        
        # 获取所有用户
        users = redis_manager.get_all_users()
        
        # 格式化用户列表
        users_list = []
        for user in users:
            # 获取用户的设备数量
            devices_count = len(redis_manager.get_user_devices(user['id']))
            
            # 获取用户的剪贴板数量
            clipboard_history = redis_manager.get_user_clipboard_history(user['id'], page=1, per_page=1)
            clipboards_count = clipboard_history.total
            
            # 获取用户最后登录时间
            user_devices = redis_manager.get_user_devices(user['id'])
            last_login = None
            if user_devices:
                # 找到最近的登录时间
                latest_device = max(user_devices, key=lambda d: d.get('last_seen', d.get('created_at')))
                last_login = latest_device.get('last_seen', latest_device.get('created_at'))
                if last_login:
                    last_login = last_login.strftime("%Y-%m-%d %H:%M:%S")
            
            users_list.append({
                "user_id": user['id'],
                "username": user['username'],
                "email": user.get('email', ''),
                "created_at": user.get('created_at', '').strftime("%Y-%m-%d %H:%M:%S") if user.get('created_at') else '',
                "last_login": last_login,
                "devices_count": devices_count,
                "clipboards_count": clipboards_count
            })
        
        logger.info(f"管理员获取用户列表成功，共 {len(users_list)} 个用户")
        
        return JSONResponse(content={
            "success": True,
            "users": users_list,
            "total": len(users_list)
        })
        
    except Exception as e:
        logger.error(f"管理员获取用户列表失败: {e}")
        return JSONResponse(content={
            "success": False,
            "message": "获取用户列表失败"
        }, status_code=500)


@app.delete("/admin/users/{username}")
async def admin_delete_user(username: str, request: Request):
    """管理员删除用户及其所有数据"""
    try:
        # 获取Authorization头中的token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(content={
                "success": False,
                "message": "缺少认证token"
            }, status_code=401)
        
        token = auth_header.split("Bearer ")[1]
        
        # 验证管理员token
        if not verify_admin_token(token):
            return JSONResponse(content={
                "success": False,
                "message": "无效的管理员token"
            }, status_code=401)
        
        # 检查用户是否存在
        user = redis_manager.get_user_by_username(username)
        if not user:
            return JSONResponse(content={
                "success": False,
                "message": "用户不存在"
            }, status_code=404)
        
        user_id = user['id']
        
        # 删除用户的所有剪贴板数据
        clipboard_history = redis_manager.get_user_clipboard_history(user_id, page=1, per_page=10000)
        deleted_clipboards = 0
        for item in clipboard_history.items:
            if redis_manager.delete_clipboard_item(user_id, item.id):
                deleted_clipboards += 1
        
        # 删除用户的所有设备
        devices = redis_manager.get_user_devices(user_id)
        deleted_devices = 0
        for device in devices:
            device_id = device.get('device_id')
            if device_id and redis_manager.remove_user_device(user_id, device_id):
                deleted_devices += 1
        
        # 删除用户账户
        if redis_manager.delete_user(user_id):
            logger.info(f"管理员删除用户成功: {username}, 删除剪贴板: {deleted_clipboards}, 删除设备: {deleted_devices}")
            
            return JSONResponse(content={
                "success": True,
                "message": f"用户 {username} 及其所有数据已删除",
                "deleted_clipboards": deleted_clipboards,
                "deleted_devices": deleted_devices
            })
        else:
            return JSONResponse(content={
                "success": False,
                "message": "删除用户失败"
            }, status_code=500)
        
    except Exception as e:
        logger.error(f"管理员删除用户失败: {e}")
        return JSONResponse(content={
            "success": False,
            "message": "删除用户过程中发生错误"
        }, status_code=500)


@app.get("/admin/stats")
async def admin_get_stats(request: Request):
    """管理员获取系统统计信息"""
    try:
        # 获取Authorization头中的token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(content={
                "success": False,
                "message": "缺少认证token"
            }, status_code=401)
        
        token = auth_header.split("Bearer ")[1]
        
        # 验证管理员token
        if not verify_admin_token(token):
            return JSONResponse(content={
                "success": False,
                "message": "无效的管理员token"
            }, status_code=401)
        
        # 获取系统统计
        all_users = redis_manager.get_all_users()
        total_users = len(all_users)
        
        total_devices = 0
        total_clipboards = 0
        active_users = 0
        
        for user in all_users:
            user_id = user['id']
            
            # 统计设备数量
            devices = redis_manager.get_user_devices(user_id)
            total_devices += len(devices)
            
            # 检查是否为活跃用户（7天内有设备活动）
            week_ago = datetime.now() - timedelta(days=7)
            for device in devices:
                last_seen = device.get('last_seen')
                if last_seen and last_seen > week_ago:
                    active_users += 1
                    break
            
            # 统计剪贴板数量
            clipboard_history = redis_manager.get_user_clipboard_history(user_id, page=1, per_page=1)
            total_clipboards += clipboard_history.total
        
        # Redis状态
        redis_info = {
            "connected": redis_manager.is_connected(),
            "version": "6.0+"  # 简化版本信息
        }
        
        return JSONResponse(content={
            "success": True,
            "stats": {
                "total_users": total_users,
                "active_users": active_users,
                "total_devices": total_devices,
                "total_clipboards": total_clipboards,
                "redis_status": redis_info,
                "server_version": "2.0.0",
                "timestamp": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"管理员获取统计信息失败: {e}")
        return JSONResponse(content={
            "success": False,
            "message": "获取统计信息失败"
        }, status_code=500)


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 启动BeeSyncClip模块化服务器...")
    
    uvicorn.run(
        "server.modular_server:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    ) 
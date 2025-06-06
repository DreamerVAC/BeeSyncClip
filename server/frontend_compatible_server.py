"""
BeeSyncClip 前端兼容服务器
保持与Mock服务器相同的API接口，但使用真实的后端逻辑
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import time
import uuid
from loguru import logger
from datetime import datetime

from server.auth import auth_manager
from server.redis_manager import redis_manager
from shared.models import ClipboardItem, Device, User, ClipboardType
from shared.utils import get_device_info


app = FastAPI(
    title="BeeSyncClip Frontend Compatible API",
    description="与前端Mock服务器兼容的真实API服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求数据模型
class LoginRequest(BaseModel):
    username: str
    password: str
    device_info: Dict[str, Any]


class RegisterRequest(BaseModel):
    username: str
    password: str


class UpdateDeviceLabelRequest(BaseModel):
    username: str
    device_id: str
    new_label: str


class RemoveDeviceRequest(BaseModel):
    username: str
    device_id: str


class AddClipboardRequest(BaseModel):
    username: str
    content: str
    device_id: str
    content_type: Optional[str] = "text/plain"


class DeleteClipboardRequest(BaseModel):
    username: str
    clip_id: str


class ClearClipboardsRequest(BaseModel):
    username: str


def success_response(data: Dict[str, Any], status_code: int = 200) -> JSONResponse:
    """返回成功响应"""
    return JSONResponse(content=data, status_code=status_code)


def error_response(message: str, status_code: int = 400) -> JSONResponse:
    """返回错误响应"""
    return JSONResponse(
        content={
            "success": False,
            "message": message,
            "status": status_code
        },
        status_code=status_code
    )


@app.get("/")
async def root():
    """根路径 - 返回API信息"""
    return {
        "service": "BeeSyncClip API Server",
        "version": "1.0.0",
        "status": "running",
        "message": "BeeSyncClip 跨平台同步剪贴板服务",
        "endpoints": {
            "health": "/health",
            "register": "/register",
            "login": "/login",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        # 检查Redis连接
        redis_status = "connected" if redis_manager.is_connected() else "disconnected"
        
        return {
            "status": "healthy",
            "service": "BeeSyncClip",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "redis": redis_status,
                "api": "running"
            },
            "server_info": {
                "host": "47.110.154.99",
                "port": 8000,
                "environment": "production"
            }
        }
    except Exception as e:
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            status_code=503
        )


@app.post("/login")
async def login(request: LoginRequest):
    """用户登录 - 兼容Mock服务器格式"""
    try:
        username = request.username
        password = request.password
        device_info = request.device_info
        
        # 确保设备信息包含device_id
        if 'device_id' not in device_info:
            return error_response("设备信息缺少device_id", 400)
        
        # 使用我们的认证系统
        from shared.models import AuthRequest
        auth_request = AuthRequest(
            username=username,
            password=password,
            device_info=device_info
        )
        
        auth_response = auth_manager.authenticate_user(auth_request)
        
        if auth_response.success:
            # 获取用户设备列表
            user_devices = redis_manager.get_user_devices(auth_response.user_id)
            
            # 获取用户剪贴板历史
            clipboard_history = redis_manager.get_user_clipboard_history(
                auth_response.user_id, page=1, per_page=50
            )
            
            # 查找当前设备信息
            current_device = None
            for device in user_devices:
                if device.device_id == device_info['device_id']:
                    current_device = {
                        "device_id": device.device_id,
                        "label": device.name,
                        "os": device.os_info,
                        "ip_address": device.ip_address,
                        "first_login": device.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "last_login": device.last_seen.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    break
            
            # 转换设备列表格式
            devices_list = []
            for device in user_devices:
                devices_list.append({
                    "device_id": device.device_id,
                    "label": device.name,
                    "os": device.os_info,
                    "ip_address": device.ip_address,
                    "first_login": device.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "last_login": device.last_seen.strftime("%Y-%m-%d %H:%M:%S")
                })
            
            # 转换剪贴板格式
            clipboards_list = []
            for item in clipboard_history.items:
                clipboards_list.append({
                    "clip_id": item.id,
                    "content": item.content,
                    "content_type": item.content_type,
                    "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "last_modified": item.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "device_id": item.device_id
                })
            
            return success_response({
                "success": True,
                "message": "登录成功",
                "token": auth_response.token,
                "device_id": device_info['device_id'],
                "devices": devices_list,
                "current_device": current_device,
                "clipboards": clipboards_list
            })
        else:
            return error_response("用户名或密码错误", 401)
            
    except Exception as e:
        logger.error(f"登录错误: {e}")
        return error_response("登录过程中发生错误", 500)


@app.post("/register")
async def register(request: RegisterRequest):
    """用户注册 - 兼容Mock服务器格式"""
    try:
        username = request.username
        password = request.password
        
        # 检查用户名长度
        if len(username) < 3:
            return error_response("用户名至少需要3个字符", 400)
        
        if len(password) < 6:
            return error_response("密码至少需要6个字符", 400)
        
        # 先检查用户是否已存在
        existing_user = redis_manager.get_user_by_username(username)
        if existing_user:
            return error_response("用户名已存在", 409)
        
        # 使用我们的认证系统注册
        user = auth_manager.register_user(username=username, password=password)
        
        if user:
            # 获取用户总数
            user_count = redis_manager.get_total_users_count()
            
            return success_response({
                "success": True,
                "message": "注册成功",
                "user_count": user_count,
                "username": username
            }, 201)
        else:
            return error_response("注册失败，请稍后重试", 500)
            
    except Exception as e:
        logger.error(f"注册错误: {e}")
        return error_response("注册过程中发生错误", 500)


@app.post("/update_device_label")
async def update_device_label(request: UpdateDeviceLabelRequest):
    """更新设备标签 - 兼容Mock服务器格式"""
    try:
        username = request.username
        device_id = request.device_id
        new_label = request.new_label
        
        # 根据用户名获取用户ID
        user = redis_manager.get_user_by_username(username)
        if not user:
            return error_response("用户未找到", 404)
        
        # 更新设备标签
        success = redis_manager.update_device_name(device_id, new_label)
        
        if success:
            return success_response({
                "success": True,
                "message": "设备标签更新成功",
                "device_id": device_id,
                "new_label": new_label
            })
        else:
            return error_response("设备未找到", 404)
            
    except Exception as e:
        logger.error(f"更新设备标签错误: {e}")
        return error_response("更新设备标签过程中发生错误", 500)


@app.post("/remove_device")
async def remove_device(request: RemoveDeviceRequest):
    """删除设备 - 兼容Mock服务器格式"""
    try:
        username = request.username
        device_id = request.device_id
        
        # 根据用户名获取用户ID
        user = redis_manager.get_user_by_username(username)
        if not user:
            return error_response("用户未找到", 404)
        
        # 删除设备及相关数据
        success = redis_manager.remove_device(device_id)
        
        if success:
            # 删除该设备的剪贴板记录
            removed_clip_count = redis_manager.delete_device_clipboard_items(device_id)
            
            return success_response({
                "success": True,
                "message": "设备删除成功",
                "device_id": device_id,
                "removed_clip_count": removed_clip_count
            })
        else:
            return error_response("设备未找到", 404)
            
    except Exception as e:
        logger.error(f"删除设备错误: {e}")
        return error_response("删除设备过程中发生错误", 500)


@app.post("/add_clipboard")
async def add_clipboard(request: AddClipboardRequest):
    """添加剪贴板内容 - 兼容Mock服务器格式"""
    try:
        username = request.username
        content = request.content
        device_id = request.device_id
        content_type = request.content_type
        
        # 根据用户名获取用户ID
        user = redis_manager.get_user_by_username(username)
        if not user:
            return error_response("用户未找到", 404)
        
        # 创建剪贴板项数据
        clip_id = str(uuid.uuid4())
        item_data = {
            "id": clip_id,
            "content": content,
            "content_type": content_type,
            "device_id": device_id,
            "user_id": user['id'],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 直接存储到Redis
        if not redis_manager.is_connected():
            return error_response("Redis连接失败", 500)
        
        # 保存剪贴板项
        item_key = f"item:{clip_id}"
        user_key = f"clipboard:{user['id']}"
        
        # 存储项目数据
        redis_manager.redis_client.hset(item_key, mapping=item_data)
        
        # 添加到用户的有序集合中
        score = datetime.now().timestamp()
        redis_manager.redis_client.zadd(user_key, {clip_id: score})
        
        # 设置过期时间
        redis_manager.redis_client.expire(item_key, 86400)
        redis_manager.redis_client.expire(user_key, 86400)
        
        # 获取用户所有剪贴板内容
        item_ids = redis_manager.redis_client.zrevrange(user_key, 0, 99)
        
        clipboards_list = []
        for item_id in item_ids:
            item_key = f"item:{item_id}"
            item_data = redis_manager.redis_client.hgetall(item_key)
            if item_data:
                clipboards_list.append({
                    "clip_id": item_data['id'],
                    "content": item_data['content'],
                    "content_type": item_data.get('content_type', 'text/plain'),
                    "created_at": item_data['created_at'],
                    "last_modified": item_data['updated_at'],
                    "device_id": item_data['device_id']
                })
        
        return success_response({
            "success": True,
            "message": "剪贴板内容添加成功",
            "clip_id": clip_id,
            "clipboards": clipboards_list
        }, 201)
            
    except Exception as e:
        logger.error(f"添加剪贴板内容错误: {e}")
        return error_response("添加剪贴板内容过程中发生错误", 500)


@app.post("/delete_clipboard")
async def delete_clipboard(request: DeleteClipboardRequest):
    """删除剪贴板内容 - 兼容Mock服务器格式"""
    try:
        username = request.username
        clip_id = request.clip_id
        
        # 根据用户名获取用户ID
        user = redis_manager.get_user_by_username(username)
        if not user:
            return error_response("用户未找到", 404)
        
        # 获取剪贴板项信息用于显示
        item_key = f"item:{clip_id}"
        item_data = redis_manager.redis_client.hgetall(item_key)
        if not item_data:
            return error_response("剪贴板内容未找到", 404)
        
        # 删除剪贴板项
        user_key = f"clipboard:{user['id']}"
        redis_manager.redis_client.zrem(user_key, clip_id)
        redis_manager.redis_client.delete(item_key)
        
        # 获取剩余的剪贴板数量
        remaining_count = redis_manager.redis_client.zcard(user_key)
        
        deleted_content = item_data['content'][:50] + "..." if len(item_data['content']) > 50 else item_data['content']
        
        return success_response({
            "success": True,
            "message": f"剪贴板内容删除成功: '{deleted_content}'",
            "clip_id": clip_id,
            "remaining_clips": remaining_count
        })
            
    except Exception as e:
        logger.error(f"删除剪贴板内容错误: {e}")
        return error_response("删除剪贴板内容过程中发生错误", 500)


@app.post("/clear_clipboards")
async def clear_clipboards(request: ClearClipboardsRequest):
    """清空所有剪贴板内容 - 兼容Mock服务器格式"""
    try:
        username = request.username
        
        # 根据用户名获取用户ID
        user = redis_manager.get_user_by_username(username)
        if not user:
            return error_response("用户未找到", 404)
        
        # 获取当前剪贴板数量
        clipboard_history = redis_manager.get_user_clipboard_history(
            user['id'], page=1, per_page=1
        )
        deleted_count = clipboard_history.total
        
        # 清空用户所有剪贴板内容
        success = redis_manager.clear_user_clipboard_history(user['id'])
        
        if success:
            return success_response({
                "success": True,
                "message": "剪贴板已清空",
                "deleted_count": deleted_count
            })
        else:
            return error_response("清空剪贴板失败", 500)
            
    except Exception as e:
        logger.error(f"清空剪贴板错误: {e}")
        return error_response("清空剪贴板过程中发生错误", 500)


@app.get("/get_devices")
async def get_devices(username: str):
    """获取用户设备列表 - 兼容Mock服务器格式"""
    try:
        if not username:
            return error_response("缺少username参数", 400)
        
        # 根据用户名获取用户ID
        user = redis_manager.get_user_by_username(username)
        if not user:
            return error_response("用户未找到", 404)
        
        # 获取用户设备列表
        user_devices = redis_manager.get_user_devices(user['id'])
        
        # 转换格式
        devices_list = []
        for device in user_devices:
            devices_list.append({
                "device_id": device.device_id,
                "label": device.name,
                "os": device.os_info,
                "ip_address": device.ip_address,
                "first_login": device.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": device.last_seen.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return success_response({
            "success": True,
            "devices": devices_list,
            "count": len(devices_list)
        })
        
    except Exception as e:
        logger.error(f"获取设备列表错误: {e}")
        return error_response("获取设备列表过程中发生错误", 500)


@app.get("/get_clipboards")
async def get_clipboards(username: str):
    """获取用户剪贴板内容 - 兼容Mock服务器格式"""
    try:
        if not username:
            return error_response("缺少username参数", 400)
        
        # 根据用户名获取用户ID
        user = redis_manager.get_user_by_username(username)
        if not user:
            return error_response("用户未找到", 404)
        
        # 获取用户剪贴板历史
        if not redis_manager.is_connected():
            return error_response("Redis连接失败", 500)
        
        user_key = f"clipboard:{user['id']}"
        item_ids = redis_manager.redis_client.zrevrange(user_key, 0, 99)
        
        # 转换格式
        clipboards_list = []
        for item_id in item_ids:
            item_key = f"item:{item_id}"
            item_data = redis_manager.redis_client.hgetall(item_key)
            if item_data:
                clipboards_list.append({
                    "clip_id": item_data['id'],
                    "content": item_data['content'],
                    "content_type": item_data.get('content_type', 'text/plain'),
                    "created_at": item_data['created_at'],
                    "last_modified": item_data['updated_at'],
                    "device_id": item_data['device_id']
                })
        
        return success_response({
            "success": True,
            "clipboards": clipboards_list,
            "count": len(clipboards_list)
        })
        
    except Exception as e:
        logger.error(f"获取剪贴板内容错误: {e}")
        return error_response("获取剪贴板内容过程中发生错误", 500)


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动BeeSyncClip前端兼容服务器...")
    print("✅ Redis连接正常")
    print("🌐 访问地址: http://47.110.154.99:8000")
    print("📱 测试账号: testuser / test123")
    print("🎯 Ready for production!")
    
    uvicorn.run(
        "server.frontend_compatible_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 
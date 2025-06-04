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

from server.auth import auth_manager
from server.redis_manager import redis_manager
from shared.models import ClipboardItem, Device, User
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
            return error_response("用户名已存在", 409)
            
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
        
        # 创建剪贴板项
        clip_item = ClipboardItem(
            id=str(uuid.uuid4()),
            content=content,
            content_type=content_type,
            device_id=device_id,
            user_id=user.id
        )
        
        # 保存到Redis
        success = redis_manager.save_clipboard_item(clip_item)
        
        if success:
            # 获取用户所有剪贴板内容
            clipboard_history = redis_manager.get_user_clipboard_history(
                user.id, page=1, per_page=100
            )
            
            # 转换格式
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
                "message": "剪贴板内容添加成功",
                "clip_id": clip_item.id,
                "clipboards": clipboards_list
            }, 201)
        else:
            return error_response("添加剪贴板内容失败", 500)
            
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
        clip_item = redis_manager.get_clipboard_item(clip_id)
        if not clip_item:
            return error_response("剪贴板内容未找到", 404)
        
        # 删除剪贴板项
        success = redis_manager.delete_clipboard_item(clip_id)
        
        if success:
            # 获取剩余的剪贴板数量
            clipboard_history = redis_manager.get_user_clipboard_history(
                user.id, page=1, per_page=1
            )
            
            deleted_content = clip_item.content[:50] + "..." if len(clip_item.content) > 50 else clip_item.content
            
            return success_response({
                "success": True,
                "message": f"剪贴板内容删除成功: '{deleted_content}'",
                "clip_id": clip_id,
                "remaining_clips": clipboard_history.total
            })
        else:
            return error_response("删除剪贴板内容失败", 500)
            
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
            user.id, page=1, per_page=1
        )
        deleted_count = clipboard_history.total
        
        # 清空用户所有剪贴板内容
        success = redis_manager.clear_user_clipboard_history(user.id)
        
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
        user_devices = redis_manager.get_user_devices(user.id)
        
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
        clipboard_history = redis_manager.get_user_clipboard_history(
            user.id, page=1, per_page=100
        )
        
        # 转换格式
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
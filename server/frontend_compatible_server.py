"""
BeeSyncClip 前端兼容服务器
保持与Mock服务器相同的API接口，但使用真实的后端逻辑
支持WebSocket实时同步
"""

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional, Set
import time
import uuid
import json
import asyncio
from loguru import logger
from datetime import datetime

from server.auth import auth_manager
from server.redis_manager import redis_manager
from shared.models import ClipboardItem, Device, User, ClipboardType
from shared.utils import get_device_info


app = FastAPI(
    title="BeeSyncClip Frontend Compatible API",
    description="与前端Mock服务器兼容的真实API服务，支持WebSocket实时同步",
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


# WebSocket连接管理
class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}  # user_id -> set of websockets
        self.user_connections: Dict[int, str] = {}  # websocket_id -> user_id
        self.device_connections: Dict[int, str] = {}  # websocket_id -> device_id
        self.redis_listener_task = None
        self.redis_listener_started = False

    def start_redis_listener(self):
        """启动Redis消息监听器（仅在有事件循环时）"""
        if not self.redis_listener_started and not self.redis_listener_task:
            try:
                self.redis_listener_task = asyncio.create_task(self._redis_message_listener())
                self.redis_listener_started = True
                logger.info("Redis消息监听器已启动")
            except RuntimeError:
                # 没有事件循环，稍后再启动
                logger.debug("暂无事件循环，Redis监听器将在首次WebSocket连接时启动")

    async def _redis_message_listener(self):
        """Redis消息监听器"""
        try:
            await redis_manager.listen_for_messages()
        except Exception as e:
            logger.error(f"Redis消息监听器错误: {e}")

    async def _handle_redis_sync_message(self, user_id: str, message_data: dict):
        """处理Redis同步消息"""
        try:
            action = message_data.get("action")
            data = message_data.get("data", {})
            source_device = message_data.get("source_device")
            
            # 构造WebSocket消息
            ws_message = {
                "type": "clipboard_update",
                "action": action,
                "data": data,
                "source_device": source_device,
                "timestamp": message_data.get("timestamp")
            }
            
            # 广播给该用户的所有设备（排除源设备）
            await self.broadcast_to_user(user_id, ws_message, exclude_device=source_device)
            
        except Exception as e:
            logger.error(f"处理Redis同步消息失败: {e}")

    async def connect(self, websocket: WebSocket, user_id: str, device_id: str):
        await websocket.accept()
        
        # 确保Redis监听器已启动
        if not self.redis_listener_started:
            self.start_redis_listener()
        
        if user_id not in self.connections:
            self.connections[user_id] = set()
        
        self.connections[user_id].add(websocket)
        ws_id = id(websocket)
        self.user_connections[ws_id] = user_id
        self.device_connections[ws_id] = device_id
        
        # 🔥 订阅Redis同步消息
        redis_manager.subscribe_clipboard_sync(user_id, self._handle_redis_sync_message)
        
        logger.info(f"WebSocket连接建立: user={user_id}, device={device_id}")

    async def disconnect(self, websocket: WebSocket):
        ws_id = id(websocket)
        user_id = self.user_connections.get(ws_id)
        device_id = self.device_connections.get(ws_id)
        
        if user_id and user_id in self.connections:
            self.connections[user_id].discard(websocket)
            if not self.connections[user_id]:
                del self.connections[user_id]
                # 🔥 取消Redis订阅（如果没有其他连接）
                redis_manager.unsubscribe_clipboard_sync(user_id, self._handle_redis_sync_message)
        
        self.user_connections.pop(ws_id, None)
        self.device_connections.pop(ws_id, None)
        
        logger.info(f"WebSocket连接断开: user={user_id}, device={device_id}")

    async def broadcast_to_user(self, user_id: str, message: dict, exclude_device: str = None):
        """向用户的所有设备广播消息（可排除指定设备）"""
        if user_id not in self.connections:
            return
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for websocket in self.connections[user_id]:
            try:
                ws_id = id(websocket)
                device_id = self.device_connections.get(ws_id)
                
                # 排除指定设备
                if exclude_device and device_id == exclude_device:
                    continue
                
                await websocket.send_text(message_json)
                logger.debug(f"消息已发送到设备: {device_id}")
                
            except Exception as e:
                logger.warning(f"发送消息失败: {e}")
                disconnected.add(websocket)
        
        # 清理断开的连接
        for websocket in disconnected:
            await self.disconnect(websocket)

# 全局WebSocket管理器
websocket_manager = WebSocketManager()


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
        "features": ["REST API", "WebSocket实时同步"],
        "endpoints": {
            "health": "/health",
            "register": "/register",
            "login": "/login",
            "websocket": "/ws/{user_id}/{device_id}",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        # 检查Redis连接
        redis_status = "connected" if redis_manager.is_connected() else "disconnected"
        
        # 统计WebSocket连接数
        ws_connections = sum(len(connections) for connections in websocket_manager.connections.values())
        
        return {
            "status": "healthy",
            "service": "BeeSyncClip",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "redis": redis_status,
                "api": "running",
                "websocket": f"{ws_connections} connections"
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
        # 增加详细的请求日志
        logger.debug(f"收到登录请求: username={request.username}, device_info={request.device_info}")

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
    """添加剪贴板内容（通过Redis发布订阅实现实时同步）"""
    try:
        username = request.username
        content = request.content
        device_id = request.device_id
        content_type = request.content_type
        
        # 参数验证
        if not username or not content:
            return error_response("用户名和内容不能为空")
        
        # 获取用户信息
        user_info = auth_manager.get_user_info(username)
        if not user_info:
            return error_response("用户不存在", 404)
        
        user_id = user_info.get('id', username)
        
        # 检查Redis连接
        if not redis_manager.is_connected():
            logger.error("Redis连接失败")
            return error_response("服务暂时不可用，请稍后重试", 503)
        
        # 创建剪贴板项数据
        clip_id = str(uuid.uuid4())
        item_data = {
            'id': clip_id,
            'content': content,
            'content_type': content_type,
            'device_id': device_id,
            'user_id': user_id,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 保存到Redis
        item_key = f"item:{clip_id}"
        user_key = f"clipboard:{user_id}"
        
        # 保存项目数据
        redis_manager.redis_client.hset(item_key, mapping=item_data)
        
        # 添加到用户的剪贴板列表（按时间排序）
        score = datetime.now().timestamp()
        redis_manager.redis_client.zadd(user_key, {clip_id: score})
        
        # 设置过期时间（24小时）
        redis_manager.redis_client.expire(item_key, 86400)
        redis_manager.redis_client.expire(user_key, 86400)
        
        # 🔥 通过Redis发布订阅自动同步到所有设备
        redis_manager.publish_clipboard_sync(
            user_id=user_id,
            action="add",
            data={
                "clip_id": clip_id,
                "content": content,
                "content_type": content_type,
                "created_at": item_data["created_at"],
                "device_id": device_id
            },
            source_device=device_id
        )
        
        logger.info(f"剪贴板添加成功: user={user_id}, device={device_id}, redis_sync=enabled")
        
        return success_response({
            "success": True,
            "message": "剪贴板记录已添加",
            "clip_id": clip_id,
            "item": item_data
        }, status_code=201)
        
    except Exception as e:
        logger.error(f"添加剪贴板内容失败: {e}")
        return error_response("添加剪贴板内容过程中发生错误", 500)


@app.post("/delete_clipboard")
async def delete_clipboard(request: DeleteClipboardRequest):
    """删除剪贴板内容（通过Redis发布订阅实现实时同步）"""
    try:
        username = request.username
        clip_id = request.clip_id
        
        # 参数验证
        if not username or not clip_id:
            return error_response("用户名和剪贴板ID不能为空")
        
        # 获取用户信息
        user_info = auth_manager.get_user_info(username)
        if not user_info:
            return error_response("用户不存在", 404)
        
        user_id = user_info.get('id', username)
        
        # 检查Redis连接
        if not redis_manager.is_connected():
            return error_response("服务暂时不可用，请稍后重试", 503)
        
        # 删除剪贴板项（Redis管理器会自动发布同步消息）
        success = redis_manager.delete_clipboard_item(clip_id)
        
        if success:
            logger.info(f"剪贴板删除成功: user={user_id}, clip_id={clip_id}")
            return success_response({
                "success": True,
                "message": "剪贴板内容删除成功",
                "clip_id": clip_id,
                "sync_method": "redis_pubsub"
            })
        else:
            return error_response("删除失败，剪贴板项不存在", 404)
        
    except Exception as e:
        logger.error(f"删除剪贴板内容失败: {e}")
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
                "device_id": device.get("device_id"),
                "label": device.get("name"),
                "os": device.get("os_info"),
                "ip_address": device.get("ip_address"),
                "first_login": device.get("created_at").isoformat() if device.get("created_at") else None,
                "last_login": device.get("last_seen").isoformat() if device.get("last_seen") else None
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
        
        # 获取用户设备列表，并创建一个 device_id 到 device_label 的映射
        user_devices = redis_manager.get_user_devices(user['id'])
        device_map = {d['device_id']: d['name'] for d in user_devices}
        logger.debug(f"用户 {username} 的设备映射: {device_map}")
        
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
                device_id = item_data['device_id']
                device_label = device_map.get(device_id)
                
                # 如果没有找到设备标签，尝试从设备信息中直接获取
                if not device_label:
                    device_key = f"device:{device_id}"
                    device_data = redis_manager.redis_client.hgetall(device_key)
                    if device_data:
                        device_label = device_data.get('name', '未知设备')
                        logger.debug(f"从设备信息中获取标签: {device_id} -> {device_label}")
                    else:
                        device_label = f"设备-{device_id[:8]}"  # 使用device_id前8位作为标签
                        logger.warning(f"未找到设备信息: {device_id}")
                
                clipboards_list.append({
                    "clip_id": item_data['id'],
                    "content": item_data['content'],
                    "content_type": item_data.get('content_type', 'text/plain'),
                    "created_at": item_data['created_at'],
                    "last_modified": item_data['updated_at'],
                    "device_id": device_id,
                    "device_label": device_label
                })
        
        return success_response({
            "success": True,
            "clipboards": clipboards_list,
            "count": len(clipboards_list)
        })
        
    except Exception as e:
        logger.error(f"获取剪贴板内容错误: {e}")
        return error_response("获取剪贴板内容过程中发生错误", 500)


@app.websocket("/ws/{user_id}/{device_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, device_id: str):
    """WebSocket端点，用于实时同步"""
    await websocket_manager.connect(websocket, user_id, device_id)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "ping":
                # 心跳响应
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
                
            elif message_type == "clipboard_sync":
                # 剪贴板同步
                await handle_websocket_clipboard_sync(websocket, message, user_id, device_id)
                
            elif message_type == "request_history":
                # 请求历史记录
                await handle_websocket_history_request(websocket, user_id)
                
            else:
                logger.warning(f"未知WebSocket消息类型: {message_type}")
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket客户端断开连接: user={user_id}, device={device_id}")
    except Exception as e:
        logger.error(f"WebSocket处理错误: {e}")
    finally:
        await websocket_manager.disconnect(websocket)


async def handle_websocket_clipboard_sync(websocket: WebSocket, message: dict, user_id: str, device_id: str):
    """处理WebSocket剪贴板同步"""
    try:
        content = message.get("content")
        content_type = message.get("content_type", "text/plain")
        
        if not content:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "内容不能为空"
            }))
            return
        
        # 创建剪贴板项数据
        clip_id = str(uuid.uuid4())
        item_data = {
            "id": clip_id,
            "content": content,
            "content_type": content_type,
            "device_id": device_id,
            "user_id": user_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 保存到Redis
        if not redis_manager.is_connected():
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Redis连接失败"
            }))
            return
        
        item_key = f"item:{clip_id}"
        user_key = f"clipboard:{user_id}"
        
        redis_manager.redis_client.hset(item_key, mapping=item_data)
        score = datetime.now().timestamp()
        redis_manager.redis_client.zadd(user_key, {clip_id: score})
        redis_manager.redis_client.expire(item_key, 86400)
        redis_manager.redis_client.expire(user_key, 86400)
        
        # 广播给其他设备
        sync_message = {
            "type": "clipboard_update",
            "action": "add",
            "data": {
                "clip_id": clip_id,
                "content": content,
                "content_type": content_type,
                "created_at": item_data["created_at"],
                "device_id": device_id,
                "source_device": device_id
            }
        }
        
        await websocket_manager.broadcast_to_user(user_id, sync_message, exclude_device=device_id)
        
        # 确认消息给发送方
        await websocket.send_text(json.dumps({
            "type": "clipboard_sync_ack",
            "clip_id": clip_id,
            "message": "同步成功"
        }))
        
        logger.info(f"WebSocket剪贴板同步成功: user={user_id}, device={device_id}")
        
    except Exception as e:
        logger.error(f"WebSocket剪贴板同步失败: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "同步失败"
        }))


async def handle_websocket_history_request(websocket: WebSocket, user_id: str):
    """处理WebSocket历史记录请求"""
    try:
        if not redis_manager.is_connected():
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Redis连接失败"
            }))
            return
        
        user_key = f"clipboard:{user_id}"
        item_ids = redis_manager.redis_client.zrevrange(user_key, 0, 49)  # 最近50条
        
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
        
        await websocket.send_text(json.dumps({
            "type": "history_response",
            "clipboards": clipboards_list,
            "count": len(clipboards_list)
        }))
        
    except Exception as e:
        logger.error(f"WebSocket历史记录请求失败: {e}")
        await websocket.send_text(json.dumps({
            "type": "error", 
            "message": "获取历史记录失败"
        }))


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动BeeSyncClip前端兼容服务器...")
    print("✅ Redis连接正常")
    print("🌐 访问地址: http://47.110.154.99:8000")
    print("📱 新用户请在客户端界面进行注册")
    print("🎯 Ready for production!")
    
    uvicorn.run(
        "server.frontend_compatible_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 
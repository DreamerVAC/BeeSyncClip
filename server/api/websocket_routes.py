"""
WebSocket相关的路由
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Any, Set
import json
import asyncio
import time
from loguru import logger

from server.security import security_middleware, token_manager, encryption_manager
from server.redis_manager import redis_manager
from shared.models import ClipboardItem, ClipboardType
from shared.utils import calculate_checksum


websocket_router = APIRouter(tags=["WebSocket"])


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}  # user_id -> set of websockets
        self.user_connections: Dict[int, str] = {}  # websocket_id -> user_id
        self.device_connections: Dict[int, str] = {}  # websocket_id -> device_id
        self.redis_listener_task = None
        self.redis_listener_started = False

    def start_redis_listener(self):
        """启动Redis消息监听器"""
        if not self.redis_listener_started and not self.redis_listener_task:
            try:
                self.redis_listener_task = asyncio.create_task(self._redis_message_listener())
                self.redis_listener_started = True
                logger.info("Redis消息监听器已启动")
            except RuntimeError:
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
        """建立WebSocket连接"""
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
        
        # 订阅Redis同步消息
        redis_manager.subscribe_clipboard_sync(user_id, self._handle_redis_sync_message)
        
        # 设置设备在线状态
        redis_manager.set_device_online(user_id, device_id)
        
        logger.info(f"WebSocket连接建立: user={user_id}, device={device_id}")

    async def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        ws_id = id(websocket)
        user_id = self.user_connections.get(ws_id)
        device_id = self.device_connections.get(ws_id)
        
        if user_id and user_id in self.connections:
            self.connections[user_id].discard(websocket)
            if not self.connections[user_id]:
                del self.connections[user_id]
                # 取消Redis订阅（如果没有其他连接）
                redis_manager.unsubscribe_clipboard_sync(user_id, self._handle_redis_sync_message)
        
        self.user_connections.pop(ws_id, None)
        self.device_connections.pop(ws_id, None)
        
        # 设置设备离线状态
        if user_id and device_id:
            redis_manager.set_device_offline(user_id, device_id)
        
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

    async def send_to_device(self, user_id: str, device_id: str, message: dict):
        """向指定设备发送消息"""
        if user_id not in self.connections:
            return False
        
        message_json = json.dumps(message)
        
        for websocket in self.connections[user_id]:
            ws_id = id(websocket)
            if self.device_connections.get(ws_id) == device_id:
                try:
                    await websocket.send_text(message_json)
                    return True
                except Exception as e:
                    logger.error(f"向设备发送消息失败: {e}")
                    await self.disconnect(websocket)
                    return False
        
        return False


# 全局WebSocket管理器
websocket_manager = WebSocketManager()


@websocket_router.websocket("/ws/{user_id}/{device_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: str, 
    device_id: str,
    token: str = Query(...)
):
    """WebSocket连接端点"""
    try:
        # 验证token
        payload = token_manager.verify_token(token, 'access')
        if not payload:
            await websocket.close(code=4001, reason="Invalid token")
            return
        
        # 验证用户ID和设备ID
        if payload['user_id'] != user_id or payload['device_id'] != device_id:
            await websocket.close(code=4002, reason="User or device mismatch")
            return
        
        # 建立连接
        await websocket_manager.connect(websocket, user_id, device_id)
        
        try:
            while True:
                # 接收消息
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # 处理消息
                await handle_websocket_message(websocket, message, payload)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket客户端断开连接: user={user_id}, device={device_id}")
        except Exception as e:
            logger.error(f"WebSocket消息处理错误: {e}")
        finally:
            await websocket_manager.disconnect(websocket)
            
    except Exception as e:
        logger.error(f"WebSocket连接错误: {e}")
        try:
            await websocket.close(code=4000, reason="Connection error")
        except:
            pass


async def handle_websocket_message(websocket: WebSocket, message: dict, user_payload: dict):
    """处理WebSocket消息"""
    try:
        message_type = message.get("type")
        user_id = user_payload['user_id']
        device_id = user_payload['device_id']
        
        logger.debug(f"收到WebSocket消息: type={message_type}, user={user_id}")
        
        if message_type == "ping":
            # 心跳响应
            await websocket.send_text(json.dumps({
                "type": "pong",
                "timestamp": str(int(time.time()))
            }))
            
        elif message_type == "clipboard_sync":
            # 剪切板同步
            await handle_websocket_clipboard_sync(websocket, message, user_id, device_id)
            
        elif message_type == "request_history":
            # 请求历史记录
            await handle_websocket_history_request(websocket, user_id)
            
        elif message_type == "key_exchange":
            # 密钥交换
            await handle_websocket_key_exchange(websocket, message, user_id)
            
        else:
            logger.warning(f"未知WebSocket消息类型: {message_type}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "未知消息类型"
            }))
            
    except Exception as e:
        logger.error(f"处理WebSocket消息失败: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "消息处理失败"
        }))


async def handle_websocket_clipboard_sync(websocket: WebSocket, message: dict, user_id: str, device_id: str):
    """处理剪切板同步"""
    try:
        clipboard_data = message.get("data", {})
        
        # 处理加密数据
        if clipboard_data.get("encrypted"):
            try:
                content = encryption_manager.decrypt_clipboard_content(
                    clipboard_data.get("content", {}), user_id
                )
            except Exception as e:
                logger.error(f"解密剪切板内容失败: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "数据解密失败"
                }))
                return
        else:
            content = clipboard_data.get("content", "")
        
        # 验证内容大小
        if len(content) > 10 * 1024 * 1024:  # 10MB限制
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "内容过大，超过10MB限制"
            }))
            return
        
        # 创建剪切板项
        clipboard_item = ClipboardItem(
            type=ClipboardType(clipboard_data.get("content_type", "text/plain")),
            content=content,
            metadata={
                "source": "websocket",
                "encrypted": clipboard_data.get("encrypted", False)
            },
            size=len(content.encode('utf-8')),
            device_id=device_id,
            user_id=user_id,
            checksum=calculate_checksum(content)
        )
        
        # 保存到Redis
        if redis_manager.save_clipboard_item(clipboard_item):
            # 发布同步消息给其他设备
            sync_message = {
                "action": "add",
                "data": {
                    "id": clipboard_item.id,
                    "content": content,
                    "content_type": clipboard_data.get("content_type", "text/plain"),
                    "timestamp": clipboard_item.timestamp.isoformat(),
                    "device_id": device_id,
                    "checksum": clipboard_item.checksum
                },
                "source_device": device_id,
                "timestamp": clipboard_item.timestamp.isoformat()
            }
            
            redis_manager.publish_clipboard_sync(user_id, sync_message['action'], sync_message['data'], sync_message.get('source_device'))
            
            # 确认消息
            await websocket.send_text(json.dumps({
                "type": "sync_success",
                "clip_id": clipboard_item.id
            }))
            
            logger.info(f"WebSocket剪切板同步成功: user={user_id}, size={clipboard_item.size}")
        else:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "保存剪切板内容失败"
            }))
            
    except Exception as e:
        logger.error(f"WebSocket剪切板同步失败: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "剪切板同步失败"
        }))


async def handle_websocket_history_request(websocket: WebSocket, user_id: str):
    """处理历史记录请求"""
    try:
        # 获取剪切板历史
        history = redis_manager.get_user_clipboard_history(user_id, page=1, per_page=20)
        
        # 格式化历史记录
        history_data = [
            {
                "id": item.id,
                "content": item.content,
                "content_type": item.type.value,
                "timestamp": item.timestamp.isoformat(),
                "device_id": item.device_id,
                "size": item.size,
                "checksum": item.checksum
            }
            for item in history.items
        ]
        
        await websocket.send_text(json.dumps({
            "type": "history_response",
            "data": {
                "items": history_data,
                "total": history.total,
                "page": history.page,
                "per_page": history.per_page
            }
        }))
        
        logger.debug(f"WebSocket历史记录已发送: user={user_id}, count={len(history_data)}")
        
    except Exception as e:
        logger.error(f"WebSocket历史记录请求失败: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "获取历史记录失败"
        }))


async def handle_websocket_key_exchange(websocket: WebSocket, message: dict, user_id: str):
    """处理密钥交换"""
    try:
        encrypted_session_key = message.get("data", {}).get("encrypted_session_key")
        
        if not encrypted_session_key:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "缺少加密的会话密钥"
            }))
            return
        
        # 解密会话密钥
        session_key = encryption_manager.decrypt_with_server_key(encrypted_session_key)
        
        # 存储会话密钥
        encryption_manager.user_session_keys[user_id] = session_key
        
        await websocket.send_text(json.dumps({
            "type": "key_exchange_success",
            "message": "密钥交换成功"
        }))
        
        logger.info(f"WebSocket密钥交换成功: user={user_id}")
        
    except Exception as e:
        logger.error(f"WebSocket密钥交换失败: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "密钥交换失败"
        })) 
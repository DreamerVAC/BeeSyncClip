"""
BeeSyncClip WebSocket 服务器
"""

import json
import asyncio
import websockets
from typing import Set, Dict, Any
from datetime import datetime
from loguru import logger

from shared.models import WebSocketMessage, SyncEvent, ClipboardItem, ClipboardType
from shared.utils import config_manager, calculate_checksum
from server.auth import auth_manager
from server.redis_manager import redis_manager


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.connections: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        self.user_connections: Dict[str, str] = {}  # websocket -> user_id
        self.device_connections: Dict[str, str] = {}  # websocket -> device_id
    
    async def register_connection(self, websocket: websockets.WebSocketServerProtocol, 
                                user_id: str, device_id: str):
        """注册WebSocket连接"""
        if user_id not in self.connections:
            self.connections[user_id] = set()
        
        self.connections[user_id].add(websocket)
        self.user_connections[id(websocket)] = user_id
        self.device_connections[id(websocket)] = device_id
        
        # 更新设备在线状态
        redis_manager.set_device_online(user_id, device_id)
        
        logger.info(f"WebSocket连接已注册: user_id={user_id}, device_id={device_id}")
    
    async def unregister_connection(self, websocket: websockets.WebSocketServerProtocol):
        """注销WebSocket连接"""
        ws_id = id(websocket)
        user_id = self.user_connections.get(ws_id)
        device_id = self.device_connections.get(ws_id)
        
        if user_id and user_id in self.connections:
            self.connections[user_id].discard(websocket)
            if not self.connections[user_id]:
                del self.connections[user_id]
        
        self.user_connections.pop(ws_id, None)
        self.device_connections.pop(ws_id, None)
        
        if user_id and device_id:
            # 设置设备离线
            device_key = f"device:{device_id}"
            if redis_manager.is_connected():
                redis_manager.redis_client.hset(device_key, 'is_online', 'false')
        
        logger.info(f"WebSocket连接已注销: user_id={user_id}, device_id={device_id}")
    
    async def broadcast_to_user(self, user_id: str, message: WebSocketMessage, 
                              exclude_device: str = None):
        """向用户的所有设备广播消息（可排除指定设备）"""
        if user_id not in self.connections:
            return
        
        message_json = message.json()
        disconnected = set()
        
        for websocket in self.connections[user_id]:
            try:
                ws_id = id(websocket)
                device_id = self.device_connections.get(ws_id)
                
                # 排除指定设备
                if exclude_device and device_id == exclude_device:
                    continue
                
                await websocket.send(message_json)
                logger.debug(f"消息已发送到设备: {device_id}")
                
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
                logger.warning(f"检测到断开的连接: {device_id}")
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                disconnected.add(websocket)
        
        # 清理断开的连接
        for websocket in disconnected:
            await self.unregister_connection(websocket)
    
    async def send_to_device(self, user_id: str, device_id: str, message: WebSocketMessage):
        """向指定设备发送消息"""
        if user_id not in self.connections:
            return False
        
        for websocket in self.connections[user_id]:
            ws_id = id(websocket)
            if self.device_connections.get(ws_id) == device_id:
                try:
                    await websocket.send(message.json())
                    return True
                except Exception as e:
                    logger.error(f"向设备发送消息失败: {e}")
                    await self.unregister_connection(websocket)
                    return False
        
        return False


# 全局WebSocket管理器
ws_manager = WebSocketManager()


async def handle_websocket_message(websocket: websockets.WebSocketServerProtocol, 
                                 message_data: dict, user_info: dict):
    """处理WebSocket消息"""
    try:
        message = WebSocketMessage(**message_data)
        user_id = user_info['user_id']
        device_id = user_info['device_id']
        
        logger.debug(f"收到消息: type={message.type}, user={user_id}")
        
        if message.type == "ping":
            # 心跳响应
            pong_message = WebSocketMessage(type="pong", data={"timestamp": datetime.now().isoformat()})
            await websocket.send(pong_message.json())
            
        elif message.type == "sync":
            # 剪切板同步
            await handle_clipboard_sync(websocket, message, user_id, device_id)
            
        elif message.type == "request_history":
            # 请求历史记录
            await handle_history_request(websocket, message, user_id)
            
        else:
            logger.warning(f"未知消息类型: {message.type}")
            
    except Exception as e:
        logger.error(f"处理WebSocket消息失败: {e}")
        error_message = WebSocketMessage(
            type="error", 
            data={"message": "消息处理失败"}
        )
        await websocket.send(error_message.json())


async def handle_clipboard_sync(websocket: websockets.WebSocketServerProtocol, 
                               message: WebSocketMessage, user_id: str, device_id: str):
    """处理剪切板同步"""
    try:
        clipboard_data = message.data.get('clipboard_item')
        if not clipboard_data:
            return
        
        # 创建剪切板项
        clipboard_item = ClipboardItem(
            type=ClipboardType(clipboard_data['type']),
            content=clipboard_data['content'],
            metadata=clipboard_data.get('metadata', {}),
            size=len(clipboard_data['content'].encode('utf-8')),
            device_id=device_id,
            user_id=user_id,
            checksum=calculate_checksum(clipboard_data['content'])
        )
        
        # 检查数据大小限制
        max_size = config_manager.get('clipboard.max_data_size', 10485760)
        if clipboard_item.size > max_size:
            error_message = WebSocketMessage(
                type="error",
                data={"message": f"数据过大，超过限制 {max_size} 字节"}
            )
            await websocket.send(error_message.json())
            return
        
        # 保存到Redis
        if redis_manager.save_clipboard_item(clipboard_item):
            # 创建同步事件
            sync_event = SyncEvent(
                event_type="created",
                clipboard_item=clipboard_item
            )
            
            # 广播给用户的其他设备
            sync_message = WebSocketMessage(
                type="sync",
                data={
                    "event": sync_event.dict(),
                    "source_device": device_id
                }
            )
            
            await ws_manager.broadcast_to_user(user_id, sync_message, exclude_device=device_id)
            logger.info(f"剪切板同步成功: user={user_id}, type={clipboard_item.type}")
            
            # 发送确认消息
            confirm_message = WebSocketMessage(
                type="sync_confirm",
                data={"item_id": clipboard_item.id, "status": "success"}
            )
            await websocket.send(confirm_message.json())
        else:
            error_message = WebSocketMessage(
                type="error",
                data={"message": "保存剪切板数据失败"}
            )
            await websocket.send(error_message.json())
            
    except Exception as e:
        logger.error(f"处理剪切板同步失败: {e}")
        error_message = WebSocketMessage(
            type="error",
            data={"message": "同步处理失败"}
        )
        await websocket.send(error_message.json())


async def handle_history_request(websocket: websockets.WebSocketServerProtocol, 
                                message: WebSocketMessage, user_id: str):
    """处理历史记录请求"""
    try:
        page = message.data.get('page', 1)
        per_page = message.data.get('per_page', 20)
        
        # 获取历史记录
        history = redis_manager.get_user_clipboard_history(user_id, page, per_page)
        
        # 发送历史记录
        history_message = WebSocketMessage(
            type="history",
            data={
                "items": [item.dict() for item in history.items],
                "total": history.total,
                "page": history.page,
                "per_page": history.per_page
            }
        )
        
        await websocket.send(history_message.json())
        logger.debug(f"历史记录已发送: user={user_id}, page={page}")
        
    except Exception as e:
        logger.error(f"处理历史记录请求失败: {e}")
        error_message = WebSocketMessage(
            type="error",
            data={"message": "获取历史记录失败"}
        )
        await websocket.send(error_message.json())


async def websocket_handler(websocket: websockets.WebSocketServerProtocol, path: str):
    """WebSocket连接处理器"""
    logger.info(f"新的WebSocket连接: {websocket.remote_address}")
    
    try:
        # 等待认证消息
        auth_message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
        auth_data = json.loads(auth_message)
        
        if auth_data.get('type') != 'auth':
            await websocket.close(code=1008, reason="需要认证")
            return
        
        # 验证token
        token = auth_data.get('token')
        if not token:
            await websocket.close(code=1008, reason="缺少认证token")
            return
        
        user_info = auth_manager.get_user_by_token(token)
        if not user_info:
            await websocket.close(code=1008, reason="认证失败")
            return
        
        # 注册连接
        await ws_manager.register_connection(
            websocket, 
            user_info['user_id'], 
            user_info['device_id']
        )
        
        # 发送认证成功消息
        auth_success = WebSocketMessage(
            type="auth_success",
            data={"message": "认证成功", "user_id": user_info['user_id']}
        )
        await websocket.send(auth_success.json())
        
        # 处理后续消息
        async for message in websocket:
            try:
                message_data = json.loads(message)
                await handle_websocket_message(websocket, message_data, user_info)
            except json.JSONDecodeError:
                logger.warning("收到无效的JSON消息")
            except Exception as e:
                logger.error(f"处理消息时发生错误: {e}")
        
    except asyncio.TimeoutError:
        logger.warning("WebSocket认证超时")
        await websocket.close(code=1008, reason="认证超时")
    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket连接已关闭")
    except Exception as e:
        logger.error(f"WebSocket处理错误: {e}")
    finally:
        await ws_manager.unregister_connection(websocket)


async def start_websocket_server():
    """启动WebSocket服务器"""
    host = config_manager.get('websocket.host', 'localhost')
    port = config_manager.get('websocket.port', 8765)
    
    logger.info(f"启动WebSocket服务器: {host}:{port}")
    
    server = await websockets.serve(
        websocket_handler,
        host,
        port,
        ping_interval=config_manager.get('websocket.ping_interval', 20),
        ping_timeout=config_manager.get('websocket.ping_timeout', 10),
        max_size=config_manager.get('clipboard.max_data_size', 10485760)
    )
    
    logger.info("WebSocket服务器启动成功")
    return server


if __name__ == "__main__":
    asyncio.run(start_websocket_server()) 
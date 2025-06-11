"""
BeeSyncClip Redis 数据管理器
支持发布订阅实时同步
"""

import json
import redis
import asyncio
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from loguru import logger

from shared.models import ClipboardItem, ClipboardHistory
from shared.utils import config_manager


class RedisManager:
    """Redis 数据管理器"""
    
    def __init__(self):
        self.redis_client = None
        self.pubsub_client = None
        self.pubsub = None
        self.subscribers = {}  # user_id -> callback functions
        self.connect()
    
    def connect(self) -> bool:
        """连接到 Redis"""
        try:
            redis_config = config_manager.get('redis', {})
            
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                password=redis_config.get('password'),
                db=redis_config.get('db', 0),
                decode_responses=redis_config.get('decode_responses', True),
                socket_timeout=redis_config.get('socket_timeout', 5),
                retry_on_timeout=redis_config.get('retry_on_timeout', True)
            )
            
            # 创建发布订阅客户端
            self.pubsub_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                password=redis_config.get('password'),
                db=redis_config.get('db', 0),
                decode_responses=redis_config.get('decode_responses', True)
            )
            
            # 测试连接
            self.redis_client.ping()
            self.pubsub_client.ping()
            
            # 初始化发布订阅
            self.pubsub = self.pubsub_client.pubsub()
            
            logger.info("Redis 连接成功")
            return True
            
        except Exception as e:
            logger.error(f"Redis 连接失败: {e}")
            return False
    
    def is_connected(self) -> bool:
        """检查 Redis 连接状态"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except:
            pass
        return False

    def publish_clipboard_sync(self, user_id: str, action: str, data: dict, source_device: str = None):
        """发布剪贴板同步消息"""
        try:
            if not self.is_connected():
                logger.error("Redis未连接，无法发布消息")
                return False
            
            message = {
                "action": action,  # add, delete, clear
                "data": data,
                "source_device": source_device,
                "timestamp": datetime.now().isoformat()
            }
            
            channel = f"clipboard_sync:{user_id}"
            self.redis_client.publish(channel, json.dumps(message))
            
            logger.debug(f"发布同步消息: user={user_id}, action={action}")
            return True
            
        except Exception as e:
            logger.error(f"发布同步消息失败: {e}")
            return False

    def subscribe_clipboard_sync(self, user_id: str, callback: Callable):
        """订阅剪贴板同步消息"""
        try:
            if not self.is_connected():
                logger.error("Redis未连接，无法订阅")
                return False
            
            channel = f"clipboard_sync:{user_id}"
            
            # 保存回调函数
            if user_id not in self.subscribers:
                self.subscribers[user_id] = []
            self.subscribers[user_id].append(callback)
            
            # 订阅频道
            self.pubsub.subscribe(channel)
            
            logger.info(f"订阅剪贴板同步: user={user_id}")
            return True
            
        except Exception as e:
            logger.error(f"订阅剪贴板同步失败: {e}")
            return False

    def unsubscribe_clipboard_sync(self, user_id: str, callback: Callable = None):
        """取消订阅剪贴板同步"""
        try:
            channel = f"clipboard_sync:{user_id}"
            
            if callback and user_id in self.subscribers:
                # 移除特定回调
                if callback in self.subscribers[user_id]:
                    self.subscribers[user_id].remove(callback)
                
                # 如果没有回调了，取消订阅
                if not self.subscribers[user_id]:
                    self.pubsub.unsubscribe(channel)
                    del self.subscribers[user_id]
            else:
                # 取消所有订阅
                self.pubsub.unsubscribe(channel)
                self.subscribers.pop(user_id, None)
            
            logger.info(f"取消订阅剪贴板同步: user={user_id}")
            return True
            
        except Exception as e:
            logger.error(f"取消订阅失败: {e}")
            return False

    async def listen_for_messages(self):
        """监听Redis发布订阅消息"""
        try:
            if not self.pubsub:
                return
            
            while True:
                message = self.pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    try:
                        # 解析消息
                        channel = message['channel']
                        data = json.loads(message['data'])
                        
                        # 提取用户ID
                        user_id = channel.split(':')[1]
                        
                        # 调用回调函数
                        if user_id in self.subscribers:
                            for callback in self.subscribers[user_id]:
                                try:
                                    if asyncio.iscoroutinefunction(callback):
                                        await callback(user_id, data)
                                    else:
                                        callback(user_id, data)
                                except Exception as e:
                                    logger.error(f"回调函数执行失败: {e}")
                    
                    except Exception as e:
                        logger.error(f"处理订阅消息失败: {e}")
                
                await asyncio.sleep(0.01)  # 避免CPU占用过高
                
        except Exception as e:
            logger.error(f"监听订阅消息失败: {e}")

    def save_clipboard_item(self, item: ClipboardItem) -> bool:
        """保存剪切板项"""
        try:
            if not self.is_connected():
                logger.error("Redis 未连接")
                return False
            
            # 使用有序集合存储用户的剪切板历史
            user_key = f"clipboard:{item.user_id}"
            item_key = f"item:{item.id}"
            
            # 保存具体的剪切板项数据
            item_data = item.dict()
            item_data['created_at'] = item.created_at.isoformat()
            item_data['updated_at'] = item.updated_at.isoformat()
            
            # 序列化metadata为JSON字符串
            if 'metadata' in item_data and isinstance(item_data['metadata'], dict):
                item_data['metadata'] = json.dumps(item_data['metadata'])
            
            # 兼容原始API：添加content_type字段
            metadata = item.metadata if isinstance(item.metadata, dict) else {}
            if 'original_content_type' in metadata:
                item_data['content_type'] = metadata['original_content_type']
            else:
                # 如果没有原始类型，根据type转换
                type_to_content_type = {
                    'text': 'text/plain',
                    'image': 'image/png',
                    'file': 'application/octet-stream',
                    'html': 'text/html',
                    'rtf': 'text/rtf'
                }
                item_data['content_type'] = type_to_content_type.get(item.type.value, 'text/plain')
            
            # 确保所有值都是Redis可接受的类型
            for key, value in item_data.items():
                if isinstance(value, (dict, list)):
                    item_data[key] = json.dumps(value)
                elif value is None:
                    item_data[key] = ""
            
            self.redis_client.hset(item_key, mapping=item_data)
            
            # 添加到用户的有序集合中（按时间戳排序）
            score = item.created_at.timestamp()
            self.redis_client.zadd(user_key, {item.id: score})
            
            # 设置过期时间
            expire_time = config_manager.get('clipboard.expire_time', 86400)
            self.redis_client.expire(item_key, expire_time)
            self.redis_client.expire(user_key, expire_time)
            
            # 限制历史记录数量
            max_history = config_manager.get('clipboard.max_history', 1000)
            self.redis_client.zremrangebyrank(user_key, 0, -(max_history + 1))
            
            # 🔥 发布同步消息
            self.publish_clipboard_sync(
                user_id=item.user_id,
                action="add",
                data={
                    "clip_id": item.id,
                    "content": item.content,
                    "content_type": item.type.value if hasattr(item.type, 'value') else str(item.type),
                    "created_at": item.created_at.isoformat(),
                    "device_id": item.device_id
                },
                source_device=item.device_id
            )
            
            logger.debug(f"保存剪切板项成功: {item.id}")
            return True
            
        except Exception as e:
            logger.error(f"保存剪切板项失败: {e}")
            return False
    
    def get_clipboard_item(self, item_id: str) -> Optional[ClipboardItem]:
        """获取指定的剪切板项"""
        try:
            if not self.is_connected():
                return None
            
            item_key = f"item:{item_id}"
            item_data = self.redis_client.hgetall(item_key)
            
            if not item_data:
                return None
            
            # 兼容旧数据: 将 'content_type' 映射到 'type'
            if 'content_type' in item_data and 'type' not in item_data:
                content_type = item_data.pop('content_type')
                # 映射 content_type 到 ClipboardType 枚举值
                if content_type in ['text/plain', 'text']:
                    item_data['type'] = 'text'
                elif content_type in ['image/png', 'image/jpeg', 'image']:
                    item_data['type'] = 'image'
                elif content_type in ['application/octet-stream', 'file']:
                    item_data['type'] = 'file'
                elif content_type in ['text/html', 'html']:
                    item_data['type'] = 'html'
                elif content_type in ['text/rtf', 'rtf']:
                    item_data['type'] = 'rtf'
                else:
                    # 默认为text类型
                    item_data['type'] = 'text'

            # 转换时间字段
            if 'created_at' in item_data:
                if isinstance(item_data['created_at'], str):
                    item_data['created_at'] = datetime.fromisoformat(item_data['created_at'])
            
            if 'updated_at' in item_data:
                if isinstance(item_data['updated_at'], str):
                    item_data['updated_at'] = datetime.fromisoformat(item_data['updated_at'])
            else:
                # 如果没有updated_at字段，使用created_at的值
                item_data['updated_at'] = item_data.get('created_at', datetime.now())
            
            # 转换元数据
            if 'metadata' in item_data and isinstance(item_data['metadata'], str):
                item_data['metadata'] = json.loads(item_data['metadata'])
            elif 'metadata' not in item_data:
                item_data['metadata'] = {}
            
            # 确保必需字段存在
            if 'size' not in item_data:
                item_data['size'] = len(item_data.get('content', ''))
            
            if 'checksum' not in item_data:
                item_data['checksum'] = None
            
            return ClipboardItem(**item_data)
            
        except Exception as e:
            logger.error(f"获取剪切板项失败: {e}")
            return None
    
    def get_user_clipboard_history(self, user_id: str, page: int = 1, 
                                 per_page: int = 50) -> ClipboardHistory:
        """获取用户的剪切板历史（优化版本，避免N+1查询）"""
        try:
            if not self.is_connected():
                return ClipboardHistory(items=[], total=0, page=page, per_page=per_page)
            
            user_key = f"clipboard:{user_id}"
            
            # 获取总数
            total = self.redis_client.zcard(user_key)
            
            # 计算分页
            start = (page - 1) * per_page
            end = start + per_page - 1
            
            # 获取指定范围的项目ID（按时间倒序）
            item_ids = self.redis_client.zrevrange(user_key, start, end)
            
            if not item_ids:
                return ClipboardHistory(items=[], total=total, page=page, per_page=per_page)
            
            # 🚀 批量获取剪切板项，避免N+1查询问题
            items = self._batch_get_clipboard_items(item_ids)
            
            return ClipboardHistory(
                items=items,
                total=total,
                page=page,
                per_page=per_page
            )
            
        except Exception as e:
            logger.error(f"获取用户剪切板历史失败: {e}")
            return ClipboardHistory(items=[], total=0, page=page, per_page=per_page)
    
    def _batch_get_clipboard_items(self, item_ids: List[str]) -> List[ClipboardItem]:
        """批量获取剪切板项，优化性能"""
        try:
            if not item_ids:
                return []
            
            # 使用pipeline批量获取，减少Redis往返次数
            pipe = self.redis_client.pipeline()
            
            for item_id in item_ids:
                item_key = f"item:{item_id}"
                pipe.hgetall(item_key)
            
            results = pipe.execute()
            
            items = []
            for i, item_data in enumerate(results):
                if not item_data:
                    continue
                
                try:
                    # 兼容处理
                    if 'content_type' in item_data and 'type' not in item_data:
                        content_type = item_data.pop('content_type')
                        # 映射到枚举值
                        if content_type in ['text/plain', 'text']:
                            item_data['type'] = 'text'
                        elif content_type in ['image/png', 'image/jpeg', 'image']:
                            item_data['type'] = 'image'
                        elif content_type in ['application/octet-stream', 'file']:
                            item_data['type'] = 'file'
                        elif content_type in ['text/html', 'html']:
                            item_data['type'] = 'html'
                        elif content_type in ['text/rtf', 'rtf']:
                            item_data['type'] = 'rtf'
                        else:
                            item_data['type'] = 'text'
                        
                        # 保存原始content_type到metadata
                        if 'metadata' not in item_data:
                            item_data['metadata'] = {}
                        elif isinstance(item_data['metadata'], str):
                            item_data['metadata'] = json.loads(item_data['metadata'])
                        
                        if isinstance(item_data['metadata'], dict):
                            item_data['metadata']['original_content_type'] = content_type
                    
                    # 处理时间字段
                    if 'created_at' in item_data and isinstance(item_data['created_at'], str):
                        item_data['created_at'] = datetime.fromisoformat(item_data['created_at'])
                    
                    if 'updated_at' in item_data and isinstance(item_data['updated_at'], str):
                        item_data['updated_at'] = datetime.fromisoformat(item_data['updated_at'])
                    elif 'updated_at' not in item_data:
                        item_data['updated_at'] = item_data.get('created_at', datetime.now())
                    
                    # 处理metadata
                    if 'metadata' in item_data and isinstance(item_data['metadata'], str):
                        item_data['metadata'] = json.loads(item_data['metadata'])
                    elif 'metadata' not in item_data:
                        item_data['metadata'] = {}
                    
                    # 确保必需字段
                    if 'size' not in item_data:
                        item_data['size'] = len(item_data.get('content', ''))
                    if 'checksum' not in item_data:
                        item_data['checksum'] = None
                    
                    item = ClipboardItem(**item_data)
                    items.append(item)
                    
                except Exception as e:
                    logger.error(f"解析剪切板项失败 {item_ids[i]}: {e}")
                    continue
            
            return items
            
        except Exception as e:
            logger.error(f"批量获取剪切板项失败: {e}")
            return []
    
    def delete_clipboard_item(self, item_id: str) -> bool:
        """删除指定的剪切板项（重载版本，不需要user_id）"""
        try:
            if not self.is_connected():
                return False
            
            item_key = f"item:{item_id}"
            
            # 获取项目数据以找到用户ID
            item_data = self.redis_client.hgetall(item_key)
            if not item_data:
                return False
            
            user_id = item_data.get('user_id')
            if user_id:
                # 从用户的有序集合中删除
                user_key = f"clipboard:{user_id}"
                self.redis_client.zrem(user_key, item_id)
            
            # 删除具体的项目数据
            self.redis_client.delete(item_key)
            
            # 🔥 发布删除同步消息
            if item_data and user_id:
                self.publish_clipboard_sync(
                    user_id=user_id,
                    action="delete",
                    data={
                        "clip_id": item_id,
                        "device_id": item_data.get('device_id')
                    },
                    source_device=item_data.get('device_id')
                )
            
            logger.debug(f"删除剪切板项成功: {item_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除剪切板项失败: {e}")
            return False
    
    def get_latest_clipboard_item(self, user_id: str) -> Optional[ClipboardItem]:
        """获取用户最新的剪切板项"""
        try:
            if not self.is_connected():
                return None
            
            user_key = f"clipboard:{user_id}"
            
            # 获取最新的项目ID
            latest_ids = self.redis_client.zrevrange(user_key, 0, 0)
            
            if not latest_ids:
                return None
            
            return self.get_clipboard_item(latest_ids[0])
            
        except Exception as e:
            logger.error(f"获取最新剪切板项失败: {e}")
            return None
    
    def set_device_online(self, user_id: str, device_id: str) -> bool:
        """设置设备在线状态"""
        try:
            if not self.is_connected():
                return False
            
            device_key = f"device:{device_id}"
            self.redis_client.hset(device_key, mapping={
                'user_id': user_id,
                'last_seen': datetime.now().isoformat(),
                'is_online': 'true'
            })
            
            # 设置过期时间（心跳超时）
            self.redis_client.expire(device_key, 60)
            
            # 添加到在线设备集合
            online_devices_key = f"online_devices:{user_id}"
            self.redis_client.sadd(online_devices_key, device_id)
            self.redis_client.expire(online_devices_key, 60)
            
            return True
            
        except Exception as e:
            logger.error(f"设置设备在线状态失败: {e}")
            return False
    
    def get_online_devices(self, user_id: str) -> List[str]:
        """获取用户的在线设备列表"""
        try:
            if not self.is_connected():
                return []
            
            online_devices_key = f"online_devices:{user_id}"
            return list(self.redis_client.smembers(online_devices_key))
            
        except Exception as e:
            logger.error(f"获取在线设备列表失败: {e}")
            return []
    
    def is_device_online(self, user_id: str, device_id: str) -> bool:
        """检查设备是否在线"""
        try:
            if not self.is_connected():
                return False
            
            online_devices_key = f"online_devices:{user_id}"
            return self.redis_client.sismember(online_devices_key, device_id)
            
        except Exception as e:
            logger.error(f"检查设备在线状态失败: {e}")
            return False
    
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """根据用户名获取用户信息"""
        try:
            if not self.is_connected():
                return None
            
            # 首先通过用户名索引获取用户ID
            user_key = f"user:username:{username}"
            user_id = self.redis_client.get(user_key)
            
            if not user_id:
                return None
            
            # 然后获取用户详细信息
            user_data_key = f"user:{user_id}"
            user_data = self.redis_client.hgetall(user_data_key)
            
            if not user_data:
                return None
            
            return {
                'id': user_data.get('id'),
                'username': user_data.get('username'),
                'email': user_data.get('email'),
                'created_at': user_data.get('created_at'),
                'is_active': user_data.get('is_active', 'True') == 'True'
            }
            
        except Exception as e:
            logger.error(f"根据用户名获取用户失败: {e}")
            return None
    
    def get_total_users_count(self) -> int:
        """获取用户总数"""
        try:
            if not self.is_connected():
                return 0
            
            # 统计所有user:*键的数量
            user_keys = self.redis_client.keys("user:*")
            return len(user_keys)
            
        except Exception as e:
            logger.error(f"获取用户总数失败: {e}")
            return 0
    
    def get_user_devices(self, user_id: str) -> List[dict]:
        """获取用户设备列表"""
        try:
            if not self.is_connected():
                logger.error("Redis未连接")
                return []
            
            devices_key = f"devices:{user_id}"
            device_ids = self.redis_client.smembers(devices_key)
            logger.debug(f"获取用户设备列表: user_id={user_id}, device_ids={device_ids}")
            
            devices = []
            for device_id in device_ids:
                device_key = f"device:{device_id}"
                device_data = self.redis_client.hgetall(device_key)
                logger.debug(f"设备数据: device_id={device_id}, data={device_data}")
                
                if device_data:
                    # 转换时间字段
                    from datetime import datetime
                    try:
                        created_at = device_data.get('created_at')
                        last_seen = device_data.get('last_seen')
                        
                        device_info = {
                            'device_id': device_id,
                            'name': device_data.get('name', 'Unknown Device'),
                            'os_info': device_data.get('os_info', 'Unknown'),
                            'ip_address': device_data.get('ip_address', '0.0.0.0'),
                            'created_at': datetime.fromisoformat(created_at) if created_at else datetime.now(),
                            'last_seen': datetime.fromisoformat(last_seen) if last_seen else datetime.now()
                        }
                        devices.append(device_info)
                        logger.debug(f"设备信息已添加: {device_info}")
                    except Exception as time_error:
                        logger.error(f"时间字段解析失败: {time_error}, device_data={device_data}")
                        # 如果时间解析失败，使用默认值
                        device_info = {
                            'device_id': device_id,
                            'name': device_data.get('name', 'Unknown Device'),
                            'os_info': device_data.get('os_info', 'Unknown'),
                            'ip_address': device_data.get('ip_address', '0.0.0.0'),
                            'created_at': datetime.now(),
                            'last_seen': datetime.now()
                        }
                        devices.append(device_info)
                        logger.debug(f"设备信息已添加 (默认时间): {device_info}")
                else:
                    logger.warning(f"设备数据为空: device_id={device_id}")
            
            logger.debug(f"最终设备列表: {devices}")
            return devices
            
        except Exception as e:
            logger.error(f"获取用户设备列表失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            return []
    
    def update_device_name(self, device_id: str, new_name: str) -> bool:
        """更新设备名称"""
        try:
            if not self.is_connected():
                return False
            
            device_key = f"device:{device_id}"
            
            # 检查设备是否存在
            if not self.redis_client.exists(device_key):
                return False
            
            # 更新设备名称
            self.redis_client.hset(device_key, "name", new_name)
            
            logger.debug(f"更新设备名称成功: {device_id} -> {new_name}")
            return True
            
        except Exception as e:
            logger.error(f"更新设备名称失败: {e}")
            return False
    
    def remove_device(self, device_id: str) -> bool:
        """删除设备"""
        try:
            if not self.is_connected():
                return False
            
            device_key = f"device:{device_id}"
            
            # 获取设备所属用户
            device_data = self.redis_client.hgetall(device_key)
            if not device_data:
                return False
            
            user_id = device_data.get('user_id')
            if user_id:
                # 从用户设备集合中删除
                devices_key = f"devices:{user_id}"
                self.redis_client.srem(devices_key, device_id)
                # 从在线设备集合中删除
                self.redis_client.srem(f"online_devices:{user_id}", device_id)
            
            # 删除设备信息
            self.redis_client.delete(device_key)
            
            logger.debug(f"删除设备成功: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除设备失败: {e}")
            return False
    
    def delete_device_clipboard_items(self, device_id: str) -> int:
        """删除指定设备的所有剪贴板项"""
        try:
            if not self.is_connected():
                return 0
            
            deleted_count = 0
            
            # 查找所有剪贴板项
            item_keys = self.redis_client.keys("item:*")
            
            for item_key in item_keys:
                item_data = self.redis_client.hgetall(item_key)
                if item_data.get('device_id') == device_id:
                    # 从用户的剪贴板历史中删除
                    user_id = item_data.get('user_id')
                    if user_id:
                        item_id = item_key.split(':')[1]
                        user_key = f"clipboard:{user_id}"
                        self.redis_client.zrem(user_key, item_id)
                    
                    # 删除项目数据
                    self.redis_client.delete(item_key)
                    deleted_count += 1
            
            logger.debug(f"删除设备剪贴板项: {device_id}, 数量: {deleted_count}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"删除设备剪贴板项失败: {e}")
            return 0
    
    def clear_user_clipboard_history(self, user_id: str) -> bool:
        """清空用户所有剪贴板历史"""
        try:
            if not self.is_connected():
                return False
            
            user_key = f"clipboard:{user_id}"
            
            # 获取所有剪贴板项ID
            item_ids = self.redis_client.zrange(user_key, 0, -1)
            
            # 删除所有剪贴板项数据
            for item_id in item_ids:
                item_key = f"item:{item_id}"
                self.redis_client.delete(item_key)
            
            # 清空用户的剪贴板有序集合
            self.redis_client.delete(user_key)
            
            logger.debug(f"清空用户剪贴板历史: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"清空用户剪贴板历史失败: {e}")
            return False
    
    def clean_orphaned_clipboard_items(self, user_id: str) -> int:
        """清理引用不存在设备的剪贴板项"""
        try:
            if not self.is_connected():
                return 0
            
            # 获取用户的有效设备列表
            valid_devices = set()
            user_devices = self.get_user_devices(user_id)
            for device in user_devices:
                if device.get('device_id'):
                    valid_devices.add(device['device_id'])
            
            user_key = f"clipboard:{user_id}"
            item_ids = self.redis_client.zrange(user_key, 0, -1)
            
            cleaned_count = 0
            for item_id in item_ids:
                item_key = f"item:{item_id}"
                item_data = self.redis_client.hgetall(item_key)
                
                if item_data:
                    device_id = item_data.get('device_id')
                    # 如果设备ID不存在或不在有效设备列表中，删除此剪贴板项
                    if not device_id or device_id not in valid_devices:
                        # 从用户集合中删除
                        self.redis_client.zrem(user_key, item_id)
                        # 删除项目数据
                        self.redis_client.delete(item_key)
                        cleaned_count += 1
                        logger.debug(f"清理无效剪贴板项: {item_id}, device_id={device_id}")
            
            if cleaned_count > 0:
                logger.info(f"清理完成: user_id={user_id}, cleaned_items={cleaned_count}")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理无效剪贴板项失败: {e}")
            return 0
    
    def get_user_clipboard_stats(self, user_id: str) -> Dict[str, Any]:
        """获取用户剪切板统计信息"""
        try:
            if not self.is_connected():
                return {"total": 0, "today": 0, "this_week": 0}
            
            user_key = f"clipboard:{user_id}"
            total = self.redis_client.zcard(user_key)
            
            # 简化统计，只返回总数
            return {
                "total": total,
                "today": 0,  # 可以后续实现
                "this_week": 0  # 可以后续实现
            }
            
        except Exception as e:
            logger.error(f"获取用户剪切板统计失败: {e}")
            return {"total": 0, "today": 0, "this_week": 0}
    
    def close(self):
        """关闭Redis连接"""
        try:
            # 取消所有订阅
            if self.pubsub:
                self.pubsub.close()
                self.pubsub = None
            
            # 关闭Redis客户端连接
            if self.redis_client:
                self.redis_client.close()
                self.redis_client = None
            
            if self.pubsub_client:
                self.pubsub_client.close()
                self.pubsub_client = None
            
            # 清空订阅者
            self.subscribers.clear()
            
            logger.info("Redis连接已关闭")
            
        except Exception as e:
            logger.error(f"关闭Redis连接失败: {e}")


# 全局 Redis 管理器实例
redis_manager = RedisManager() 
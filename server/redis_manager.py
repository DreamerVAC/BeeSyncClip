"""
BeeSyncClip Redis 数据管理器
"""

import json
import redis
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from shared.models import ClipboardItem, ClipboardHistory
from shared.utils import config_manager


class RedisManager:
    """Redis 数据管理器"""
    
    def __init__(self):
        self.redis_client = None
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
            
            # 测试连接
            self.redis_client.ping()
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
            
            # 转换时间字段
            if 'created_at' in item_data:
                item_data['created_at'] = datetime.fromisoformat(item_data['created_at'])
            
            # 转换元数据
            if 'metadata' in item_data and isinstance(item_data['metadata'], str):
                item_data['metadata'] = json.loads(item_data['metadata'])
            
            return ClipboardItem(**item_data)
            
        except Exception as e:
            logger.error(f"获取剪切板项失败: {e}")
            return None
    
    def get_user_clipboard_history(self, user_id: str, page: int = 1, 
                                 per_page: int = 50) -> ClipboardHistory:
        """获取用户的剪切板历史"""
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
            
            # 获取具体的剪切板项
            items = []
            for item_id in item_ids:
                item = self.get_clipboard_item(item_id)
                if item:
                    items.append(item)
            
            return ClipboardHistory(
                items=items,
                total=total,
                page=page,
                per_page=per_page
            )
            
        except Exception as e:
            logger.error(f"获取用户剪切板历史失败: {e}")
            return ClipboardHistory(items=[], total=0, page=page, per_page=per_page)
    
    def delete_clipboard_item(self, user_id: str, item_id: str) -> bool:
        """删除指定的剪切板项"""
        try:
            if not self.is_connected():
                return False
            
            user_key = f"clipboard:{user_id}"
            item_key = f"item:{item_id}"
            
            # 从用户的有序集合中删除
            self.redis_client.zrem(user_key, item_id)
            
            # 删除具体的项目数据
            self.redis_client.delete(item_key)
            
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
                return []
            
            devices_key = f"devices:{user_id}"
            device_ids = self.redis_client.smembers(devices_key)
            
            devices = []
            for device_id in device_ids:
                device_key = f"device:{device_id}"
                device_data = self.redis_client.hgetall(device_key)
                
                if device_data:
                    # 转换时间字段
                    from datetime import datetime
                    device_info = {
                        'device_id': device_id,
                        'name': device_data.get('name', 'Unknown Device'),
                        'os_info': device_data.get('os_info', 'Unknown'),
                        'ip_address': device_data.get('ip_address', '0.0.0.0'),
                        'created_at': datetime.fromisoformat(device_data.get('created_at', datetime.now().isoformat())),
                        'last_seen': datetime.fromisoformat(device_data.get('last_seen', datetime.now().isoformat()))
                    }
                    devices.append(device_info)
            
            return devices
            
        except Exception as e:
            logger.error(f"获取用户设备列表失败: {e}")
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
            
            logger.debug(f"删除剪切板项成功: {item_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除剪切板项失败: {e}")
            return False


# 全局 Redis 管理器实例
redis_manager = RedisManager() 
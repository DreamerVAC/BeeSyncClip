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


# 全局 Redis 管理器实例
redis_manager = RedisManager() 
# BeeSyncClip 剪贴板数据库设计 🗄️

## 📋 概述

BeeSyncClip使用Redis作为主要数据存储，实现高性能的剪贴板数据管理和跨设备同步。

## 🏗️ 数据架构

### 数据模型层次结构

```
用户 (User)
├── 设备 (Device) - 多个
└── 剪贴板历史 (Clipboard History)
    └── 剪贴板项 (Clipboard Item) - 多个
```

## 📊 数据模型定义

### 1. ClipboardItem (剪贴板项)

```python
class ClipboardItem(BaseModel):
    id: str                        # 唯一标识符 (UUID)
    type: ClipboardType           # 内容类型 (text/image/file/html/rtf)
    content: str                  # 内容或base64编码数据
    metadata: Dict[str, Any]      # 元数据 (文件名、尺寸等)
    size: int                     # 数据大小 (字节)
    created_at: datetime          # 创建时间
    device_id: str               # 来源设备ID
    user_id: str                 # 所属用户ID
    checksum: Optional[str]       # 数据校验和 (防重复)
```

### 2. 支持的内容类型

```python
class ClipboardType(str, Enum):
    TEXT = "text"      # 纯文本
    IMAGE = "image"    # 图片 (base64编码)
    FILE = "file"      # 文件路径列表
    HTML = "html"      # 富文本HTML
    RTF = "rtf"        # 富文本格式
```

## 🔑 Redis存储设计

### 存储结构

```
Redis Keys:
├── clipboard:{user_id}           # 用户剪贴板历史索引 (ZSet)
├── item:{item_id}               # 具体剪贴板项数据 (Hash)
├── user:{username}              # 用户基础信息 (Hash)
├── device:{device_id}           # 设备信息 (Hash)
└── online_devices:{user_id}     # 在线设备集合 (Set)
```

### 1. 剪贴板历史索引 (ZSet)

**Key**: `clipboard:{user_id}`

```redis
ZADD clipboard:user123 1702982400 "item-uuid-1"
ZADD clipboard:user123 1702982500 "item-uuid-2"
ZADD clipboard:user123 1702982600 "item-uuid-3"

# Score = timestamp (时间戳)
# Member = item_id (剪贴板项ID)
```

**优势**:
- ✅ 按时间自动排序
- ✅ 支持范围查询和分页
- ✅ O(log N) 插入性能
- ✅ 自动去重

### 2. 剪贴板项数据 (Hash)

**Key**: `item:{item_id}`

```redis
HSET item:uuid-123 
  "id" "uuid-123"
  "type" "text"
  "content" "Hello World"
  "metadata" "{}"
  "size" "11"
  "created_at" "2024-12-19T10:30:00"
  "device_id" "device-456"
  "user_id" "user-789"
  "checksum" "abc123def"
```

### 3. 用户信息 (Hash)

**Key**: `user:{username}`

```redis
HSET user:testuser
  "id" "user-789"
  "username" "testuser"
  "password_hash" "$2b$12$..."
  "created_at" "2024-12-19T10:00:00"
```

## 🚀 核心功能实现

### 1. 保存剪贴板项

```python
def save_clipboard_item(self, item: ClipboardItem) -> bool:
    """
    保存剪贴板项到Redis
    
    实现步骤:
    1. 保存具体数据到 item:{item_id}
    2. 添加索引到 clipboard:{user_id} ZSet
    3. 设置过期时间 (默认24小时)
    4. 限制历史记录数量 (默认1000条)
    """
    try:
        # 1. 保存具体数据
        item_key = f"item:{item.id}"
        item_data = item.dict()
        item_data['created_at'] = item.created_at.isoformat()
        self.redis_client.hset(item_key, mapping=item_data)
        
        # 2. 添加到时间序列索引
        user_key = f"clipboard:{item.user_id}"
        score = item.created_at.timestamp()
        self.redis_client.zadd(user_key, {item.id: score})
        
        # 3. 设置过期时间
        expire_time = config_manager.get('clipboard.expire_time', 86400)
        self.redis_client.expire(item_key, expire_time)
        self.redis_client.expire(user_key, expire_time)
        
        # 4. 限制历史记录数量
        max_history = config_manager.get('clipboard.max_history', 1000)
        self.redis_client.zremrangebyrank(user_key, 0, -(max_history + 1))
        
        return True
    except Exception as e:
        logger.error(f"保存失败: {e}")
        return False
```

### 2. 获取历史记录 (分页)

```python
def get_user_clipboard_history(self, user_id: str, page: int = 1, 
                             per_page: int = 50) -> ClipboardHistory:
    """
    获取用户剪贴板历史 (分页)
    
    实现步骤:
    1. 从 clipboard:{user_id} 获取总数
    2. 计算分页范围
    3. 按时间倒序获取项目ID列表
    4. 批量获取具体剪贴板项数据
    """
    try:
        user_key = f"clipboard:{user_id}"
        
        # 1. 获取总数
        total = self.redis_client.zcard(user_key)
        
        # 2. 计算分页
        start = (page - 1) * per_page
        end = start + per_page - 1
        
        # 3. 获取项目ID (按时间倒序)
        item_ids = self.redis_client.zrevrange(user_key, start, end)
        
        # 4. 批量获取数据
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
        logger.error(f"获取历史失败: {e}")
        return ClipboardHistory(items=[], total=0)
```

### 3. 删除剪贴板项

```python
def delete_clipboard_item(self, user_id: str, item_id: str) -> bool:
    """
    删除剪贴板项
    
    实现步骤:
    1. 从索引中删除 (ZSet)
    2. 删除具体数据 (Hash)
    """
    try:
        user_key = f"clipboard:{user_id}"
        item_key = f"item:{item_id}"
        
        # 1. 从索引中删除
        self.redis_client.zrem(user_key, item_id)
        
        # 2. 删除具体数据
        self.redis_client.delete(item_key)
        
        return True
    except Exception as e:
        logger.error(f"删除失败: {e}")
        return False
```

## ⚡ 性能优化

### 1. 时间复杂度分析

| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| 保存项目 | O(log N) | ZSet插入 |
| 获取历史 | O(log N + M) | 范围查询 + M个Hash查询 |
| 删除项目 | O(log N) | ZSet删除 + Hash删除 |
| 获取最新 | O(log N) | ZSet范围查询 |

### 2. 内存优化策略

#### 过期策略
```python
# 自动过期 (24小时)
expire_time = config_manager.get('clipboard.expire_time', 86400)
self.redis_client.expire(item_key, expire_time)

# 数量限制 (最多1000条)
max_history = config_manager.get('clipboard.max_history', 1000)
self.redis_client.zremrangebyrank(user_key, 0, -(max_history + 1))
```

#### 数据压缩
```python
# 大文件内容可以使用压缩
import gzip
import base64

def compress_content(content: str) -> str:
    """压缩内容"""
    compressed = gzip.compress(content.encode('utf-8'))
    return base64.b64encode(compressed).decode('utf-8')

def decompress_content(compressed: str) -> str:
    """解压缩内容"""
    data = base64.b64decode(compressed.encode('utf-8'))
    return gzip.decompress(data).decode('utf-8')
```

### 3. 并发控制

#### 乐观锁防重复
```python
def save_clipboard_item_safe(self, item: ClipboardItem) -> bool:
    """
    使用校验和防止重复保存相同内容
    """
    try:
        # 检查是否已存在相同内容
        if item.checksum:
            existing_key = f"checksum:{item.checksum}"
            if self.redis_client.exists(existing_key):
                logger.debug(f"内容已存在，跳过保存: {item.checksum}")
                return True
            
            # 设置校验和标记
            self.redis_client.set(existing_key, item.id, ex=86400)
        
        return self.save_clipboard_item(item)
    except Exception as e:
        logger.error(f"安全保存失败: {e}")
        return False
```

## 🔄 实时同步机制

### 1. WebSocket事件

```python
class SyncEvent(BaseModel):
    event_type: str              # created, updated, deleted
    clipboard_item: ClipboardItem
    timestamp: datetime
```

### 2. 发布订阅

```python
# 发布剪贴板更新事件
def publish_clipboard_event(self, user_id: str, event: SyncEvent):
    """发布剪贴板事件到所有在线设备"""
    channel = f"clipboard_sync:{user_id}"
    message = event.json()
    self.redis_client.publish(channel, message)

# 订阅剪贴板事件
def subscribe_clipboard_events(self, user_id: str):
    """订阅剪贴板同步事件"""
    pubsub = self.redis_client.pubsub()
    channel = f"clipboard_sync:{user_id}"
    pubsub.subscribe(channel)
    return pubsub
```

## 📈 监控和统计

### 1. 数据统计

```python
def get_clipboard_stats(self, user_id: str) -> Dict[str, Any]:
    """获取剪贴板使用统计"""
    user_key = f"clipboard:{user_id}"
    
    total_items = self.redis_client.zcard(user_key)
    
    # 按类型统计
    type_stats = {}
    item_ids = self.redis_client.zrevrange(user_key, 0, -1)
    
    for item_id in item_ids:
        item = self.get_clipboard_item(item_id)
        if item:
            item_type = item.type
            type_stats[item_type] = type_stats.get(item_type, 0) + 1
    
    return {
        'total_items': total_items,
        'type_distribution': type_stats,
        'storage_used': self._calculate_storage_usage(user_id)
    }
```

### 2. 性能监控

```python
import time
from functools import wraps

def monitor_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} 执行时间: {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败: {e}, 时间: {duration:.3f}s")
            raise
    return wrapper
```

## 🔒 安全性考虑

### 1. 数据加密
```python
from cryptography.fernet import Fernet

class EncryptedClipboard:
    def __init__(self, encryption_key: bytes):
        self.cipher = Fernet(encryption_key)
    
    def encrypt_content(self, content: str) -> str:
        """加密剪贴板内容"""
        encrypted = self.cipher.encrypt(content.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_content(self, encrypted_content: str) -> str:
        """解密剪贴板内容"""
        encrypted_bytes = base64.b64decode(encrypted_content.encode('utf-8'))
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
```

### 2. 访问控制
```python
def check_access_permission(self, user_id: str, item_id: str) -> bool:
    """检查用户是否有权访问指定剪贴板项"""
    item = self.get_clipboard_item(item_id)
    return item and item.user_id == user_id
```

## 🎯 配置参数

```yaml
# config/settings.yaml
clipboard:
  expire_time: 86400        # 过期时间 (秒)
  max_history: 1000         # 最大历史记录数
  max_content_size: 10485760  # 最大内容大小 (10MB)
  enable_compression: true   # 启用压缩
  enable_encryption: false  # 启用加密

redis:
  host: "localhost"
  port: 6379
  db: 0
  password: null
  socket_timeout: 5
  retry_on_timeout: true
```

---

## 📋 总结

BeeSyncClip的剪贴板数据库设计具有以下特点：

✅ **高性能**: Redis ZSet实现O(log N)操作  
✅ **可扩展**: 支持分页、过期、限制等策略  
✅ **实时性**: WebSocket + 发布订阅实现实时同步  
✅ **安全性**: 支持加密、访问控制、数据校验  
✅ **监控性**: 完整的性能监控和统计功能  

这种设计能够支持大规模用户和高并发访问，同时保证数据的一致性和安全性。 
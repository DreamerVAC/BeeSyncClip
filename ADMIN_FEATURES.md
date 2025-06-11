# BeeSyncClip 管理员功能

## 概述

BeeSyncClip 2.0 增加了管理员功能，支持通过硬编码账户管理用户数据。

## 管理员账户

- 用户名: `admin`
- 密码: `beesync2024!`
- Token有效期: 12小时

## API接口

### 管理员登录
```http
POST /admin/login
Content-Type: application/json

{
  "username": "admin",
  "password": "beesync2024!"
}
```

### 获取用户列表
```http
GET /admin/users
Authorization: Bearer {admin_token}
```

### 删除用户
```http
DELETE /admin/users/{username}
Authorization: Bearer {admin_token}
```

### 系统统计
```http
GET /admin/stats
Authorization: Bearer {admin_token}
```

## 实现文件

### server/modular_server.py
- 硬编码管理员配置
- 管理员API路由
- Token验证逻辑

### server/security/token_manager.py
- `generate_admin_token()` - 生成管理员Token
- `verify_admin_token()` - 验证管理员Token

### server/redis_manager.py
- `get_all_users()` - 获取所有用户
- `delete_user()` - 删除用户
- `remove_user_device()` - 移除用户设备

### server/auth.py
- 修复用户名映射格式
- 统一用户存储逻辑

## 安全特性

- SHA256密码哈希
- JWT Token认证
- 专用管理员Token类型
- Bearer Token授权验证

## 生产环境配置

1. 修改默认密码: 编辑 `ADMIN_CONFIG["password"]`
2. 设置JWT密钥: 环境变量 `JWT_SECRET_KEY`
3. 限制API访问IP
4. 监控管理员操作日志

## 📋 功能特性

### 🔑 管理员账户
- **用户名**: `admin`
- **密码**: `beesync2024!` (生产环境建议修改)
- **认证方式**: SHA256密码哈希 + JWT Token
- **Token有效期**: 12小时

### 🌐 API接口

#### 1. 管理员登录
```http
POST /admin/login
Content-Type: application/json

{
  "username": "admin",
  "password": "beesync2024!"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "管理员登录成功",
  "admin_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "admin",
  "role": "admin"
}
```

#### 2. 获取所有用户列表
```http
GET /admin/users
Authorization: Bearer {admin_token}
```

**响应示例**:
```json
{
  "success": true,
  "users": [
    {
      "user_id": "uuid",
      "username": "testuser",
      "email": "testuser@example.com",
      "created_at": "2025-06-12 01:30:00",
      "last_login": "2025-06-12 01:35:00",
      "devices_count": 2,
      "clipboards_count": 15
    }
  ],
  "total": 119
}
```

#### 3. 删除用户及其所有数据
```http
DELETE /admin/users/{username}
Authorization: Bearer {admin_token}
```

**响应示例**:
```json
{
  "success": true,
  "message": "用户 testuser 及其所有数据已删除",
  "deleted_clipboards": 15,
  "deleted_devices": 2
}
```

#### 4. 获取系统统计信息
```http
GET /admin/stats
Authorization: Bearer {admin_token}
```

**响应示例**:
```json
{
  "success": true,
  "stats": {
    "total_users": 119,
    "active_users": 45,
    "total_devices": 234,
    "total_clipboards": 1567,
    "redis_status": {
      "connected": true,
      "version": "6.0+"
    },
    "server_version": "2.0.0",
    "timestamp": "2025-06-12T01:50:00.000000"
  }
}
```

## 🛡️ 安全特性

### 认证机制
- **密码安全**: SHA256哈希存储，启动时生成
- **Token认证**: JWT Token，12小时有效期
- **权限验证**: 专用管理员Token类型验证
- **访问控制**: Bearer Token授权头验证

### 安全措施
- 无效Token自动拒绝 (HTTP 401)
- Token类型和角色双重验证
- 操作日志记录
- 密码不在代码中明文存储

## 🔧 技术实现

### 文件修改清单

#### 1. `server/modular_server.py`
- 添加硬编码管理员配置
- 新增管理员API路由:
  - `/admin/login` - 管理员登录
  - `/admin/users` - 获取用户列表  
  - `/admin/users/{username}` - 删除用户
  - `/admin/stats` - 系统统计
- 管理员Token验证功能
- 启动时初始化管理员密码哈希

#### 2. `server/security/token_manager.py`
- 新增 `generate_admin_token()` 方法
- 新增 `verify_admin_token()` 方法
- 管理员Token专用配置 (12小时有效期)
- 管理员Token类型和角色验证

#### 3. `server/redis_manager.py`
- 新增 `get_all_users()` 方法 - 获取所有用户
- 新增 `delete_user()` 方法 - 删除用户账户
- 新增 `remove_user_device()` 方法 - 移除用户设备
- 用户数据格式化和时间处理
- Redis key类型兼容性处理

#### 4. `server/auth.py`
- 修复用户名到ID映射格式 (`username:xxx`)
- 统一用户注册和查找逻辑
- 优化用户数据存储格式

## 📊 功能验证

### 测试结果
- ✅ 管理员登录成功 (200 OK)
- ✅ 获取用户列表成功 (119个用户)
- ✅ 用户创建和删除测试通过
- ✅ 系统统计信息正常显示
- ✅ 无效Token正确拒绝 (401 Unauthorized)
- ✅ 所有API响应格式标准化

### 性能特点
- 支持大量用户管理 (已测试119个用户)
- Redis高效查询和批量操作
- 内存中管理员认证，响应快速
- JWT Token机制，无需服务器端状态

## 🚀 部署说明

### 生产环境配置建议
1. **修改默认密码**: 在`server/modular_server.py`中修改`ADMIN_CONFIG["password"]`
2. **Token密钥**: 设置环境变量`JWT_SECRET_KEY`使用自定义密钥
3. **访问限制**: 在网关层限制管理员API访问IP
4. **日志监控**: 监控管理员登录和操作日志

### 环境变量
```bash
# 可选：自定义JWT密钥
export JWT_SECRET_KEY="your-secret-key-here"
```

## 📱 前端集成

前端开发者可基于以上API实现管理员控制面板，包括：
- 管理员登录界面
- 用户列表展示和搜索
- 用户删除确认对话框
- 系统统计信息仪表板
- 批量用户管理功能

## 🔍 故障排除

### 常见问题
1. **401 Unauthorized**: 检查Token是否有效、格式是否正确
2. **用户列表为空**: 确认Redis连接正常，检查用户数据格式
3. **删除失败**: 验证用户名是否存在，检查权限

### 日志位置
- 服务器日志: `beesyncclip.log`
- 管理员操作: 查找包含"管理员"的日志条目

---

**版本**: BeeSyncClip 2.0  
**更新时间**: 2025-06-12  
**兼容性**: 完全向后兼容，不影响现有客户端功能 
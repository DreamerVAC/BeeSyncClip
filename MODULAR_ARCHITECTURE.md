# BeeSyncClip 模块化架构说明

## 🎯 概述

BeeSyncClip 服务器已完成模块化、标准化改造，并实现了完整的加密功能。新架构提供了更好的安全性、可维护性和扩展性。

## 🏗️ 架构设计

### 模块结构

```
server/
├── security/                    # 安全模块
│   ├── __init__.py             # 模块初始化
│   ├── encryption.py           # 加密管理器 (AES-256, RSA-2048)
│   ├── token_manager.py        # JWT Token管理器
│   └── security_middleware.py  # 安全中间件
├── api/                        # API路由模块
│   ├── __init__.py             # 模块初始化
│   ├── auth_routes.py          # 认证相关路由
│   ├── clipboard_routes.py     # 剪切板相关路由
│   ├── device_routes.py        # 设备管理路由
│   └── websocket_routes.py     # WebSocket路由
├── modular_server.py           # 模块化服务器主文件
├── frontend_compatible_server.py  # 原前端兼容服务器
├── redis_manager.py            # Redis管理器
└── auth.py                     # 认证管理器
```

## 🔐 安全功能

### 1. 加密系统
- **AES-256-CBC**: 对称加密，用于数据传输加密
- **RSA-2048**: 非对称加密，用于密钥交换
- **PBKDF2**: 密码哈希，100,000次迭代
- **数据完整性**: SHA-256校验和验证

### 2. 认证系统
- **JWT Token**: 访问令牌，24小时有效期
- **Refresh Token**: 刷新令牌，30天有效期
- **Token黑名单**: 支持令牌吊销
- **设备绑定**: Token与设备ID绑定

### 3. 安全中间件
- **速率限制**: 每分钟60次请求限制
- **安全头**: 完整的HTTP安全头
- **请求验证**: 自动认证和权限检查
- **安全事件记录**: 详细的安全日志

## 🚀 新功能特性

### 1. 模块化路由
- `/auth/*` - 认证相关接口
- `/clipboard/*` - 剪切板管理接口
- `/devices/*` - 设备管理接口
- `/ws/*` - WebSocket连接

### 2. 加密API
- `GET /auth/public-key` - 获取服务器公钥
- `POST /auth/key-exchange` - 密钥交换
- `GET /security/info` - 安全配置信息

### 3. 健康检查
- `GET /health` - 服务健康状态
- `GET /` - 服务基本信息

## 📡 API接口

### 认证接口
```
POST /auth/register     - 用户注册
POST /auth/login        - 用户登录
POST /auth/logout       - 用户登出
POST /auth/refresh      - 刷新Token
GET  /auth/profile      - 获取用户信息
GET  /auth/public-key   - 获取公钥
POST /auth/key-exchange - 密钥交换
```

### 剪切板接口
```
POST /clipboard/add     - 添加剪切板内容
GET  /clipboard/list    - 获取剪切板历史
GET  /clipboard/latest  - 获取最新内容
DELETE /clipboard/{id}  - 删除指定内容
POST /clipboard/clear   - 清空剪切板
GET  /clipboard/stats   - 获取统计信息
```

### 设备管理接口
```
GET  /devices/list           - 获取设备列表
PUT  /devices/update-label   - 更新设备标签
DELETE /devices/{id}         - 移除设备
GET  /devices/{id}/status    - 获取设备状态
GET  /devices/stats          - 获取设备统计
```

### WebSocket接口
```
WS /ws/{user_id}/{device_id}?token={jwt_token}
```

## 🔧 启动方式

### 模块化服务器
```bash
# 新的模块化服务器（推荐）
python3 start_modular_server.py

# 或直接运行
python3 -m server.modular_server
```

### 兼容性服务器
```bash
# 原前端兼容服务器（保持兼容）
python3 start_frontend_server.py
```

## 🛡️ 安全特性

### 数据加密流程
1. **密钥交换**: 客户端使用服务器公钥加密会话密钥
2. **会话建立**: 服务器解密并存储用户会话密钥
3. **数据传输**: 使用AES-256加密所有敏感数据
4. **完整性验证**: SHA-256校验和确保数据完整性

### 认证流程
1. **用户注册/登录**: 密码使用PBKDF2哈希
2. **Token生成**: 生成JWT访问令牌和刷新令牌
3. **请求认证**: 每个API请求验证JWT令牌
4. **权限检查**: 验证用户对资源的访问权限

### 安全防护
- **速率限制**: 防止暴力攻击
- **Token黑名单**: 支持令牌吊销
- **安全头**: 防止XSS、CSRF等攻击
- **输入验证**: 严格的数据验证
- **错误处理**: 安全的错误信息返回

## 📊 性能优化

### 缓存策略
- **Redis缓存**: 用户会话、设备状态
- **内存缓存**: 加密密钥、Token黑名单
- **连接池**: Redis连接复用

### 异步处理
- **FastAPI**: 异步Web框架
- **WebSocket**: 实时双向通信
- **异步Redis**: 非阻塞数据库操作

## 🔄 兼容性

### 向后兼容
- 保留原有API接口路径
- 兼容现有客户端
- 渐进式迁移支持

### 前端适配
- 支持加密和非加密模式
- 自动检测客户端能力
- 优雅降级机制

## 📈 监控和日志

### 安全监控
- 登录失败记录
- 异常访问检测
- 速率限制触发
- Token异常使用

### 性能监控
- 请求处理时间
- Redis连接状态
- 内存使用情况
- 错误率统计

## 🚀 部署建议

### 生产环境
1. **HTTPS**: 启用SSL/TLS加密
2. **防火墙**: 限制端口访问
3. **负载均衡**: 多实例部署
4. **监控告警**: 实时状态监控

### 安全配置
1. **环境变量**: 敏感配置外部化
2. **密钥管理**: 定期轮换密钥
3. **访问控制**: 限制CORS域名
4. **日志审计**: 完整的操作日志

## 📝 更新日志

### v2.0.0 (当前版本)
- ✅ 完整的模块化架构
- ✅ AES-256 + RSA-2048 加密
- ✅ JWT认证系统
- ✅ 安全中间件
- ✅ 速率限制
- ✅ WebSocket实时同步
- ✅ 完整的API文档
- ✅ 健康检查接口
- ✅ 向后兼容支持

### 下一步计划
- 🔄 数据库持久化
- 🔄 集群部署支持
- 🔄 更多加密算法
- �� 审计日志系统
- 🔄 管理后台界面 
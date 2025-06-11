# 🐝 BeeSyncClip - 跨平台剪贴板同步工具

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-GUI-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-red.svg)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-Cache-orange.svg)](https://redis.io/)
[![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-blue.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)


## ✨ 核心功能

- 🔄 **跨设备同步**: 使用 WebSocket 和 Redis Pub/Sub 实现跨设备剪贴板同步
- 🖥️ **桌面客户端**: 基于 PyQt5 的跨平台桌面应用，支持 Windows、macOS、Linux
- 📋 **剪贴板管理**: 提供剪贴板历史记录的查看、搜索和管理功能
- 🔐 **企业级安全**: AES-256加密 + JWT认证，保障数据传输安全
- ⚡ **双服务器架构**: 
  - 🔥 **模块化服务器 v2.0** (推荐): 企业级安全、性能优化、完全兼容
  - 📦 **原始服务器 v1.0**: 传统版本，稳定运行
- 🚀 **性能优化**: 批量查询优化，解决多设备同步卡顿，性能提升20%
- 📦 **简化部署**: 统一的启动脚本简化服务器和客户端的启动流程

## 🚀 快速入门

### 1. 准备环境

确保您的系统已安装 `Python 3.8+` 和 `pip`。

### 2. 客户端使用 (推荐)

这是最简单的使用方式，直接连接到已部署的公共服务器。

```bash
# 克隆项目
git clone https://github.com/DreamerVAC/BeeSyncClip.git
cd BeeSyncClip

# 安装客户端依赖
pip install -r requirements-client.txt

# 启动GUI客户端
python client/ui/form_ui.py

# 或使用便捷脚本（自动检查和安装依赖）
chmod +x start_client.sh
./start_client.sh                    # 前台启动
./start_client.sh --daemon           # 后台启动，不占用终端
```

**登录信息**:
- **服务器地址**: `http://47.110.154.99:8000` (客户端默认配置)
- **注册**: 新用户请在客户端界面进行注册，创建自己的账号

### 3. 本地部署 (可选)

如果您想在自己的服务器上部署，请按以下步骤操作。

**服务器端**:

```bash
# (在服务器上) 克隆项目
git clone https://github.com/DreamerVAC/BeeSyncClip.git
cd BeeSyncClip

# 安装服务器依赖
pip install -r requirements-server.txt

# 🔥 启动模块化服务器 (推荐 - 企业级安全)
chmod +x start_server.sh
./start_server.sh -m -d          # 后台启动模块化服务器
./start_server.sh -m             # 前台启动模块化服务器

# 📦 启动原始服务器 (传统版本)
./start_server.sh -o -d          # 后台启动原始服务器
./start_server.sh -o             # 前台启动原始服务器

# 查看服务状态
./status.sh

# 停止服务器
./stop_server.sh
```

**服务器版本对比**:

| 特性 | 模块化服务器 v2.0 🔥 | 原始服务器 v1.0 📦 |
|------|---------------------|-------------------|
| 安全性 | AES-256加密 + JWT认证 | 基础认证 |
| 性能 | 批量查询优化，提升20% | 标准性能 |
| 多设备同步 | 解决卡顿问题 | 可能出现卡顿 |
| API兼容性 | 100%向后兼容 | 原始API |
| 企业级功能 | ✅ 完整支持 | ❌ 不支持 |
| 推荐程度 | 🌟🌟🌟🌟🌟 | 🌟🌟🌟 |

**客户端配置**:

客户端需要修改服务器地址以连接到您的私有服务器：

**方法一：修改源代码（推荐）**
```bash
# 编辑主要的客户端文件，将默认服务器地址替换为您的服务器
find client/ -name "*.py" -exec sed -i 's/http:\/\/47\.110\.154\.99:8000/http:\/\/YOUR_SERVER_IP:8000/g' {} \;

# 例如，如果您的服务器IP是192.168.1.100
find client/ -name "*.py" -exec sed -i 's/http:\/\/47\.110\.154\.99:8000/http:\/\/192.168.1.100:8000/g' {} \;
```

**方法二：手动修改关键文件**

需要修改以下文件中的服务器地址：
- `client/api/api_manager.py` (第15行)
- `client/api/http_client.py` (第13行)  
- `client/ui/page3_login.py` (第137行)

将 `http://47.110.154.99:8000` 替换为 `http://YOUR_SERVER_IP:8000`

**方法三：使用自定义端口**

如果您使用了非8000端口启动服务器，请确保客户端配置中的端口号与服务器启动端口一致。

## 🏗️ 项目架构

### 项目结构

```
BeeSyncClip/
├── client/                   # PyQt5 GUI客户端
│   ├── ui/                   # GUI界面模块
│   └── api/                  # API客户端
├── server/                   # FastAPI后端服务器
│   ├── modular_server.py     # 🔥 模块化服务器 v2.0 (推荐)
│   ├── frontend_compatible_server.py  # 📦 原始服务器 v1.0
│   ├── security/             # 安全模块 (模块化服务器)
│   │   ├── encryption.py     # AES-256加密
│   │   ├── auth.py           # JWT认证
│   │   └── middleware.py     # 安全中间件
│   ├── api/                  # API路由模块
│   ├── database/             # 数据库管理
│   └── redis_manager.py      # Redis管理器
├── shared/                   # 共享代码和数据模型
├── config/                   # 配置文件
├── requirements.txt          # 完整依赖列表
├── requirements-client.txt   # 客户端专用依赖
├── requirements-server.txt   # 服务器专用依赖
├── start_server.sh           # 统一服务器启动脚本
└── *.sh                      # 其他管理脚本
```

### 模块化架构 (v2.0)

#### 安全功能
- **AES-256-CBC**: 对称加密，用于数据传输加密
- **RSA-2048**: 非对称加密，用于密钥交换
- **PBKDF2**: 密码哈希，100,000次迭代
- **JWT Token**: 访问令牌，24小时有效期
- **安全中间件**: 速率限制、安全头、请求验证

#### 性能优化
- **异步处理**: FastAPI异步框架
- **Redis缓存**: 用户会话、设备状态缓存
- **批量查询**: 优化数据库查询性能
- **连接池**: Redis连接复用

## 🚀 脚本使用指南

### 统一启动脚本 start_server.sh

这是主要的服务器启动脚本，支持多种启动模式：

```bash
# 🔥 模块化服务器（推荐）
./start_server.sh -m              # 前台启动
./start_server.sh -m -d           # 后台启动

# 📦 原始服务器
./start_server.sh -o              # 前台启动  
./start_server.sh -o -d           # 后台启动

# 指定端口
./start_server.sh -m -p 3000      # 模块化服务器，端口3000
./start_server.sh -o -p 9000      # 原始服务器，端口9000

# 使用80端口（需要sudo权限）
sudo ./start_server.sh -m --port80
```

**参数说明：**
- `-m, --modular`: 启动模块化服务器 v2.0（推荐）
- `-o, --original`: 启动原始服务器 v1.0
- `-d, --daemon`: 后台模式启动
- `-f, --foreground`: 前台模式启动（默认）
- `-p, --port PORT`: 指定端口（默认：8000）
- `--port80`: 使用80端口启动

### 其他管理脚本

```bash
# 查看服务器状态
./status.sh

# 停止服务器
./stop_server.sh

# 服务器切换
./switch_server.sh -m    # 切换到模块化服务器
./switch_server.sh -o    # 切换到原始服务器

# API测试
python test_api.py

# 性能对比
python compare_servers.py
```

## 📦 依赖说明

项目提供了多个requirements文件以满足不同的使用场景：

- **`requirements-client.txt`**: 客户端GUI应用的最小依赖集
- **`requirements-server.txt`**: 服务器后端的必需依赖  
- **`requirements.txt`**: 完整的项目依赖列表

## 🔌 API 文档

### 在线文档
项目使用 FastAPI 自动生成 API 文档：
- **Swagger UI**: `http://<server-address>:8000/docs`
- **ReDoc**: `http://<server-address>:8000/redoc`

### 主要 API 端点

#### 认证相关
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/logout` - 用户登出
- `POST /auth/refresh` - 刷新Token
- `GET /auth/profile` - 获取用户信息

#### 剪贴板管理
- `GET /clipboard/history` - 获取剪贴板历史记录
- `POST /clipboard/add` - 添加剪贴板记录
- `GET /clipboard/latest` - 获取最新内容
- `DELETE /clipboard/{id}` - 删除指定记录
- `POST /clipboard/clear` - 清空剪贴板

#### 设备管理
- `GET /devices/list` - 获取设备列表
- `PUT /devices/update-label` - 更新设备标签
- `DELETE /devices/{id}` - 移除设备
- `GET /devices/{id}/status` - 获取设备状态

#### 兼容接口 (向后兼容)
- `GET /get_clipboards?username={username}` - 获取用户剪贴板记录
- `POST /add_clipboard` - 添加剪贴板记录
- `POST /delete_clipboard` - 删除指定剪贴板记录
- `POST /clear_clipboards` - 清空用户所有剪贴板记录

#### 系统信息
- `GET /` - API 状态和信息
- `GET /health` - 服务健康检查

### WebSocket 连接
- **端点**: `ws://<server-address>:8000/ws/{user_id}/{device_id}?token={jwt_token}`
- **用途**: 实时剪贴板同步和设备状态通信
- **支持消息类型**: 
  - `ping/pong` - 心跳检测
  - `clipboard_sync` - 剪贴板同步
  - `request_history` - 请求历史记录

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
- **速率限制**: 防止暴力攻击（每分钟60次请求）
- **Token黑名单**: 支持令牌吊销
- **安全头**: 防止XSS、CSRF等攻击
- **输入验证**: 严格的数据验证
- **错误处理**: 安全的错误信息返回

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

## 🔧 故障排除

### 常见问题

1. **Redis连接失败**
   ```bash
   # 启动Redis服务
   sudo systemctl start redis
   ```

2. **端口占用**
   ```bash
   # 查看端口占用
   netstat -tuln | grep :8000
   # 或使用其他端口
   ./start_server.sh -m -p 9000
   ```

3. **依赖安装失败**
   ```bash
   # 更新pip
   pip install --upgrade pip
   # 重新安装依赖
   pip install -r requirements-server.txt
   ```

## 📋 更新日志

### v2.0.0 (当前版本)
- ✅ 完整的模块化架构
- ✅ AES-256 + RSA-2048 加密
- ✅ JWT认证系统
- ✅ 安全中间件
- ✅ 性能优化
- ✅ 统一启动脚本

### v1.0.0
- ✅ 基础剪贴板同步功能
- ✅ PyQt5桌面客户端
- ✅ FastAPI后端服务器
- ✅ Redis数据存储

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交问题和拉取请求！请先阅读我们的贡献指南。

## 📞 支持

如果您遇到问题或有疑问，请：
1. 查看本文档的故障排除部分
2. 提交 GitHub Issue
3. 查看在线API文档

---

🐝 **BeeSyncClip** - 让您的剪贴板在设备间自由飞翔！

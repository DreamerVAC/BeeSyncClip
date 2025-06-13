# 🐝 BeeSyncClip - 跨平台剪贴板同步工具

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-GUI-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-red.svg)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-Cache-orange.svg)](https://redis.io/)
[![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-blue.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

## ✨ 核心功能

- 🔄 **跨设备同步**: 使用 WebSocket 和 Redis Pub/Sub 实现跨设备剪贴板同步
- 🖥️ **桌面客户端**: 基于 PyQt5 的跨平台桌面应用，支持 Windows、macOS、Linux
- 📋 **剪贴板管理**: 提供剪贴板历史记录的查看、搜索和管理功能
- 🔐 **数据安全**: AES-256加密 + JWT认证，保障数据传输安全
- 📦 **简化部署**: 统一的启动脚本简化服务器和客户端的启动流程

## 🚀 快速入门

### 1. 准备环境

确保您的系统已安装 `Python 3.11+` 和 `pip`。

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

### 3. 本地部署

如果您想在自己的服务器上部署，请按以下步骤操作。

```bash
# (在服务器上) 克隆项目
git clone https://github.com/DreamerVAC/BeeSyncClip.git
cd BeeSyncClip

# 安装服务器依赖
pip install -r requirements-server.txt

# 启动服务器
chmod +x start_server.sh
./start_server.sh -m -d          # 后台启动服务器
./start_server.sh -m             # 前台启动服务器

# 查看服务状态
./status.sh

# 停止服务器
./stop_server.sh
```

**客户端配置**:

客户端需要修改服务器地址以连接到您的私有服务器：

```bash
# 编辑主要的客户端文件，将默认服务器地址替换为您的服务器
find client/ -name "*.py" -exec sed -i 's/http:\/\/47\.110\.154\.99:8000/http:\/\/YOUR_SERVER_IP:8000/g' {} \;
```

## 🏗️ 项目架构

### 项目结构

```
BeeSyncClip/
├── client/                   # PyQt5 GUI客户端
│   ├── ui/                   # GUI界面模块
│   └── api/                  # API客户端
├── server/                   # FastAPI后端服务器
│   ├── modular_server.py     # 服务器主程序
│   ├── security/             # 安全模块
│   ├── api/                  # API路由模块
│   ├── database/             # 数据库管理
│   └── redis_manager.py      # Redis管理器
├── shared/                   # 共享代码和数据模型
├── config/                   # 配置文件
├── requirements/             # 依赖文件
├── tests/                    # 测试文件
├── start_server.sh           # 统一服务器启动脚本
└── *.sh                      # 其他管理脚本
```

## 🚀 脚本使用指南

### 统一启动脚本 start_server.sh

这是主要的服务器启动脚本，支持多种启动模式：

```bash
# 启动服务器
./start_server.sh -m              # 前台启动
./start_server.sh -m -d           # 后台启动

# 指定端口
./start_server.sh -m -p 3000      # 服务器，端口3000

# 使用80端口（需要sudo权限）
sudo ./start_server.sh -m --port80
```

**参数说明：**
- `-m, --modular`: 启动服务器
- `-d, --daemon`: 后台模式启动
- `-f, --foreground`: 前台模式启动（默认）
- `-p, --port PORT`: 指定端口（默认：8000）
- `--port80`: 使用80端口启动

## 📄 许可证

本项目采用 MIT 许可证



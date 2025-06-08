# 🐝 BeeSyncClip - 跨平台剪贴板同步工具

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-GUI-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-red.svg)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-Cache-orange.svg)](https://redis.io/)
[![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-blue.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

> 🚀 **v1.1.2 - 生产就绪**  
> **实时同步，稳定可靠**

## ✨ 核心功能

- 🔄 **实时同步**: 基于 `WebSocket` 和 `Redis Pub/Sub`，实现毫秒级跨设备剪贴板同步。
- 🖥️ **原生GUI**: 基于 `PyQt5` 的现代化原生桌面客户端，支持 Windows, macOS, Linux。
- 📋 **剪贴板管理**: 提供完整的剪贴板历史记录查看、搜索、复制和删除功能。
- 🔐 **安全认证**: 支持多用户、多设备安全认证和独立管理。
- ⚡ **高性能后端**: `FastAPI` + `Redis` 提供高性能、高并发的API服务。
- ☁️ **一键部署**: 提供自动化脚本，简化服务器和客户端的部署流程。

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
./start_client.sh
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

# 启动后台服务 (推荐)
chmod +x start_server.sh
./start_server.sh -d

# 或前台启动 (调试时使用)
./start_server.sh

# 查看服务状态
./status.sh
```

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

## 🏗️ 项目结构

```
BeeSyncClip/
├── client/                   # PyQt5 GUI客户端
│   ├── ui/                   # GUI界面模块
│   │   └── form_ui.py        # 客户端入口
│   └── api/                  # API客户端
├── server/                   # FastAPI后端服务器
│   ├── frontend_compatible_server.py  # 主服务器
│   ├── redis_manager.py      # Redis管理器
│   └── auth.py               # 认证模块
├── shared/                   # 共享代码和数据模型
│   ├── models.py             # 数据模型定义
│   └── utils.py              # 工具函数和配置管理
├── config/                   # 配置文件
├── requirements.txt          # 完整依赖列表
├── requirements-client.txt   # 客户端专用依赖
├── requirements-server.txt   # 服务器专用依赖
└── *.sh                      # 服务器管理脚本
```

## 📦 依赖说明

项目提供了多个requirements文件以满足不同的使用场景：

- **`requirements-client.txt`**: 客户端GUI应用的最小依赖集
- **`requirements-server.txt`**: 服务器后端的必需依赖  
- **`requirements.txt`**: 完整的项目依赖列表

## 🔌 API & WebSocket

### API 文档
- **Swagger UI**: `http://<your-server-ip>:8000/docs`
- **Redoc**: `http://<your-server-ip>:8000/redoc`

### WebSocket 端点
- `ws://<your-server-ip>:8000/ws/{user_id}/{device_id}`
- 该端点用于客户端和服务器之间的实时通信。

## 🔧 开发与调试

### 启动开发服务器
```bash
# 确保 Redis 服务正在运行
# 然后启动FastAPI开发服务器
python server/main_server.py
```

### 启动GUI客户端进行调试
```bash
# 启动客户端GUI
python client/ui/form_ui.py
```

## 📄 许可证

本项目基于 [MIT License](LICENSE) 授权。

---

⭐ 如果这个项目对您有帮助，请给一个 **Star** 支持一下！

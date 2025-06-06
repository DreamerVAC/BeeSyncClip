# 🐝 BeeSyncClip - 跨平台剪贴板同步工具

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-red.svg)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-Database-orange.svg)](https://redis.io/)

> 🚀 **已部署运行** - 服务器地址: http://47.110.154.99:8000  
> 📱 **测试账号** - 用户名: `testuser` / 密码: `test123`

## ✨ 功能特点

- 🔄 **实时同步** - 跨设备剪贴板内容实时同步
- 🖥️ **原生GUI** - 基于PyQt6的美观桌面客户端
- 📱 **多设备支持** - 支持Windows、macOS、Linux
- 🔒 **安全认证** - 用户登录和设备管理
- 📋 **历史记录** - 完整的剪贴板历史管理
- ⚡ **高性能** - Redis缓存，FastAPI后端

## 🚀 快速开始

### 方法1: 直接使用（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/DreamerVAC/BeeSyncClip.git
cd BeeSyncClip

# 2. 安装依赖
pip install PyQt6 pyperclip requests

# 3. 启动GUI客户端
chmod +x start_gui.sh
./start_gui.sh
```

### 方法2: 完整安装

```bash
# 安装所有依赖
pip install -r requirements.txt

# 启动桌面客户端
python desktop/main.py
```

## 🔧 网络配置

### 选项A: 直接连接（需配置安全组）
- 服务器地址: `http://47.110.154.99:8000`
- 需要配置阿里云安全组开放8000端口

### 选项B: 80端口访问（立即可用）
- 服务器地址: `http://47.110.154.99`
- 服务器端执行: `sudo ./start_server_port80.sh`

### 选项C: SSH隧道
```bash
ssh -L 8000:localhost:8000 ubuntu@47.110.154.99 -N
# 然后连接: http://localhost:8000
```

## 📱 使用说明

### 登录信息
- **用户名**: `testuser`
- **密码**: `test123`
- **服务器**: 自动检测可用地址

### 主要功能
1. **查看历史** - 显示所有同步的剪贴板内容
2. **复制内容** - 一键复制历史项目到本地剪贴板
3. **删除项目** - 管理不需要的剪贴板项目
4. **自动同步** - 实时监控并同步新内容
5. **设备管理** - 查看和管理已连接设备

## 🏗️ 项目结构

```
BeeSyncClip/
├── 📱 client/          # Web客户端
├── 🖥️ desktop/         # PyQt6桌面客户端
├── 🔧 server/          # FastAPI后端服务
├── 📦 shared/          # 共享模块和数据模型
├── ⚙️ config/          # 配置文件
├── 🚀 deploy/          # 部署脚本
├── 📋 requirements.txt # Python依赖
├── 🎯 start_gui.sh     # GUI启动脚本
└── 📖 README.md        # 项目说明
```

## 🔌 API接口

### 核心端点
- `POST /login` - 用户登录
- `GET /get_clipboards` - 获取剪贴板历史
- `POST /add_clipboard` - 添加剪贴板内容
- `POST /delete_clipboard` - 删除剪贴板项目
- `GET /get_devices` - 获取设备列表
- `GET /health` - 健康检查

### API文档
访问 http://47.110.154.99:8000/docs 查看完整API文档

## 🛠️ 开发部署

### 服务器端部署
```bash
# 启动服务器
./start_daemon.sh

# 检查状态
./status.sh

# 停止服务器
./stop_server.sh
```

### 本地开发
```bash
# 安装开发依赖
pip install -r requirements.txt

# 启动开发服务器
python start_frontend_server.py

# 启动GUI客户端
python desktop/main.py
```

## 📋 系统要求

### 客户端
- Python 3.8+
- PyQt6
- pyperclip
- requests

### 服务器端
- Python 3.8+
- Redis 6.0+
- FastAPI
- uvicorn

## 🔧 故障排除

### 无法连接服务器
```bash
# 检测端口连通性
curl http://47.110.154.99:8000/health  # 8000端口
curl http://47.110.154.99/health        # 80端口
```

### GUI无法启动
```bash
# 安装GUI依赖
pip install PyQt6 pyperclip

# Linux额外依赖
sudo apt-get install python3-pyqt6
```

### 剪贴板不工作
```bash
# Linux安装剪贴板支持
sudo apt-get install xclip  # 或 xsel
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/DreamerVAC/BeeSyncClip/issues)
- 📖 文档: [项目Wiki](https://github.com/DreamerVAC/BeeSyncClip/wiki)

---

⭐ 如果这个项目对您有帮助，请给个Star支持一下！

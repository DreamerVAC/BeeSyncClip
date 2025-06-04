# BeeSyncClip 🐝📋

一个基于 Python + PyQt + Redis + WebSocket 的跨平台同步剪切板应用。

## 📁 项目结构

```
BeeSyncClip/
├── client/                      # 前端客户端
│   ├── api/                     # API通信层
│   │   ├── __init__.py          # API包初始化
│   │   ├── api_manager.py       # 统一API管理器
│   │   ├── auth_api.py          # 认证API客户端
│   │   ├── clipboard_api.py     # 剪贴板API客户端
│   │   ├── device_api.py        # 设备API客户端
│   │   └── http_client.py       # HTTP客户端基础类
│   ├── ui/                      # 用户界面
│   │   ├── form_ui.py           # 主界面
│   │   ├── page1_clipboard.py   # 剪贴板页面
│   │   ├── page2_device.py      # 设备管理页面
│   │   ├── page3_login.py       # 登录页面
│   │   └── page4_register.py    # 注册页面
│   └── main.py                  # 客户端主入口
├── server/                      # 后端服务
│   ├── api_server.py            # FastAPI服务器
│   ├── auth.py                  # 认证管理
│   ├── frontend_compatible_server.py  # 前端兼容服务器
│   ├── main_server.py           # 主服务器
│   ├── redis_manager.py         # Redis数据管理
│   └── websocket_server.py      # WebSocket服务器
├── shared/                      # 共享代码
│   ├── models.py                # 数据模型
│   └── utils.py                 # 工具函数
├── config/                      # 配置文件
│   ├── settings.yaml            # 本地配置
│   └── aliyun_settings.yaml     # 阿里云配置
├── deploy/                      # 部署脚本
│   ├── connect_aliyun.sh        # 阿里云连接脚本
│   ├── ubuntu_deploy.sh         # Ubuntu部署脚本
│   └── aliyun_deploy.sh         # 阿里云部署脚本
├── legacy/                      # 历史文件
│   └── mock_server.py           # 原Mock服务器
├── start_frontend_server.py     # 前端兼容服务器启动脚本
├── test_connection.py           # 连接测试脚本
├── upload_to_server.sh          # 服务器上传脚本
├── requirements.txt             # 项目依赖
└── README.md                    # 项目说明
```

## 🚀 运行说明

### 系统要求
- Python 3.11+
- Redis 6.0+

### 快速启动

#### 1. 安装依赖
```bash
pip install -r requirements.txt
```

#### 2. 启动Redis
```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis-server

# 验证
redis-cli ping  # 返回 PONG
```

#### 3. 启动后端服务
```bash
python start_frontend_server.py
```

#### 4. 启动客户端
```bash
# 推荐方式
python client/main.py

# 或直接启动UI
python client/ui/form_ui.py
```

#### 5. 测试登录
- 用户名: `testuser`
- 密码: `test123`

### 服务器信息
- **服务器地址**: http://47.110.154.99:8000
- **WebSocket地址**: ws://47.110.154.99:8765

### 连接测试
```bash
python test_connection.py
```

### 部署到服务器
```bash
# 上传代码
./upload_to_server.sh

# 详细部署指南
参考 DEPLOYMENT_GUIDE.md
```

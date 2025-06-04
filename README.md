# BeeSyncClip 🐝📋

一个基于 Python + PyQt6 + Redis + WebSocket 的跨平台同步剪切板应用。

> 💡 **灵感来源**: 参考了优秀的开源项目 [EcoPaste](https://github.com/EcoPasteHub/EcoPaste) 的设计理念，并结合云端同步的强大功能。

## ✨ 核心特性

### 🔄 云端同步优势
- **实时同步**: 通过 WebSocket 和 Redis 实现多设备间剪切板实时同步
- **云端存储**: 基于阿里云的企业级服务架构
- **团队协作**: 支持团队共享剪切板空间 (规划中)

### 🖥️ 跨平台体验
- **全平台支持**: Windows、macOS、Linux 无缝体验
- **现代化UI**: 参考 EcoPaste 的简洁设计，基于 PyQt6 的现代界面
- **系统集成**: 系统托盘、快捷键、右键菜单完整支持

### 📋 强大功能
- **多格式支持**: 文本、图片、文件等多种剪切板内容
- **智能搜索**: 全文搜索、正则表达式、按类型筛选
- **历史管理**: 持久化存储，支持标签和分类
- **安全可靠**: 本地加密 + 云端安全，双重保护

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动 Redis 服务

```bash
# 本地开发
redis-server

# 或使用 Docker
docker run -d -p 6379:6379 redis:alpine
```

### 3. 启动同步服务器

```bash
cd server
python main_server.py
```

### 4. 启动桌面客户端

```bash
cd desktop
python main.py
```

## 📁 项目结构

```
BeeSyncClip/
├── desktop/           # PyQt6 桌面客户端
│   ├── main.py       # 客户端启动入口
│   ├── main_window.py # 主窗口 (参考EcoPaste设计)
│   └── components/   # UI组件库
├── server/           # FastAPI WebSocket 服务端
│   ├── main_server.py    # 服务器启动脚本
│   ├── api_server.py     # HTTP API服务
│   ├── websocket_server.py # WebSocket服务
│   ├── auth.py          # 认证系统
│   └── redis_manager.py # Redis管理
├── shared/           # 共享工具和模型
├── config/           # 配置文件
│   ├── settings.yaml      # 基础配置
│   └── aliyun_settings.yaml # 阿里云部署配置
├── deploy/           # 部署脚本
├── logs/             # 日志文件
├── requirements.txt  # Python 依赖
├── ROADMAP.md       # 发展路线图
└── README.md        # 项目说明
```

## 🎨 界面设计

### 设计理念 (参考 EcoPaste)
- **简洁至上**: 界面简洁直观，操作零门槛
- **效率优先**: 快速访问和操作
- **美观现代**: 现代化设计语言
- **跨平台一致**: 统一的用户体验

### 主要界面
- 🔍 **智能搜索栏**: 快速查找历史记录
- 📝 **列表视图**: 清晰展示剪贴板历史
- 👁️ **预览面板**: 实时预览选中内容
- ⚙️ **设置面板**: 丰富的个性化配置

## ⚙️ 配置说明

### 基础配置 (`config/settings.yaml`)
```yaml
# Redis 连接
redis:
  host: "localhost"
  port: 6379
  
# WebSocket 服务
websocket:
  host: "localhost"
  port: 8765
  
# 剪切板设置
clipboard:
  monitor_interval: 0.5
  max_history: 1000
```

### 阿里云部署 (`config/aliyun_settings.yaml`)
```yaml
# 生产环境配置
redis:
  host: "your-redis-host"
  password: "your-redis-password"
  
websocket:
  host: "0.0.0.0"
  port: 8765
```

## 🛣️ 开发计划

| 阶段 | 功能 | 状态 | 参考 |
|------|------|------|------|
| Phase 1 | 基础架构 | ✅ | - |
| Phase 1 | 服务端开发 | ✅ | - |
| Phase 1 | 桌面客户端UI | 🚧 | EcoPaste 设计风格 |
| Phase 2 | 智能分类 | 📋 | EcoPaste 分类系统 |
| Phase 2 | 高级搜索 | 📋 | EcoPaste 搜索功能 |
| Phase 3 | 主题系统 | 📋 | EcoPaste 主题切换 |
| Phase 4 | 团队协作 | 📋 | BeeSyncClip 独有 |
| Phase 5 | 移动端 | 📋 | 扩展生态 |

> 📋 = 计划中 | 🚧 = 开发中 | ✅ = 已完成

## 🆚 对比优势

### vs EcoPaste
| 特性 | EcoPaste | BeeSyncClip |
|------|----------|-------------|
| 技术栈 | Tauri + TypeScript | Python + PyQt6 |
| 数据同步 | 本地存储 | **云端实时同步** |
| 跨设备 | 需手动同步 | **自动同步** |
| 团队协作 | 不支持 | **企业级支持** |
| 部署方式 | 单机应用 | **云端服务** |
| 扩展性 | 限制 | **高度可扩展** |

### 独特优势
- 🌩️ **真正的云端同步**: 多设备实时同步，不限平台
- 🏢 **企业级架构**: 支持团队共享、权限管理
- 🔒 **安全可靠**: 双重加密，企业级安全保障
- 📈 **高可扩展**: 微服务架构，支持集群部署

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 开发环境设置
```bash
# 1. 克隆项目
git clone https://github.com/your-repo/BeeSyncClip.git

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动开发环境
python server/main_server.py  # 终端1
python desktop/main.py        # 终端2
```

### 参与方式
- 🐛 提交 Bug 报告
- 💡 提出功能建议  
- 🔧 提交代码改进
- 📖 完善文档
- 🎨 优化界面设计

## 📄 许可证

MIT License - 自由使用和修改

## 🙏 致谢

- [EcoPaste](https://github.com/EcoPasteHub/EcoPaste) - 优秀的界面设计和用户体验启发
- PyQt6 - 强大的跨平台GUI框架
- FastAPI - 现代化的Python Web框架
- Redis - 高性能内存数据库

---

**让剪贴板同步变得简单而强大！** 🚀

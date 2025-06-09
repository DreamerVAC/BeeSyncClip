# 🚀 BeeSyncClip 脚本使用指南

本指南介绍如何使用 BeeSyncClip 项目中的各种管理脚本。

## 📋 脚本概览

| 脚本名称 | 功能 | 推荐程度 |
|---------|------|----------|
| `start_server.sh` | 统一服务器启动脚本 | ⭐⭐⭐⭐⭐ |
| `start_modular.sh` | 模块化服务器快捷启动 | ⭐⭐⭐⭐⭐ |
| `switch_server.sh` | 服务器切换工具 | ⭐⭐⭐⭐ |
| `status.sh` | 服务器状态查看 | ⭐⭐⭐⭐⭐ |
| `stop_server.sh` | 服务器停止脚本 | ⭐⭐⭐⭐⭐ |
| `test_api.py` | API测试脚本 | ⭐⭐⭐ |
| `compare_servers.py` | 服务器性能对比 | ⭐⭐⭐ |

## 🔥 推荐使用流程

### 1. 快速启动模块化服务器（推荐）

```bash
# 最简单的方式 - 启动推荐的模块化服务器
./start_modular.sh -d

# 或者使用统一脚本
./start_server.sh -m -d
```

### 2. 查看服务器状态

```bash
./status.sh
```

### 3. 停止服务器

```bash
./stop_server.sh
```

## 📖 详细脚本说明

### 🚀 start_server.sh - 统一服务器启动脚本

这是主要的服务器启动脚本，支持两种服务器版本：

**基本用法：**
```bash
# 启动模块化服务器（推荐）
./start_server.sh -m              # 前台启动
./start_server.sh -m -d           # 后台启动

# 启动原始服务器
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

### 🔥 start_modular.sh - 模块化服务器快捷启动

专门用于启动模块化服务器的快捷脚本：

```bash
# 前台启动
./start_modular.sh

# 后台启动
./start_modular.sh -d

# 指定端口
./start_modular.sh -p 3000

# 后台启动并指定端口
./start_modular.sh -d -p 9000
```

### 🔄 switch_server.sh - 服务器切换工具

方便地在两种服务器之间切换：

```bash
# 切换到模块化服务器
./switch_server.sh -m

# 切换到原始服务器
./switch_server.sh -o

# 查看当前服务器状态
./switch_server.sh -s
```

**功能特点：**
- 自动停止当前运行的服务器
- 启动指定类型的新服务器
- 显示切换结果和服务器信息

### 📊 status.sh - 服务器状态查看

查看服务器运行状态和系统信息：

```bash
./status.sh
```

**显示信息：**
- Redis 服务状态
- 服务器进程状态和版本
- 系统资源使用情况
- 网络连接状态
- 最近的日志信息
- 管理命令提示

### 🛑 stop_server.sh - 服务器停止脚本

停止所有运行中的 BeeSyncClip 服务器：

```bash
./stop_server.sh
```

**功能特点：**
- 优雅停止服务器进程
- 支持强制停止
- 清理PID文件
- 停止所有相关进程

### 🧪 test_api.py - API测试脚本

测试服务器API功能：

```bash
# 测试默认服务器
python test_api.py

# 测试指定服务器
python test_api.py http://localhost:3000
```

**测试内容：**
- 基础API接口
- 健康检查
- 用户注册和登录
- 模块化服务器特有功能（如果适用）

### 📈 compare_servers.py - 服务器性能对比

对比两种服务器的性能和功能：

```bash
# 对比当前运行的服务器
python compare_servers.py

# 对比指定服务器
python compare_servers.py http://localhost:3000
```

**对比内容：**
- 响应时间性能测试
- 并发处理能力测试
- 功能完整性对比
- 生成详细对比报告

## 🌟 服务器版本对比

### 🔥 模块化服务器 v2.0（推荐）

**优势：**
- ✅ AES-256加密 + JWT认证
- ✅ 性能优化，提升20%
- ✅ 解决多设备同步卡顿问题
- ✅ 批量查询优化
- ✅ 企业级安全功能
- ✅ 100%向后兼容
- ✅ 完整的API文档

**适用场景：**
- 生产环境部署
- 多用户企业使用
- 对安全性有要求的场景
- 需要高性能的场景

### 📦 原始服务器 v1.0

**优势：**
- ✅ 稳定可靠
- ✅ 轻量级
- ✅ 简单易用
- ✅ 资源占用少

**适用场景：**
- 个人使用
- 测试和开发
- 资源受限的环境
- 简单部署需求

## 💡 最佳实践

### 1. 生产环境推荐配置

```bash
# 1. 启动模块化服务器（后台模式）
./start_modular.sh -d

# 2. 验证服务器状态
./status.sh

# 3. 测试API功能
python test_api.py
```

### 2. 开发环境配置

```bash
# 前台启动，便于查看日志
./start_server.sh -m

# 或者使用原始服务器进行轻量级测试
./start_server.sh -o
```

### 3. 服务器维护

```bash
# 查看当前状态
./switch_server.sh -s

# 重启服务器
./stop_server.sh
./start_modular.sh -d

# 切换服务器版本进行测试
./switch_server.sh -o  # 切换到原始服务器
./switch_server.sh -m  # 切换回模块化服务器
```

### 4. 性能测试

```bash
# 启动模块化服务器并测试
./start_modular.sh -d
python compare_servers.py

# 切换到原始服务器并对比
./switch_server.sh -o
python compare_servers.py
```

## 🔧 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查看端口占用
   netstat -tuln | grep :8000
   
   # 使用其他端口启动
   ./start_server.sh -m -p 9000
   ```

2. **Redis连接失败**
   ```bash
   # 检查Redis状态
   redis-cli ping
   
   # 启动Redis服务
   sudo systemctl start redis
   ```

3. **权限问题**
   ```bash
   # 确保脚本有执行权限
   chmod +x *.sh
   
   # 80端口需要sudo权限
   sudo ./start_server.sh -m --port80
   ```

4. **依赖缺失**
   ```bash
   # 安装服务器依赖
   pip install -r requirements-server.txt
   ```

### 日志查看

```bash
# 查看实时日志
tail -f beesyncclip.log

# 查看最近的错误
grep -i error beesyncclip.log | tail -10
```

## 📞 获取帮助

每个脚本都支持 `-h` 或 `--help` 参数：

```bash
./start_server.sh -h
./start_modular.sh -h
./switch_server.sh -h
```

## 🎯 总结

- **推荐使用**: `./start_modular.sh -d` 启动模块化服务器
- **状态查看**: `./status.sh` 查看服务器状态
- **服务器切换**: `./switch_server.sh -m` 切换到模块化服务器
- **停止服务**: `./stop_server.sh` 停止所有服务器

模块化服务器 v2.0 是推荐的生产环境选择，提供企业级安全和性能优化！ 
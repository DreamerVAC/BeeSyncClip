# BeeSyncClip 阿里云部署指南 🚀

## 🌐 服务器信息

- **公网IP**: 47.110.154.99
- **用户名**: ubuntu
- **密码**: Sysu$9999
- **系统**: Ubuntu
- **端口**: 8000 (HTTP API), 8765 (WebSocket)

## 🔧 部署步骤

### 1. 连接到服务器

```bash
# SSH连接
ssh ubuntu@47.110.154.99
# 输入密码: Sysu$9999
```

### 2. 检查系统环境

```bash
# 检查Python版本
python3 --version

# 检查Redis是否安装
redis-cli --version

# 检查端口状态
sudo netstat -tulpn | grep :8000
```

### 3. 部署项目代码

#### 方法1: 直接上传代码

```bash
# 在本地运行，上传整个项目
scp -r . ubuntu@47.110.154.99:~/BeeSyncClip/
```

#### 方法2: 使用Git

```bash
# 在服务器上克隆项目
cd ~
git clone <your-repo-url> BeeSyncClip
cd BeeSyncClip
```

### 4. 安装依赖

```bash
# 更新系统
sudo apt update

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv -y

# 安装Redis
sudo apt install redis-server -y

# 启动Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 验证Redis
redis-cli ping  # 应该返回 PONG
```

### 5. 设置Python环境

```bash
cd ~/BeeSyncClip

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装项目依赖
pip install -r requirements.txt

# 如果没有requirements.txt，手动安装
pip install fastapi uvicorn redis PyJWT bcrypt
```

### 6. 配置防火墙

```bash
# 开放端口8000和8765
sudo ufw allow 8000
sudo ufw allow 8765

# 检查防火墙状态
sudo ufw status
```

### 7. 启动服务器

```bash
cd ~/BeeSyncClip

# 激活虚拟环境（如果还没激活）
source venv/bin/activate

# 启动前端兼容服务器
python start_frontend_server.py

# 或者使用后台运行
nohup python start_frontend_server.py > server.log 2>&1 &
```

### 8. 验证部署

```bash
# 检查服务是否运行
curl http://localhost:8000/health

# 检查进程
ps aux | grep python

# 查看日志
tail -f server.log
```

## 🔄 服务管理

### 创建系统服务 (可选)

```bash
# 创建服务文件
sudo tee /etc/systemd/system/beesyncclip.service > /dev/null <<EOF
[Unit]
Description=BeeSyncClip Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/BeeSyncClip
Environment=PATH=/home/ubuntu/BeeSyncClip/venv/bin
ExecStart=/home/ubuntu/BeeSyncClip/venv/bin/python start_frontend_server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 重载系统服务
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start beesyncclip

# 设置开机自启
sudo systemctl enable beesyncclip

# 查看服务状态
sudo systemctl status beesyncclip
```

### 服务管理命令

```bash
# 启动服务
sudo systemctl start beesyncclip

# 停止服务
sudo systemctl stop beesyncclip

# 重启服务
sudo systemctl restart beesyncclip

# 查看状态
sudo systemctl status beesyncclip

# 查看日志
sudo journalctl -u beesyncclip -f
```

## 🧪 测试连接

### 在服务器上测试

```bash
# 基础连接测试
curl http://localhost:8000/health

# API测试
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123","device_info":{"device_id":"test","label":"测试","os":"Linux"}}'
```

### 在本地测试

```bash
# 从本地测试服务器连接
curl http://47.110.154.99:8000/health

# 运行连接测试脚本
python test_connection.py
```

## 🚨 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   sudo netstat -tulpn | grep :8000
   sudo kill -9 <PID>
   ```

2. **Redis连接失败**
   ```bash
   sudo systemctl status redis-server
   sudo systemctl start redis-server
   ```

3. **Python依赖问题**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **防火墙问题**
   ```bash
   sudo ufw status
   sudo ufw allow 8000
   ```

5. **权限问题**
   ```bash
   sudo chown -R ubuntu:ubuntu ~/BeeSyncClip
   chmod +x start_frontend_server.py
   ```

## ✅ 部署检查清单

- [ ] 服务器连接正常
- [ ] Python 3.11+ 已安装
- [ ] Redis 已安装并运行
- [ ] 项目代码已上传
- [ ] 依赖已安装
- [ ] 防火墙端口已开放
- [ ] 服务器已启动
- [ ] 本地连接测试通过

---

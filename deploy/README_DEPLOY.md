# BeeSyncClip 阿里云部署指南 🚀

## 📋 部署前准备

### 1. 阿里云ECS购买和配置

#### 🛒 购买ECS实例
1. 登录 [阿里云控制台](https://ecs.console.aliyun.com)
2. 点击「创建实例」
3. 选择配置:
   ```
   地域: 就近选择 (如华东1-杭州)
   实例规格: 2核4GB或以上 (推荐: ecs.t6-c1m2.large)
   镜像: CentOS 7.9 64位 或 Ubuntu 20.04
   存储: 40GB SSD云盘
   网络: 专有网络VPC + 分配公网IP
   带宽: 5Mbps或以上
   ```
4. 设置root密码
5. 完成购买

#### 🔒 配置安全组
1. 进入ECS控制台 → 网络与安全 → 安全组
2. 找到您的安全组，点击「配置规则」
3. 添加以下入方向规则:

| 端口范围 | 授权对象    | 描述           |
|----------|-------------|----------------|
| 22       | 0.0.0.0/0   | SSH连接        |
| 8000     | 0.0.0.0/0   | HTTP API       |
| 8765     | 0.0.0.0/0   | WebSocket      |
| 6379     | 内网IP      | Redis (可选)   |

### 2. 获取服务器信息
```bash
# 在阿里云控制台获取以下信息:
ECS公网IP: xxx.xxx.xxx.xxx
ECS内网IP: 172.x.x.x
root密码: [您设置的密码]
```

## 🔗 连接到阿里云服务器

### 方法1: 使用我们的连接脚本 (推荐)

#### 步骤1: 配置连接信息
```bash
# 编辑连接脚本
vim deploy/connect_aliyun.sh

# 修改以下变量 (第11行)
ALIYUN_IP="您的ECS公网IP"    # 如: 47.96.123.456
```

#### 步骤2: 运行连接脚本
```bash
cd BeeSyncClip
./deploy/connect_aliyun.sh
```

#### 步骤3: 选择操作
```
请选择操作:
1) 测试连接       # 先测试网络连通性
2) SSH连接 (密钥)  # 如果您有SSH密钥
3) SSH连接 (密码)  # 使用密码连接
4) 上传代码       # 上传项目代码到服务器
5) 一键部署       # 自动部署整个项目
q) 退出
```

### 方法2: 直接SSH连接
```bash
# 使用SSH连接 (将IP替换为您的实际IP)
ssh root@您的ECS公网IP

# 首次连接会询问是否信任，输入 yes
# 然后输入root密码
```

## 🚀 部署BeeSyncClip

### 方式1: 一键自动部署 (推荐)

#### 使用我们的部署脚本:
```bash
# 在本地执行
./deploy/connect_aliyun.sh

# 选择 "5) 一键部署"
# 脚本会自动:
# - 上传代码到服务器
# - 安装所有依赖
# - 配置Redis
# - 启动服务
```

### 方式2: 手动部署

#### 步骤1: 上传代码
```bash
# 在本地打包代码
tar -czf BeeSyncClip.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    BeeSyncClip/

# 上传到服务器
scp BeeSyncClip.tar.gz root@您的服务器IP:/tmp/
```

#### 步骤2: 连接服务器
```bash
ssh root@您的服务器IP
```

#### 步骤3: 解压并部署
```bash
# 在服务器上执行
cd /tmp
tar -xzf BeeSyncClip.tar.gz
cd BeeSyncClip

# 运行部署脚本
chmod +x deploy/aliyun_deploy.sh
./deploy/aliyun_deploy.sh
```

## 📊 验证部署

### 1. 检查服务状态
```bash
# 检查Redis状态
systemctl status redis

# 检查BeeSyncClip服务状态
systemctl status beesyncclip

# 查看服务日志
journalctl -u beesyncclip -f
```

### 2. 测试API端点
```bash
# 测试健康检查接口
curl http://您的服务器IP:8000/health

# 预期返回:
{"status": "healthy", "timestamp": "2024-..."}
```

### 3. 测试WebSocket连接
```bash
# 安装wscat工具 (如果需要)
npm install -g wscat

# 测试WebSocket连接
wscat -c ws://您的服务器IP:8765
```

## 🛠 常见问题排查

### 问题1: SSH连接失败
```bash
# 检查:
1. ECS公网IP是否正确
2. 安全组是否开放22端口
3. ECS是否正在运行
4. 网络连接是否正常

# 解决方案:
ping 您的服务器IP
telnet 您的服务器IP 22
```

### 问题2: 端口无法访问
```bash
# 检查安全组配置
1. 阿里云控制台 → ECS → 安全组
2. 确认8000和8765端口已开放
3. 检查服务器防火墙: systemctl status firewalld
```

### 问题3: 服务启动失败
```bash
# 查看详细错误日志
journalctl -u beesyncclip -n 50

# 常见原因:
1. Redis未启动: systemctl start redis
2. 端口被占用: netstat -tulpn | grep :8000
3. 配置文件错误: cat /etc/beesyncclip/settings.yaml
```

### 问题4: Redis连接失败
```bash
# 检查Redis状态
systemctl status redis
redis-cli ping

# 如果Redis未启动:
systemctl start redis
systemctl enable redis
```

## 📱 客户端连接配置

### 修改本地客户端配置
```bash
# 编辑客户端配置
vim config/settings.yaml

# 修改服务器地址:
api:
  host: "您的ECS公网IP"  # 改为实际IP
  port: 8000

websocket:
  host: "您的ECS公网IP"  # 改为实际IP
  port: 8765
```

### 测试客户端连接
```bash
# 启动本地客户端
python desktop/main.py

# 检查连接日志
# 应该能看到连接到远程服务器的日志
```

## 🔧 生产环境优化

### 1. 配置域名 (可选)
```bash
# 如果您有域名，可以配置:
1. 解析域名到ECS公网IP
2. 修改配置文件使用域名
3. 配置SSL证书 (HTTPS/WSS)
```

### 2. 性能优化
```bash
# Redis优化
vim /etc/redis.conf
# 调整maxmemory, maxclients等参数

# 系统优化
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
sysctl -p
```

### 3. 监控和备份
```bash
# 设置定时备份
crontab -e
# 添加: 0 2 * * * /opt/beesyncclip/scripts/backup.sh

# 监控日志
tail -f /var/log/beesyncclip/app.log
```

## 📞 技术支持

### 获取帮助
- 查看服务日志: `journalctl -u beesyncclip -f`
- 检查配置文件: `cat /etc/beesyncclip/settings.yaml`
- 测试网络连接: `curl http://localhost:8000/health`

### 重启服务
```bash
# 重启BeeSyncClip服务
systemctl restart beesyncclip

# 重启Redis
systemctl restart redis

# 查看服务状态
systemctl status beesyncclip redis
```

---

**🎉 部署完成后，您就拥有了一个云端的剪贴板同步服务！**

下一步: [配置客户端连接](../README.md#配置说明) 和 [测试多设备同步](../ROADMAP.md#测试计划) 
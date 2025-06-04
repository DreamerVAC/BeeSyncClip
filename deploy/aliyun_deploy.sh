#!/bin/bash

# BeeSyncClip 阿里云部署脚本
# 作者: BeeSyncClip Team  
# 版本: 1.0

set -e  # 遇到错误立即退出

echo "=============================================="
echo "     BeeSyncClip 阿里云服务器部署脚本"
echo "=============================================="

# 配置变量
APP_NAME="beesyncclip"
APP_USER="beesync"
APP_DIR="/opt/beesyncclip"
LOG_DIR="/var/log/beesyncclip"
SERVICE_NAME="beesyncclip"
PYTHON_VERSION="3.11"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否以root身份运行
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要以root身份运行"
        exit 1
    fi
}

# 更新系统
update_system() {
    log_info "更新系统软件包..."
    yum update -y
    yum groupinstall -y "Development Tools"
    yum install -y wget curl git vim htop
}

# 安装Python 3.11
install_python() {
    log_info "检查Python版本..."
    
    if python3.11 --version >/dev/null 2>&1; then
        log_info "Python 3.11 已安装"
        return 0
    fi
    
    log_info "安装Python 3.11..."
    # 安装EPEL仓库
    yum install -y epel-release
    
    # 安装Python 3.11依赖
    yum install -y python3-devel python3-pip
    
    # 如果系统没有Python 3.11，通过源码编译安装
    if ! python3.11 --version >/dev/null 2>&1; then
        log_info "从源码编译安装Python 3.11..."
        cd /tmp
        wget https://www.python.org/ftp/python/3.11.5/Python-3.11.5.tgz
        tar xzf Python-3.11.5.tgz
        cd Python-3.11.5
        ./configure --enable-optimizations --with-ssl
        make altinstall
        ln -sf /usr/local/bin/python3.11 /usr/bin/python3.11
        ln -sf /usr/local/bin/pip3.11 /usr/bin/pip3.11
    fi
}

# 安装Redis
install_redis() {
    log_info "安装Redis..."
    
    if systemctl is-active --quiet redis; then
        log_info "Redis已安装并运行"
        return 0
    fi
    
    yum install -y redis
    
    # 配置Redis
    cp /etc/redis.conf /etc/redis.conf.bak
    
    # 修改Redis配置
    sed -i 's/^bind 127.0.0.1/bind 0.0.0.0/' /etc/redis.conf
    sed -i 's/^# maxmemory <bytes>/maxmemory 512mb/' /etc/redis.conf
    sed -i 's/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis.conf
    
    # 启动Redis
    systemctl enable redis
    systemctl start redis
    
    log_info "Redis安装并启动成功"
}

# 创建应用用户
create_app_user() {
    log_info "创建应用用户..."
    
    if id "$APP_USER" &>/dev/null; then
        log_info "用户 $APP_USER 已存在"
    else
        useradd -r -s /bin/bash -d $APP_DIR $APP_USER
        log_info "创建用户 $APP_USER 成功"
    fi
}

# 创建目录结构
create_directories() {
    log_info "创建目录结构..."
    
    mkdir -p $APP_DIR
    mkdir -p $LOG_DIR
    mkdir -p /etc/beesyncclip
    
    chown -R $APP_USER:$APP_USER $APP_DIR
    chown -R $APP_USER:$APP_USER $LOG_DIR
    
    log_info "目录结构创建完成"
}

# 部署应用代码
deploy_application() {
    log_info "部署应用代码..."
    
    # 假设代码已经在当前目录
    if [[ ! -d "./BeeSyncClip" ]]; then
        log_error "未找到BeeSyncClip源代码目录"
        exit 1
    fi
    
    # 复制代码到应用目录
    cp -r ./BeeSyncClip/* $APP_DIR/
    
    # 复制阿里云配置文件
    cp $APP_DIR/config/aliyun_settings.yaml /etc/beesyncclip/settings.yaml
    
    # 设置权限
    chown -R $APP_USER:$APP_USER $APP_DIR
    chmod +x $APP_DIR/server/main_server.py
    
    log_info "应用代码部署完成"
}

# 安装Python依赖
install_python_dependencies() {
    log_info "安装Python依赖..."
    
    cd $APP_DIR
    
    # 创建虚拟环境
    python3.11 -m venv venv
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    if [[ -f "requirements-freeze.txt" ]]; then
        pip install -r requirements-freeze.txt
    else
        log_error "未找到requirements-freeze.txt文件"
        exit 1
    fi
    
    deactivate
    
    # 设置权限
    chown -R $APP_USER:$APP_USER $APP_DIR/venv
    
    log_info "Python依赖安装完成"
}

# 创建systemd服务文件
create_systemd_service() {
    log_info "创建systemd服务..."
    
    cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=BeeSyncClip Cross-Platform Clipboard Sync Service
After=network.target redis.service
Requires=redis.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PYTHONPATH=$APP_DIR
Environment=CONFIG_FILE=/etc/beesyncclip/settings.yaml
ExecStart=$APP_DIR/venv/bin/python server/main_server.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

# 资源限制
LimitNOFILE=65536
MemoryMax=1G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    log_info "systemd服务创建完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    # 检查firewalld是否运行
    if systemctl is-active --quiet firewalld; then
        firewall-cmd --permanent --add-port=8000/tcp
        firewall-cmd --permanent --add-port=8765/tcp
        firewall-cmd --reload
        log_info "防火墙端口已开放: 8000, 8765"
    else
        log_warn "firewalld未运行，请手动配置安全组"
    fi
}

# 配置Nginx反向代理（可选）
install_nginx() {
    log_info "是否安装Nginx反向代理? (y/n)"
    read -r install_nginx_choice
    
    if [[ $install_nginx_choice == "y" || $install_nginx_choice == "Y" ]]; then
        yum install -y nginx
        
        # 创建Nginx配置
        cat > /etc/nginx/conf.d/beesyncclip.conf << EOF
server {
    listen 80;
    server_name _;  # 请修改为您的域名
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /ws {
        proxy_pass http://127.0.0.1:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
        
        systemctl enable nginx
        systemctl start nginx
        
        log_info "Nginx反向代理配置完成"
    fi
}

# 启动服务
start_services() {
    log_info "启动BeeSyncClip服务..."
    
    systemctl enable $SERVICE_NAME
    systemctl start $SERVICE_NAME
    
    # 等待服务启动
    sleep 5
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_info "BeeSyncClip服务启动成功"
    else
        log_error "BeeSyncClip服务启动失败"
        systemctl status $SERVICE_NAME
        exit 1
    fi
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "=============================================="
    echo "           部署完成！"
    echo "=============================================="
    echo ""
    echo "服务状态:"
    systemctl status $SERVICE_NAME --no-pager -l
    echo ""
    echo "服务端点:"
    echo "  HTTP API: http://$(curl -s ifconfig.me || echo 'YOUR_SERVER_IP'):8000"
    echo "  WebSocket: ws://$(curl -s ifconfig.me || echo 'YOUR_SERVER_IP'):8765"
    echo ""
    echo "管理命令:"
    echo "  启动服务: systemctl start $SERVICE_NAME"
    echo "  停止服务: systemctl stop $SERVICE_NAME"
    echo "  重启服务: systemctl restart $SERVICE_NAME"
    echo "  查看状态: systemctl status $SERVICE_NAME"
    echo "  查看日志: journalctl -u $SERVICE_NAME -f"
    echo ""
    echo "配置文件: /etc/beesyncclip/settings.yaml"
    echo "应用目录: $APP_DIR"
    echo "日志目录: $LOG_DIR"
    echo ""
}

# 主函数
main() {
    log_info "开始部署BeeSyncClip到阿里云服务器..."
    
    check_root
    update_system
    install_python
    install_redis
    create_app_user
    create_directories
    deploy_application
    install_python_dependencies
    create_systemd_service
    configure_firewall
    install_nginx
    start_services
    show_deployment_info
    
    log_info "部署完成！"
}

# 执行主函数
main "$@" 
#!/bin/bash

# BeeSyncClip Ubuntu服务器部署脚本
# 作者: BeeSyncClip Team  
# 版本: 1.0

set -e  # 遇到错误立即退出

echo "=============================================="
echo "     BeeSyncClip Ubuntu服务器部署脚本"
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

# 检查是否以sudo权限运行
check_sudo() {
    if [[ $EUID -eq 0 ]]; then
        log_warn "检测到以root身份运行，建议使用sudo"
    fi
    
    # 测试sudo权限
    if ! sudo -n true 2>/dev/null; then
        log_info "需要sudo权限来安装系统组件"
        sudo -v
    fi
}

# 更新系统
update_system() {
    log_info "更新系统软件包..."
    sudo apt update
    sudo apt upgrade -y
    sudo apt install -y build-essential curl wget git vim htop software-properties-common
}

# 安装Python 3.11
install_python() {
    log_info "检查Python版本..."
    
    if python3.11 --version >/dev/null 2>&1; then
        log_info "Python 3.11 已安装"
        return 0
    fi
    
    log_info "安装Python 3.11..."
    
    # 添加deadsnakes PPA
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    
    # 安装Python 3.11和相关工具
    sudo apt install -y python3.11 python3.11-dev python3.11-venv python3-pip
    
    # 创建符号链接
    sudo ln -sf /usr/bin/python3.11 /usr/local/bin/python3.11
    
    log_info "Python 3.11 安装完成"
}

# 安装Redis
install_redis() {
    log_info "安装Redis..."
    
    if systemctl is-active --quiet redis-server; then
        log_info "Redis已安装并运行"
        return 0
    fi
    
    sudo apt install -y redis-server
    
    # 配置Redis
    sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.bak
    
    # 修改Redis配置
    sudo sed -i 's/^bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf
    sudo sed -i 's/^# maxmemory <bytes>/maxmemory 512mb/' /etc/redis/redis.conf
    sudo sed -i 's/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
    
    # 启动Redis
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
    
    log_info "Redis安装并启动成功"
}

# 创建应用用户
create_app_user() {
    log_info "创建应用用户..."
    
    if id "$APP_USER" &>/dev/null; then
        log_info "用户 $APP_USER 已存在"
    else
        sudo useradd -r -s /bin/bash -d $APP_DIR $APP_USER
        log_info "创建用户 $APP_USER 成功"
    fi
}

# 创建目录结构
create_directories() {
    log_info "创建目录结构..."
    
    sudo mkdir -p $APP_DIR
    sudo mkdir -p $LOG_DIR
    sudo mkdir -p /etc/beesyncclip
    
    sudo chown -R $APP_USER:$APP_USER $APP_DIR
    sudo chown -R $APP_USER:$APP_USER $LOG_DIR
    
    log_info "目录结构创建完成"
}

# 部署应用代码
deploy_application() {
    log_info "部署应用代码..."
    
    # 假设代码已经在当前目录
    if [[ ! -d "server" ]]; then
        log_error "未找到BeeSyncClip源代码目录"
        exit 1
    fi
    
    # 复制代码到应用目录
    sudo cp -r ./* $APP_DIR/
    
    # 复制阿里云配置文件
    if [[ -f "$APP_DIR/config/aliyun_settings.yaml" ]]; then
        sudo cp $APP_DIR/config/aliyun_settings.yaml /etc/beesyncclip/settings.yaml
    else
        sudo cp $APP_DIR/config/settings.yaml /etc/beesyncclip/settings.yaml
    fi
    
    # 设置权限
    sudo chown -R $APP_USER:$APP_USER $APP_DIR
    sudo chmod +x $APP_DIR/server/main_server.py
    
    log_info "应用代码部署完成"
}

# 安装Python依赖
install_python_dependencies() {
    log_info "安装Python依赖..."
    
    cd $APP_DIR
    
    # 创建虚拟环境
    sudo -u $APP_USER python3.11 -m venv venv
    
    # 激活虚拟环境并安装依赖
    sudo -u $APP_USER bash -c "
        source venv/bin/activate
        pip install --upgrade pip
        if [[ -f 'requirements.txt' ]]; then
            pip install -r requirements.txt
        else
            echo '未找到requirements.txt文件'
            exit 1
        fi
    "
    
    log_info "Python依赖安装完成"
}

# 创建systemd服务文件
create_systemd_service() {
    log_info "创建systemd服务..."
    
    sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOF
[Unit]
Description=BeeSyncClip Cross-Platform Clipboard Sync Service
After=network.target redis-server.service
Requires=redis-server.service

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

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    log_info "systemd服务创建完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    # Ubuntu使用ufw防火墙
    if command -v ufw >/dev/null 2>&1; then
        sudo ufw allow 8000/tcp
        sudo ufw allow 8765/tcp
        sudo ufw allow ssh
        log_info "防火墙端口已开放: 8000, 8765"
    else
        log_warn "ufw未安装，请手动配置安全组"
    fi
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动并启用服务
    sudo systemctl enable $SERVICE_NAME
    sudo systemctl start $SERVICE_NAME
    
    # 检查服务状态
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_info "BeeSyncClip服务启动成功 ✓"
    else
        log_error "BeeSyncClip服务启动失败"
        sudo journalctl -u $SERVICE_NAME -n 20
        exit 1
    fi
}

# 显示部署信息
show_deployment_info() {
    log_info "部署完成！"
    echo ""
    echo "📊 服务信息:"
    echo "API端点: http://47.110.154.99:8000"
    echo "WebSocket端点: ws://47.110.154.99:8765"
    echo "健康检查: curl http://47.110.154.99:8000/health"
    echo ""
    echo "===== 常用命令 ====="
    echo "查看服务状态: sudo systemctl status $SERVICE_NAME"
    echo "查看服务日志: sudo journalctl -u $SERVICE_NAME -f"
    echo "重启服务: sudo systemctl restart $SERVICE_NAME"
    echo "停止服务: sudo systemctl stop $SERVICE_NAME"
    echo ""
}

# 主函数
main() {
    log_info "开始部署BeeSyncClip到Ubuntu服务器..."
    
    check_sudo
    update_system
    install_python
    install_redis
    create_app_user
    create_directories
    deploy_application
    install_python_dependencies
    create_systemd_service
    configure_firewall
    start_services
    show_deployment_info
    
    log_info "🎉 部署完成！BeeSyncClip已成功部署到Ubuntu服务器"
}

# 如果直接运行脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 
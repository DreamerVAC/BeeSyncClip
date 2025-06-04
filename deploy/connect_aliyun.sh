#!/bin/bash

# BeeSyncClip 阿里云服务器连接脚本

echo "=============================================="
echo "     BeeSyncClip 阿里云服务器连接工具"
echo "=============================================="

# 配置变量 (请修改为您的实际信息)
ALIYUN_IP="47.110.154.99"               # 您的ECS公网IP
ALIYUN_USER="ubuntu"                     # SSH用户名 (Ubuntu服务器)
SSH_KEY="~/.ssh/id_rsa"                 # SSH私钥路径 (可选)

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查配置
check_config() {
    if [[ "$ALIYUN_IP" == "YOUR_ECS_PUBLIC_IP" ]]; then
        log_error "请在脚本中配置您的阿里云ECS公网IP地址"
        echo "请编辑 deploy/connect_aliyun.sh 文件，修改 ALIYUN_IP 变量"
        exit 1
    fi
}

# 测试连接
test_connection() {
    log_info "测试服务器连接..."
    
    if ping -c 1 "$ALIYUN_IP" &> /dev/null; then
        log_info "服务器网络连通 ✓"
    else
        log_warn "服务器ping失败，可能是防火墙设置"
    fi
    
    # 测试SSH端口
    if timeout 5 bash -c "</dev/tcp/$ALIYUN_IP/22" &> /dev/null; then
        log_info "SSH端口(22)开放 ✓"
    else
        log_error "SSH端口(22)无法访问，请检查安全组配置"
        exit 1
    fi
}

# SSH连接 (密钥方式)
connect_with_key() {
    log_info "使用SSH密钥连接服务器..."
    
    if [[ ! -f "$SSH_KEY" ]]; then
        log_error "SSH密钥文件不存在: $SSH_KEY"
        return 1
    fi
    
    ssh -i "$SSH_KEY" "$ALIYUN_USER@$ALIYUN_IP"
}

# SSH连接 (密码方式)
connect_with_password() {
    log_info "使用密码连接服务器..."
    log_warn "请输入服务器密码:"
    
    ssh "$ALIYUN_USER@$ALIYUN_IP"
}

# 上传代码到服务器
upload_code() {
    log_info "上传BeeSyncClip代码到服务器..."
    
    # 创建代码包
    cd ..
    tar -czf BeeSyncClip.tar.gz \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.vscode' \
        --exclude='logs/*' \
        BeeSyncClip/
    
    # 上传到服务器
    if [[ -f "$SSH_KEY" ]]; then
        scp -i "$SSH_KEY" BeeSyncClip.tar.gz "$ALIYUN_USER@$ALIYUN_IP:/tmp/"
    else
        scp BeeSyncClip.tar.gz "$ALIYUN_USER@$ALIYUN_IP:/tmp/"
    fi
    
    log_info "代码上传完成: /tmp/BeeSyncClip.tar.gz"
    rm BeeSyncClip.tar.gz
}

# 主菜单
show_menu() {
    echo ""
    echo "请选择操作:"
    echo "1) 测试连接"
    echo "2) SSH连接 (密钥)"
    echo "3) SSH连接 (密码)"
    echo "4) 上传代码"
    echo "5) 一键部署"
    echo "q) 退出"
    echo ""
    read -p "请输入选项 [1-5/q]: " choice
    
    case $choice in
        1) test_connection ;;
        2) connect_with_key ;;
        3) connect_with_password ;;
        4) upload_code ;;
        5) deploy_all ;;
        q) exit 0 ;;
        *) log_error "无效选项" ;;
    esac
}

# 一键部署
deploy_all() {
    log_info "开始一键部署..."
    
    # 1. 上传代码
    upload_code
    
    # 2. 连接服务器并执行部署
    log_info "连接服务器执行部署脚本..."
    
    ssh_command="
        cd /tmp && 
        tar -xzf BeeSyncClip.tar.gz && 
        cd BeeSyncClip && 
        chmod +x deploy/ubuntu_deploy.sh && 
        ./deploy/ubuntu_deploy.sh
    "
    
    if [[ -f "$SSH_KEY" ]]; then
        ssh -i "$SSH_KEY" "$ALIYUN_USER@$ALIYUN_IP" "$ssh_command"
    else
        ssh "$ALIYUN_USER@$ALIYUN_IP" "$ssh_command"
    fi
}

# 主程序
main() {
    check_config
    
    while true; do
        show_menu
    done
}

# 如果直接运行脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 
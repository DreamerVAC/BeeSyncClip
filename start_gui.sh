#!/bin/bash

# BeeSyncClip GUI 客户端启动脚本 - PyQt5版本

echo "🚀 BeeSyncClip GUI 客户端启动器 (PyQt5版本)"
echo "============================================"

# 检查服务器连接 - 直接连接模式
echo "📡 检查服务器连接..."

# 首先尝试8000端口
if curl -s --connect-timeout 3 http://47.110.154.99:8000/health > /dev/null 2>&1; then
    echo "✅ 服务器连接正常 (端口8000)"
    SERVER_URL="http://47.110.154.99:8000"
# 如果8000端口不通，尝试80端口
elif curl -s --connect-timeout 3 http://47.110.154.99/health > /dev/null 2>&1; then
    echo "✅ 服务器连接正常 (端口80)"
    SERVER_URL="http://47.110.154.99"
else
    echo "❌ 无法连接到服务器"
    echo ""
    echo "🔧 解决方案："
    echo "1. 配置阿里云安全组开放8000端口"
    echo "   - 访问: https://ecs.console.aliyun.com"
    echo "   - 添加规则: TCP 8000/8000, 授权对象: 0.0.0.0/0"
    echo ""
    echo "2. 或使用80端口启动服务器（在服务器上执行）："
    echo "   sudo ./start_server_port80.sh"
    echo ""
    echo "3. 或使用SSH隧道："
    echo "   ssh -L 8000:localhost:8000 ubuntu@47.110.154.99 -N"
    exit 1
fi

# 检查Python依赖
echo "🔍 检查依赖..."
if python3 -c "import PyQt5, pyperclip" > /dev/null 2>&1; then
    echo "✅ 依赖检查通过"
else
    echo "❌ 缺少依赖，正在安装..."
    pip install PyQt5 pyperclip requests
fi

# 启动GUI客户端
echo "🎨 启动GUI客户端..."
echo ""
echo "📱 登录信息:"
echo "   新用户请在界面中注册账号"
echo "   服务器: $SERVER_URL"
echo ""

# 设置环境变量供GUI客户端使用
export BEESYNCCLIP_SERVER_URL="$SERVER_URL"

# 启动PyQt5客户端
python3 client/main.py

echo "👋 GUI客户端已关闭" 
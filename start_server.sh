#!/bin/bash

# BeeSyncClip 后端服务器启动脚本

echo "🚀 BeeSyncClip 后端服务器"
echo "========================="

# 检查Python依赖
echo "🔍 检查服务器依赖..."
if [ -f "requirements-server.txt" ]; then
    echo "📦 安装服务器依赖..."
    pip install -r requirements-server.txt
    if [ $? -ne 0 ]; then
        echo "❌ 服务器依赖安装失败！"
        exit 1
    fi
else
    echo "⚠️ 未找到requirements-server.txt，请确保已安装所需依赖"
fi

# 检查Redis服务
echo "🔍 检查Redis服务..."
if ! systemctl is-active --quiet redis; then
    echo "⚠️ Redis服务未运行，正在启动..."
    sudo systemctl start redis
    sleep 2
fi

if systemctl is-active --quiet redis; then
    echo "✅ Redis服务正常运行"
else
    echo "❌ Redis服务启动失败！"
    exit 1
fi

# 启动服务器
echo "🎯 启动BeeSyncClip服务器..."
echo "📱 新用户请在客户端界面进行注册"

python3 start_frontend_server.py 
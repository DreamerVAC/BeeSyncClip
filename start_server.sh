#!/bin/bash

# BeeSyncClip 后端服务器启动脚本

echo "🚀 BeeSyncClip 后端服务器"
echo "========================="

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
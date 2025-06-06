#!/bin/bash

# BeeSyncClip 服务器启动脚本

echo "🚀 启动 BeeSyncClip 服务器..."

# 检查Redis是否运行
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis 未运行，请先启动 Redis 服务"
    exit 1
fi

echo "✅ Redis 连接正常"

# 检查端口是否被占用
if netstat -tuln | grep :8000 > /dev/null 2>&1; then
    echo "⚠️  端口 8000 已被占用，尝试停止现有进程..."
    pkill -f "start_frontend_server.py" || true
    sleep 2
fi

# 启动服务器
echo "🌐 启动服务器在端口 8000..."
echo "📱 测试账号: testuser / test123"
echo "🔗 服务器地址: http://47.110.154.99:8000"
echo "📋 按 Ctrl+C 停止服务器"
echo ""

python start_frontend_server.py 
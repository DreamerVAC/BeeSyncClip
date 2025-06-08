#!/bin/bash

# BeeSyncClip 服务器后台启动脚本 (阿里云生产环境)

LOG_FILE="beesyncclip.log"
PID_FILE="beesyncclip.pid"

echo "🚀 启动 BeeSyncClip 服务器 (后台模式)..."

# 检查Python依赖
echo "🔍 检查服务器依赖..."
if [ -f "requirements-server.txt" ]; then
    echo "📦 确保服务器依赖已安装..."
    pip install -r requirements-server.txt --quiet
fi

# 检查Redis是否运行
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis 未运行，请先启动 Redis 服务"
    exit 1
fi

echo "✅ Redis 连接正常"

# 检查是否已经在运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  服务器已在运行 (PID: $PID)"
        exit 1
    else
        echo "🧹 清理过期的PID文件"
        rm -f "$PID_FILE"
    fi
fi

# 停止现有进程
echo "🔄 停止现有进程..."
pkill -f "start_frontend_server.py" || true
sleep 2

# 启动服务器
echo "🌐 启动服务器在端口 8000 (后台模式)..."
echo "📱 新用户请在客户端界面进行注册"
echo "🔗 服务器地址: http://47.110.154.99:8000"
echo "📄 日志文件: $LOG_FILE"

nohup python start_frontend_server.py > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# 保存PID
echo "$SERVER_PID" > "$PID_FILE"

# 等待几秒检查启动状态
sleep 3

if ps -p "$SERVER_PID" > /dev/null 2>&1; then
    echo "✅ 服务器启动成功 (PID: $SERVER_PID)"
    echo "📋 使用以下命令管理服务器:"
    echo "   查看状态: ./status.sh"
    echo "   停止服务: ./stop_server.sh"
    echo "   查看日志: tail -f $LOG_FILE"
else
    echo "❌ 服务器启动失败，请检查日志: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi 
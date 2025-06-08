#!/bin/bash

# BeeSyncClip GUI 客户端停止脚本

PID_FILE="client.pid"

echo "🛑 停止 BeeSyncClip GUI 客户端..."

# 检查PID文件是否存在
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    # 检查进程是否还在运行
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "📋 发现运行中的客户端进程 (PID: $PID)"
        
        # 优雅停止
        echo "🔄 正在停止客户端..."
        kill "$PID"
        
        # 等待进程结束
        for i in {1..10}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                echo "✅ 客户端已停止"
                rm -f "$PID_FILE"
                exit 0
            fi
            sleep 1
        done
        
        # 强制停止
        echo "⚡ 强制停止进程..."
        kill -9 "$PID" 2>/dev/null
        
        if ! ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ 客户端已强制停止"
            rm -f "$PID_FILE"
        else
            echo "❌ 无法停止进程"
            exit 1
        fi
    else
        echo "ℹ️  进程已不在运行，清理PID文件"
        rm -f "$PID_FILE"
    fi
else
    echo "ℹ️  PID文件不存在，尝试停止所有相关进程..."
fi

# 停止所有相关进程
pkill -f "client/ui/form_ui.py" && echo "✅ 已停止所有相关进程" || echo "ℹ️  未发现运行中的进程" 
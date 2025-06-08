#!/bin/bash

# BeeSyncClip GUI 客户端启动脚本 (PyQt5版本)
# 
# 使用方法:
#   ./start_client.sh           # 前台启动 (占用终端)
#   ./start_client.sh -d        # 后台启动 (不占用终端)
#   ./start_client.sh --daemon  # 后台启动 (同上)

# 检查命令行参数
DAEMON_MODE=false
LOG_FILE="client.log"
PID_FILE="client.pid"

if [ "$1" = "-d" ] || [ "$1" = "--daemon" ]; then
    DAEMON_MODE=true
    echo "🚀 BeeSyncClip GUI 客户端启动器 (后台模式)"
    echo "==========================================="
else
    echo "🚀 BeeSyncClip GUI 客户端启动器"
    echo "================================"
fi

# 检查Python依赖
echo "🔍 检查依赖..."
missing_deps=()

python3 -c "import PyQt5" 2>/dev/null || missing_deps+=("PyQt5")
python3 -c "import pyperclip" 2>/dev/null || missing_deps+=("pyperclip")
python3 -c "import requests" 2>/dev/null || missing_deps+=("requests")

if [ ${#missing_deps[@]} -ne 0 ]; then
    echo "❌ 缺少依赖: ${missing_deps[*]}"
    echo "正在安装客户端依赖..."
    
    if [ -f "requirements-client.txt" ]; then
        pip install -r requirements-client.txt
    else
        echo "⚠️ 未找到requirements-client.txt，使用备用安装方式"
        pip install PyQt5 pyperclip requests PyYAML loguru
    fi
    
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败，请手动安装："
        echo "pip install -r requirements-client.txt"
        echo "或者："
        echo "pip install PyQt5 pyperclip requests PyYAML loguru"
        exit 1
    fi
fi

echo "✅ 依赖检查通过"

# 后台模式下检查是否已经在运行
if [ "$DAEMON_MODE" = true ]; then
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "⚠️  客户端已在运行 (PID: $PID)"
            echo "📋 使用以下命令管理客户端:"
            echo "   查看日志: tail -f $LOG_FILE"
            echo "   停止客户端: ./stop_client.sh"
            exit 1
        else
            echo "🧹 清理过期的PID文件"
            rm -f "$PID_FILE"
        fi
    fi
    
    # 停止现有进程（如果有的话）
    echo "🔄 停止现有客户端进程..."
    pkill -f "client/ui/form_ui.py" || true
    sleep 1
fi

# 启动GUI客户端
if [ "$DAEMON_MODE" = true ]; then
    echo "🎨 启动GUI客户端 (后台模式)..."
    echo "📄 日志文件: $LOG_FILE"
    echo "📱 使用说明:"
    echo "   • GUI界面将在后台启动"
    echo "   • 新用户请在界面中注册账号"
    echo "   • 默认连接服务器: http://47.110.154.99:8000"
    echo ""
    
    # 使用nohup启动，重定向输出到日志文件
    nohup python3 client/ui/form_ui.py > "$LOG_FILE" 2>&1 &
    CLIENT_PID=$!
    
    # 保存PID
    echo "$CLIENT_PID" > "$PID_FILE"
    
    # 等待几秒检查启动状态
    sleep 3
    
    if ps -p "$CLIENT_PID" > /dev/null 2>&1; then
        echo "✅ 客户端启动成功 (PID: $CLIENT_PID)"
        echo "📋 使用以下命令管理客户端:"
        echo "   查看日志: tail -f $LOG_FILE"
        echo "   停止客户端: ./stop_client.sh"
        echo ""
        echo "🎯 GUI界面现在应该已经显示，可以关闭此终端窗口"
    else
        echo "❌ 客户端启动失败，请检查日志: $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
else
    echo "🎨 启动GUI客户端..."
    echo ""
    echo "📱 使用说明:"
    echo "   • 新用户请在界面中注册账号"
    echo "   • 默认连接服务器: http://47.110.154.99:8000"
    echo "   • 支持实时剪贴板同步"
    echo ""
    
    # 前台启动PyQt5客户端
    python3 client/ui/form_ui.py
    
    echo "👋 GUI客户端已关闭"
fi 
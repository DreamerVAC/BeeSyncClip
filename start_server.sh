#!/bin/bash

# BeeSyncClip 服务器启动脚本
# 支持前台/后台模式、不同端口(8000/80)启动

LOG_FILE="beesyncclip.log"
PID_FILE="beesyncclip.pid"
DEFAULT_PORT=8000
DEFAULT_HOST="0.0.0.0"

# 显示使用说明
show_usage() {
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -d, --daemon         后台模式启动"
    echo "  -f, --foreground     前台模式启动 (默认)"
    echo "  -p, --port PORT      指定端口 (默认: 8000)"
    echo "  --port80             使用80端口启动 (需要sudo权限)"
    echo "  -h, --help           显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                   # 前台启动，端口8000"  
    echo "  $0 -d                # 后台启动，端口8000"
    echo "  $0 -p 3000           # 前台启动，端口3000"
    echo "  $0 -d -p 9000        # 后台启动，端口9000"
    echo "  $0 --port80          # 前台启动，端口80 (需要sudo)"
    echo "  sudo $0 -d --port80  # 后台启动，端口80"
    echo ""
    echo "注意:"
    echo "  - 使用80端口需要sudo权限"
    echo "  - 后台模式日志输出到: $LOG_FILE"
    echo "  - 使用 ./status.sh 查看后台服务状态"
    echo "  - 使用 ./stop_server.sh 停止后台服务"
}

# 解析命令行参数
DAEMON_MODE=false
PORT=$DEFAULT_PORT
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--daemon)
            DAEMON_MODE=true
            shift
            ;;
        -f|--foreground)
            DAEMON_MODE=false
            shift
            ;;
        -p|--port)
            if [[ -n "$2" && "$2" =~ ^[0-9]+$ ]]; then
                PORT="$2"
                shift 2
            else
                echo "❌ 端口号必须是数字"
                exit 1
            fi
            ;;
        --port80)
            PORT=80
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "❌ 未知选项: $1"
            show_usage
            exit 1
            ;;
    esac
done

echo "🚀 BeeSyncClip 后端服务器"
echo "========================="

if [ "$DAEMON_MODE" = true ]; then
    echo "🌙 启动模式: 后台模式"
else
    echo "🌞 启动模式: 前台模式"
fi

echo "🔌 端口: $PORT"

# 检查80端口权限
if [ "$PORT" -eq 80 ]; then
    if [[ $EUID -ne 0 ]]; then
        echo "❌ 使用80端口需要sudo权限"
        echo "💡 请使用: sudo $0 --port80"
        exit 1
    fi
    echo "⚡ 使用管理员权限启动80端口服务"
    
    # 80端口特殊处理 - 设置Python环境路径
    PYTHON_PATH="/home/work/miniconda3/envs/software/bin/python3"
    if [ ! -f "$PYTHON_PATH" ]; then
        echo "❌ Python环境未找到: $PYTHON_PATH"
        echo "💡 请检查conda环境是否正确"
        exit 1
    fi
    PYTHON_CMD="$PYTHON_PATH"
else
    PYTHON_CMD="python3"
fi

# 检查端口占用
echo "🔍 检查端口 $PORT 占用情况..."
if netstat -tuln | grep ":$PORT " > /dev/null; then
    echo "⚠️  端口 $PORT 已被占用"
    echo "占用端口 $PORT 的进程:"
    netstat -tuln | grep ":$PORT "
    echo ""
    if [ "$PORT" -eq 80 ]; then
        echo "💡 如果确定要继续，请先停止占用80端口的服务"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "💡 请选择其他端口或停止占用该端口的进程"
        exit 1
    fi
fi

# 检查Python依赖
echo "🔍 检查服务器依赖..."
if [ -f "requirements-server.txt" ]; then
    echo "📦 安装服务器依赖..."
    if [ "$DAEMON_MODE" = true ]; then
        pip install -r requirements-server.txt --quiet
    else
        pip install -r requirements-server.txt
    fi
    if [ $? -ne 0 ]; then
        echo "❌ 服务器依赖安装失败！"
        exit 1
    fi
else
    echo "⚠️ 未找到requirements-server.txt，请确保已安装所需依赖"
fi

# 检查Redis服务
echo "🔍 检查Redis服务..."
if [ "$DAEMON_MODE" = true ]; then
    # 后台模式：检查Redis连接
    if ! redis-cli ping > /dev/null 2>&1; then
        echo "❌ Redis 未运行，请先启动 Redis 服务"
        exit 1
    fi
    echo "✅ Redis 连接正常"
else
    # 前台模式：尝试启动Redis (仅非80端口)
    if [ "$PORT" -ne 80 ]; then
        if ! systemctl is-active --quiet redis; then
            echo "⚠️ Redis服务未运行，正在启动..."
            sudo systemctl start redis
            sleep 2
        fi
    fi
    
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis服务正常运行"
    else
        echo "❌ Redis服务启动失败！"
        exit 1
    fi
fi

# 创建动态启动脚本
create_startup_script() {
    local temp_script="/tmp/start_beesyncclip_${PORT}.py"
    
    cat > "$temp_script" << EOF
#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = "/home/work/software"
sys.path.insert(0, project_root)

# 导入服务器应用
from server.frontend_compatible_server import app

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动BeeSyncClip服务器 (端口$PORT)...")
    print("✅ Redis连接正常")
    port = $PORT
    if port == 80:
        print("🌐 访问地址: http://47.110.154.99")
    else:
        print(f"🌐 访问地址: http://47.110.154.99:{port}")
    print("📱 新用户请在客户端界面进行注册")
    print("🎯 Ready for production!")
    
    uvicorn.run(
        app,
        host="$DEFAULT_HOST",
        port=$PORT,
        log_level="info"
    )
EOF
    
    chmod +x "$temp_script"
    echo "$temp_script"
}

if [ "$DAEMON_MODE" = true ]; then
    # 后台模式启动逻辑
    echo "🔍 检查是否已在后台运行..."
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "⚠️  服务器已在运行 (PID: $PID)"
            echo "💡 使用 ./stop_server.sh 停止现有服务器"
            exit 1
        else
            echo "🧹 清理过期的PID文件"
            rm -f "$PID_FILE"
        fi
    fi
    
    # 停止现有进程
    echo "🔄 停止现有进程..."
    pkill -f "start_frontend_server.py" || true
    pkill -f "start_beesyncclip_" || true
    sleep 2
    
    # 创建启动脚本
    STARTUP_SCRIPT=$(create_startup_script)
    
    # 后台启动服务器
    echo "🌐 启动服务器在端口 $PORT (后台模式)..."
    echo "📱 新用户请在客户端界面进行注册"
    if [ "$PORT" -eq 80 ]; then
        echo "🔗 服务器地址: http://47.110.154.99"
    else
        echo "🔗 服务器地址: http://47.110.154.99:$PORT"
    fi
    echo "📄 日志文件: $LOG_FILE"
    
    nohup $PYTHON_CMD "$STARTUP_SCRIPT" > "$LOG_FILE" 2>&1 &
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
else
    # 前台模式启动逻辑
    echo "🎯 启动BeeSyncClip服务器 (前台模式)..."
    echo "📱 新用户请在客户端界面进行注册"
    echo "💡 按 Ctrl+C 停止服务器"
    
    if [ "$PORT" -eq 8000 ]; then
        # 使用原始启动脚本
        $PYTHON_CMD start_frontend_server.py
    else
        # 创建并使用动态启动脚本
        STARTUP_SCRIPT=$(create_startup_script)
        $PYTHON_CMD "$STARTUP_SCRIPT"
        # 清理临时脚本
        rm -f "$STARTUP_SCRIPT"
    fi
fi 
#!/bin/bash

# BeeSyncClip 服务器启动脚本
# 支持原始服务器和新模块化服务器
# 支持前台/后台模式、不同端口(8000/80)启动

LOG_FILE="beesyncclip.log"
PID_FILE="beesyncclip.pid"
DEFAULT_PORT=8000
DEFAULT_HOST="0.0.0.0"

# 显示使用说明
show_usage() {
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -m, --modular        启动新模块化服务器 (默认,推荐)"
    echo "  -o, --original       启动原始服务器"
    echo "  -d, --daemon         后台模式启动"
    echo "  -f, --foreground     前台模式启动 (默认)"
    echo "  -p, --port PORT      指定端口 (默认: 8000)"
    echo "  --port80             使用80端口启动 (需要sudo权限)"
    echo "  -h, --help           显示此帮助信息"
    echo ""
    echo "服务器版本:"
    echo "  🔥 模块化服务器 (推荐): 企业级安全、性能优化、完全兼容"
    echo "     - AES-256加密 + JWT认证"
    echo "     - 解决多设备同步卡顿问题"
    echo "     - 批量查询优化，性能提升20%"
    echo "     - 100%向后兼容原始API"
    echo ""
    echo "  📦 原始服务器: 传统版本，稳定运行"
    echo ""
    echo "示例:"
    echo "  $0                   # 启动模块化服务器 (默认)"
    echo "  $0 -d                # 后台启动模块化服务器"
    echo "  $0 -o                # 启动原始服务器"
    echo "  $0 -o -d             # 后台启动原始服务器"
    echo "  $0 -m -p 3000        # 模块化服务器，端口3000"
    echo "  $0 --port80 -m       # 模块化服务器，端口80 (需要sudo)"
    echo ""
    echo "注意:"
    echo "  - 推荐使用模块化服务器 (-m)，性能更好，安全性更强"
    echo "  - 使用80端口需要sudo权限"
    echo "  - 后台模式日志输出到: $LOG_FILE"
    echo "  - 使用 ./status.sh 查看后台服务状态"
    echo "  - 使用 ./stop_server.sh 停止后台服务"
}

# 解析命令行参数
DAEMON_MODE=false
PORT=$DEFAULT_PORT
USE_MODULAR=true  # 默认使用模块化服务器 (推荐)

while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--modular)
            USE_MODULAR=true
            shift
            ;;
        -o|--original)
            USE_MODULAR=false
            shift
            ;;
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

if [ "$USE_MODULAR" = true ]; then
    echo "🔥 服务器版本: 模块化服务器 v2.0 (推荐)"
    echo "   ✅ AES-256加密 + JWT认证"
    echo "   ✅ 性能优化 + 批量查询"
    echo "   ✅ 100%向后兼容"
else
    echo "📦 服务器版本: 原始服务器 v1.0"
fi

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

# 检查 Python 版本
echo "🔍 检查 Python 版本..."
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print("{}.{}.{}".format(*sys.version_info[:3]))')
if $PYTHON_CMD -c 'import sys; exit(not (sys.version_info[:2] >= (3,11)))'; then
    echo "✅ Python 版本满足要求: $PYTHON_VERSION (>=3.11)"
else
    echo "❌ 检测到 Python 版本为 $PYTHON_VERSION，建议使用 Python 3.11 及以上版本！"
    echo "   请升级本地 Python 以获得最佳兼容性。"
fi

# 创建动态启动脚本
create_startup_script() {
    local temp_script="/tmp/start_beesyncclip_${PORT}.py"
    
    if [ "$USE_MODULAR" = true ]; then
        # 模块化服务器启动脚本
        cat > "$temp_script" << EOF
#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = "/home/work/software"
sys.path.insert(0, project_root)

# 导入模块化服务器应用
from server.modular_server import app

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动BeeSyncClip模块化服务器 v2.0 (端口$PORT)...")
    print("🔐 AES-256加密 + JWT认证已启用")
    print("✅ Redis连接正常")
    port = $PORT
    if port == 80:
        print("🌐 访问地址: http://47.110.154.99")
        print("📖 API文档: http://47.110.154.99/docs")
    else:
        print(f"🌐 访问地址: http://47.110.154.99:{port}")
        print(f"📖 API文档: http://47.110.154.99:{port}/docs")
    print("📱 新用户请在客户端界面进行注册")
    print("🔐 所有数据传输均已加密")
    print("🎯 Ready for production!")
    
    uvicorn.run(
        app,
        host="$DEFAULT_HOST",
        port=$PORT,
        log_level="info"
    )
EOF
    else
        # 原始服务器启动脚本
        cat > "$temp_script" << EOF
#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = "/home/work/software"
sys.path.insert(0, project_root)

# 导入原始服务器应用
from server.frontend_compatible_server import app

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动BeeSyncClip原始服务器 v1.0 (端口$PORT)...")
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
    fi
    
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
    
    if [ "$USE_MODULAR" = true ]; then
        # 启动模块化服务器
        # 创建并使用动态启动脚本
        STARTUP_SCRIPT=$(create_startup_script)
        $PYTHON_CMD "$STARTUP_SCRIPT"
        # 清理临时脚本
        rm -f "$STARTUP_SCRIPT"
    else
        # 启动原始服务器
        # 创建并使用动态启动脚本
        STARTUP_SCRIPT=$(create_startup_script)
        $PYTHON_CMD "$STARTUP_SCRIPT"
        # 清理临时脚本
        rm -f "$STARTUP_SCRIPT"
    fi
fi 
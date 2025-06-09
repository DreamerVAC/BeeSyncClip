#!/bin/bash

# BeeSyncClip 模块化服务器快捷启动脚本
# 这是推荐的服务器版本

echo "🔥 BeeSyncClip 模块化服务器快捷启动"
echo "===================================="
echo "🚀 启动企业级安全的模块化服务器..."
echo "✅ AES-256加密 + JWT认证"
echo "✅ 性能优化 + 批量查询"
echo "✅ 100%向后兼容"
echo ""

# 解析参数
DAEMON_MODE=false
PORT=8000

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--daemon)
            DAEMON_MODE=true
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
        -h|--help)
            echo "用法: $0 [选项]"
            echo "选项:"
            echo "  -d, --daemon    后台模式启动"
            echo "  -p, --port      指定端口 (默认: 8000)"
            echo "  -h, --help      显示帮助信息"
            echo ""
            echo "示例:"
            echo "  $0              # 前台启动模块化服务器"
            echo "  $0 -d           # 后台启动模块化服务器"
            echo "  $0 -p 3000      # 指定端口3000启动"
            exit 0
            ;;
        *)
            echo "❌ 未知选项: $1"
            echo "使用 $0 -h 查看帮助"
            exit 1
            ;;
    esac
done

# 构建启动命令
if [ "$DAEMON_MODE" = true ]; then
    if [ "$PORT" -eq 8000 ]; then
        ./start_server.sh -m -d
    else
        ./start_server.sh -m -d -p "$PORT"
    fi
else
    if [ "$PORT" -eq 8000 ]; then
        ./start_server.sh -m
    else
        ./start_server.sh -m -p "$PORT"
    fi
fi 
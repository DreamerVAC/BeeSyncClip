#!/bin/bash

# BeeSyncClip 服务器状态查看脚本

PID_FILE="beesyncclip.pid"
LOG_FILE="beesyncclip.log"

echo "📊 BeeSyncClip 服务器状态"
echo "=========================="

# 检查Redis状态
echo "🔍 Redis 状态:"
if redis-cli ping > /dev/null 2>&1; then
    echo "  ✅ Redis 运行正常"
    echo "  📍 Redis 版本: $(redis-cli --version | cut -d' ' -f2)"
else
    echo "  ❌ Redis 未运行或连接失败"
fi

echo ""

# 检查服务器进程状态
echo "🌐 BeeSyncClip 服务器状态:"

# 检测服务器类型
detect_server_type() {
    # 检查模块化服务器
    if pgrep -f "modular_server" > /dev/null; then
        echo "modular"
    elif pgrep -f "modular_server" > /dev/null; then
        echo "modular"
    # 检查原始服务器
    elif pgrep -f "start_frontend_server.py" > /dev/null; then
        echo "original"
    elif pgrep -f "frontend_compatible_server" > /dev/null; then
        echo "original"
    else
        echo "unknown"
    fi
}

SERVER_TYPE=$(detect_server_type)

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "  ✅ 服务器运行中 (PID: $PID)"
        
        # 显示服务器版本
        case $SERVER_TYPE in
            "modular")
                echo "  🔥 服务器版本: 模块化服务器 v2.0"
                echo "     ✅ AES-256加密 + JWT认证"
                echo "     ✅ 性能优化 + 批量查询"
                ;;
            "original")
                echo "  📦 服务器版本: 原始服务器 v1.0"
                ;;
            *)
                echo "  ❓ 服务器版本: 未知"
                ;;
        esac
        
        # 获取进程信息
        PROCESS_INFO=$(ps -p "$PID" -o pid,ppid,pcpu,pmem,etime,cmd --no-headers)
        echo "  📋 进程信息: $PROCESS_INFO"
        
        # 检查端口
        if netstat -tuln | grep :8000 > /dev/null 2>&1; then
            echo "  🔗 端口 8000 正在监听"
        else
            echo "  ⚠️  端口 8000 未监听"
        fi
        
        # 测试API连通性
        echo "  🧪 API 测试:"
        
        # 先测试健康检查接口
        if curl -s -m 5 http://localhost:8000/health > /dev/null 2>&1; then
            echo "    ✅ 健康检查正常"
            
            # 根据服务器类型测试不同的接口
            if [ "$SERVER_TYPE" = "modular" ]; then
                # 测试模块化服务器的安全信息接口
                if curl -s -m 5 http://localhost:8000/security/info | grep -q "encryption"; then
                    echo "    ✅ 安全模块正常"
                fi
            fi
        else
            echo "    ⚠️  API 响应异常"
        fi
        
    else
        echo "  ❌ PID 文件存在但进程未运行 (陈旧的PID: $PID)"
        echo "  🧹 建议运行: rm -f $PID_FILE"
    fi
else
    echo "  ❌ 服务器未运行 (无PID文件)"
fi

echo ""

# 显示系统资源使用情况
echo "💻 系统资源:"
echo "  📊 内存使用:"
free -h | grep "Mem:" | awk '{print "    总计: " $2 ", 已用: " $3 ", 可用: " $7}'

echo "  💾 磁盘使用:"
df -h / | tail -1 | awk '{print "    总计: " $2 ", 已用: " $3 ", 可用: " $4 " (" $5 " 已使用)"}'

echo ""

# 显示网络连接
echo "🌍 网络连接:"
if netstat -tuln | grep :8000 > /dev/null 2>&1; then
    CONNECTIONS=$(netstat -tn | grep :8000 | wc -l)
    echo "  🔗 活跃连接数: $CONNECTIONS"
else
    echo "  ❌ 无网络监听"
fi

echo ""

# 显示最近的日志
echo "📄 最近日志 (最后10行):"
if [ -f "$LOG_FILE" ]; then
    echo "  📁 日志文件: $LOG_FILE"
    echo "  📝 文件大小: $(du -h "$LOG_FILE" | cut -f1)"
    echo "  ⏰ 最后修改: $(stat -c %y "$LOG_FILE")"
    echo ""
    echo "  🔍 最近日志内容:"
    tail -10 "$LOG_FILE" | sed 's/^/    /'
else
    echo "  ❌ 日志文件不存在"
fi

echo ""
echo "📋 管理命令:"
echo "  启动模块化服务器: ./start_server.sh -m -d"
echo "  启动原始服务器:   ./start_server.sh -o -d"
echo "  停止服务:         ./stop_server.sh" 
echo "  查看日志:         tail -f $LOG_FILE"
echo "  重启服务:         ./stop_server.sh && ./start_server.sh -m -d"
echo ""
echo "💡 推荐使用模块化服务器 (-m)，性能更好，安全性更强！" 
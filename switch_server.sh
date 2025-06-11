#!/bin/bash

# BeeSyncClip 服务器切换脚本
# 方便在模块化服务器和原始服务器之间切换

show_usage() {
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -m, --modular     切换到模块化服务器 v2.0 (推荐)"
    echo "  -o, --original    切换到原始服务器 v1.0"
    echo "  -s, --status      显示当前服务器状态"
    echo "  -h, --help        显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -m             # 切换到模块化服务器"
    echo "  $0 -o             # 切换到原始服务器"
    echo "  $0 -s             # 查看当前状态"
    echo ""
    echo "服务器对比:"
    echo "  🔥 模块化服务器 v2.0 (推荐):"
    echo "     ✅ AES-256加密 + JWT认证"
    echo "     ✅ 性能优化，提升20%"
    echo "     ✅ 解决多设备同步卡顿"
    echo "     ✅ 100%向后兼容"
    echo ""
    echo "  📦 原始服务器 v1.0:"
    echo "     ✅ 稳定可靠"
    echo "     ✅ 轻量级"
    echo "     ⚠️  基础功能"
}

detect_current_server() {
    if pgrep -f "modular_server" > /dev/null; then
        echo "modular"
    elif pgrep -f "start_frontend_server.py" > /dev/null || pgrep -f "frontend_compatible_server" > /dev/null; then
        echo "original"
    else
        echo "none"
    fi
}

show_status() {
    echo "📊 当前服务器状态"
    echo "=================="
    
    current=$(detect_current_server)
    
    case $current in
        "modular")
            echo "🔥 当前运行: 模块化服务器 v2.0"
            echo "   ✅ AES-256加密 + JWT认证"
            echo "   ✅ 性能优化 + 批量查询"
            echo "   ✅ 企业级安全功能"
            ;;
        "original")
            echo "📦 当前运行: 原始服务器 v1.0"
            echo "   ✅ 基础功能稳定"
            echo "   ⚠️  无高级安全功能"
            ;;
        "none")
            echo "❌ 没有检测到运行中的服务器"
            echo "💡 使用以下命令启动服务器:"
            echo "   模块化服务器: $0 -m"
            echo "   原始服务器:   $0 -o"
            return
            ;;
    esac
    
    # 显示详细状态
    ./status.sh
}

switch_to_modular() {
    echo "🔥 切换到模块化服务器 v2.0"
    echo "=========================="
    
    current=$(detect_current_server)
    
    if [ "$current" = "modular" ]; then
        echo "✅ 模块化服务器已在运行"
        return
    fi
    
    if [ "$current" != "none" ]; then
        echo "🛑 停止当前服务器..."
        ./stop_server.sh
        sleep 2
    fi
    
    echo "🚀 启动模块化服务器..."
    ./start_server.sh -m -d
    
    if [ $? -eq 0 ]; then
        echo "✅ 成功切换到模块化服务器 v2.0"
        echo "🔐 AES-256加密 + JWT认证已启用"
        echo "⚡ 性能优化已生效"
        echo "🌐 服务器地址: http://47.110.154.99:8000"
        echo "📖 API文档: http://47.110.154.99:8000/docs"
    else
        echo "❌ 切换失败，请检查错误信息"
    fi
}

switch_to_original() {
    echo "📦 切换到原始服务器 v1.0"
    echo "======================="
    
    current=$(detect_current_server)
    
    if [ "$current" = "original" ]; then
        echo "✅ 原始服务器已在运行"
        return
    fi
    
    if [ "$current" != "none" ]; then
        echo "🛑 停止当前服务器..."
        ./stop_server.sh
        sleep 2
    fi
    
    echo "🚀 启动原始服务器..."
    ./start_server.sh -o -d
    
    if [ $? -eq 0 ]; then
        echo "✅ 成功切换到原始服务器 v1.0"
        echo "📦 基础功能已就绪"
        echo "🌐 服务器地址: http://47.110.154.99:8000"
    else
        echo "❌ 切换失败，请检查错误信息"
    fi
}

# 解析命令行参数
case "${1:-}" in
    -m|--modular)
        switch_to_modular
        ;;
    -o|--original)
        switch_to_original
        ;;
    -s|--status)
        show_status
        ;;
    -h|--help)
        show_usage
        ;;
    "")
        echo "❌ 请指定操作选项"
        echo ""
        show_usage
        exit 1
        ;;
    *)
        echo "❌ 未知选项: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac 
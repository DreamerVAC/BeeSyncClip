#!/bin/bash

# BeeSyncClip GUI 客户端启动脚本 (PyQt5版本)

echo "🚀 BeeSyncClip GUI 客户端启动器"
echo "================================"

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

# 启动GUI客户端
echo "🎨 启动GUI客户端..."
echo ""
echo "📱 使用说明:"
echo "   • 新用户请在界面中注册账号"
echo "   • 默认连接服务器: http://47.110.154.99:8000"
echo "   • 支持实时剪贴板同步"
echo ""

# 启动PyQt5客户端
python3 client/ui/form_ui.py

echo "👋 GUI客户端已关闭" 
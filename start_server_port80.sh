#!/bin/bash
# BeeSyncClip 服务器启动脚本 - 80端口版本
# 用于直接外部访问，避免阿里云安全组配置

echo "🚀 启动 BeeSyncClip 服务器 (端口80)..."
echo "⚠️  需要sudo权限启动80端口服务"

# 检查是否有root权限
if [[ $EUID -ne 0 ]]; then
   echo "❌ 此脚本需要sudo权限运行80端口服务"
   echo "💡 请使用: sudo ./start_server_port80.sh"
   exit 1
fi

# 设置Python环境
PYTHON_PATH="/home/work/miniconda3/envs/software/bin/python3"

# 检查Python环境
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Python环境未找到: $PYTHON_PATH"
    echo "💡 请检查conda环境是否正确"
    exit 1
fi

# 检查Redis连接
echo "🔍 检查Redis连接..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis 连接正常"
else
    echo "❌ Redis 连接失败，请先启动Redis服务"
    exit 1
fi

# 停止现有进程
echo "🔄 停止现有进程..."
if [ -f beesyncclip.pid ]; then
    PID=$(cat beesyncclip.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "停止进程 $PID"
        kill $PID
        sleep 2
    fi
fi

# 检查80端口是否被占用
if netstat -tuln | grep ":80 " > /dev/null; then
    echo "⚠️  端口80已被占用，请检查其他Web服务"
    echo "占用端口80的进程:"
    netstat -tuln | grep ":80 "
    echo ""
    echo "💡 如果确定要继续，请先停止占用80端口的服务"
    read -p "是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 创建启动脚本
cat > /tmp/start_beesyncclip_80.py << 'EOF'
#!/usr/bin/env python3
import uvicorn
import sys
import os

# 添加项目路径
project_root = "/home/work/software"
sys.path.insert(0, project_root)

# 导入服务器应用
from server.frontend_compatible_server import app

if __name__ == "__main__":
    print("🚀 启动BeeSyncClip服务器 (端口80)...")
    print("✅ Redis连接正常")
    print("🌐 访问地址: http://47.110.154.99")
    print("📱 测试账号: testuser / test123")
    print("🎯 Ready for production!")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=80,
        log_level="info"
    )
EOF

# 设置权限
chmod +x /tmp/start_beesyncclip_80.py

# 启动服务器
echo "🌐 启动服务器在端口 80..."
echo "📱 测试账号: testuser / test123"
echo "🔗 服务器地址: http://47.110.154.99"
echo "📄 日志将直接输出到终端"
echo ""

# 使用conda环境的Python启动服务器
$PYTHON_PATH /tmp/start_beesyncclip_80.py 
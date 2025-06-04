#!/bin/bash

# BeeSyncClip 快速上传脚本
# 将项目代码上传到阿里云服务器

SERVER_IP="47.110.154.99"
USERNAME="ubuntu"
TARGET_DIR="~/BeeSyncClip"

echo "🚀 BeeSyncClip 快速上传脚本"
echo "📡 目标服务器: $USERNAME@$SERVER_IP"
echo "📁 目标目录: $TARGET_DIR"
echo "-" * 50

# 排除不需要上传的文件
EXCLUDE_LIST=(
    "--exclude=.git"
    "--exclude=__pycache__"
    "--exclude=*.pyc"
    "--exclude=.vscode"
    "--exclude=logs/*"
    "--exclude=venv"
    "--exclude=.DS_Store"
    "--exclude=*.log"
)

echo "📦 开始上传项目文件..."

# 使用rsync上传，支持增量同步
rsync -avz --progress \
    "${EXCLUDE_LIST[@]}" \
    . \
    $USERNAME@$SERVER_IP:$TARGET_DIR/

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 上传完成！"
    echo ""
    echo "🔄 接下来的步骤:"
    echo "1. SSH连接到服务器: ssh $USERNAME@$SERVER_IP"
    echo "2. 进入项目目录: cd $TARGET_DIR"
    echo "3. 安装依赖: pip install -r requirements.txt"
    echo "4. 启动服务器: python start_frontend_server.py"
    echo ""
    echo "📖 详细部署指南请查看: DEPLOYMENT_GUIDE.md"
else
    echo ""
    echo "❌ 上传失败！"
    echo "请检查网络连接和服务器信息。"
    exit 1
fi 
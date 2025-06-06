#!/bin/bash

# BeeSyncClip 项目清理脚本
echo "🧹 清理 BeeSyncClip 项目..."

# 1. 删除 Python 缓存文件
echo "🗑️  正在删除 Python 缓存文件 (__pycache__, *.pyc)..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 2. 删除日志文件
echo "🗑️  正在删除日志文件 (*.log)..."
find . -type f -name "*.log" -delete

# 3. 删除PID文件
echo "🗑️  正在删除PID文件 (*.pid)..."
find . -type f -name "*.pid" -delete

# 4. 删除测试和覆盖率报告
echo "🗑️  正在删除测试和覆盖率文件..."
rm -rf .coverage htmlcov/ .pytest_cache/

# 5. 删除其他临时文件 (如果存在)
echo "🗑️  正在删除其他临时文件..."
# 在这里添加其他需要清理的文件或目录

echo "✅ 清理完成！" 
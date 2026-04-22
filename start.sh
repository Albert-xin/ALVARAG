#!/bin/bash

# 启动脚本

echo "Starting RAG Backend Service..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# 检查依赖
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found"
    exit 1
fi

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt

# 创建必要的目录
echo "Creating necessary directories..."
mkdir -p logs temp models knowledge_base

# 启动服务
echo "Starting API server..."
python -m backend_api.main

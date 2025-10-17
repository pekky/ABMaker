#!/bin/bash

# NVIDIA P100 优化启动脚本

cd /Users/laibinqiang/Documents/projects/ttlnovel

# P100 优化设置
export SUNO_USE_SMALL_MODELS=True
export SUNO_OFFLOAD_CPU=True

# 可选：设置代理（如果需要）
# export https_proxy=http://127.0.0.1:7890
# export http_proxy=http://127.0.0.1:7890
# export all_proxy=socks5://127.0.0.1:7890
# export no_proxy=localhost,127.0.0.1,0.0.0.0

echo "======================================"
echo "PDF小说转有声读物工具（P100优化版）"
echo "======================================"
echo ""
echo "GPU优化设置："
echo "  SUNO_USE_SMALL_MODELS: $SUNO_USE_SMALL_MODELS"
echo "  SUNO_OFFLOAD_CPU: $SUNO_OFFLOAD_CPU"
echo ""
echo "正在启动Web界面..."
echo "启动成功后，请在浏览器访问: http://localhost:7860"
echo ""

# 启动应用
./venv/bin/python app.py

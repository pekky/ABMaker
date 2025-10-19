#!/bin/bash

# Web服务器启动脚本

echo "======================================"
echo "PDF转有声读物 Web服务器"
echo "======================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3"
    exit 1
fi

# 激活conda环境
echo "激活conda环境..."
source /home/alai/miniconda3/bin/activate abmaker310

# 检查Flask是否安装
if ! python -c "import flask" &> /dev/null; then
    echo "正在安装Flask..."
    pip install flask
fi

# 创建必要的目录
mkdir -p uploads
mkdir -p generated_audio
mkdir -p templates

echo "✓ 环境准备完成"
echo ""

# 启动Web服务器
echo "正在启动Web服务器..."
echo "访问地址: http://localhost:5000"
echo "外部访问: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "功能特点:"
echo "  - 拖拽上传PDF文件"
echo "  - 实时转换进度显示"
echo "  - 每5分钟生成一个音频文件"
echo "  - 在线试听和下载"
echo "  - 支持多种语音预设"
echo ""

python web_server.py

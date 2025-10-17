#!/bin/bash

# PDF小说转有声读物 - Web界面启动脚本

echo "======================================"
echo "PDF小说转有声读物工具"
echo "======================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

echo "Python版本:"
python3 --version
echo ""

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "错误: 虚拟环境创建失败"
        exit 1
    fi
    echo "✓ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 检查并安装依赖
echo "检查依赖..."
if ! python -c "import gradio" &> /dev/null; then
    echo "正在安装依赖（这可能需要几分钟）..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 依赖安装失败"
        exit 1
    fi
fi

echo "✓ 依赖检查完成"
echo ""

# 启动Web界面
echo "正在启动Web界面..."
echo "请稍候，首次运行需要下载模型文件..."
echo "启动成功后，请在浏览器访问: http://localhost:7860"
echo ""

python app.py


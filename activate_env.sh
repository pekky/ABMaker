#!/bin/bash
# -*- coding: utf-8 -*-
"""
ABMaker 环境激活脚本
快速激活 abmaker310 环境
"""

echo "🚀 激活 ABMaker 环境..."

# 重新加载 bashrc 以确保 conda 可用
source ~/.bashrc

# 激活环境
conda activate abmaker310

echo "✅ 环境已激活：abmaker310"
echo ""
echo "💡 使用方法："
echo "  python3 optimized_audiobook_maker.py docs/RiverTown.pdf --batch-mode"
echo ""
echo "📦 批量处理模式："
echo "  python3 optimized_audiobook_maker.py docs/RiverTown.pdf --batch-mode --batch-size 15000"
echo ""

# 启动新的 bash 会话，保持环境激活
exec bash




#!/bin/bash

# 带代理的启动脚本

cd /Users/laibinqiang/Documents/projects/ttlnovel

# 设置代理
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
export all_proxy=socks5://127.0.0.1:7890

# 重要：排除localhost和127.0.0.1，避免影响Gradio
export no_proxy=localhost,127.0.0.1,0.0.0.0
export NO_PROXY=localhost,127.0.0.1,0.0.0.0

echo "======================================"
echo "PDF小说转有声读物工具（带代理）"
echo "======================================"
echo ""
echo "代理设置："
echo "  http_proxy:  $http_proxy"
echo "  https_proxy: $https_proxy"
echo "  all_proxy:   $all_proxy"
echo "  no_proxy:    $no_proxy"
echo ""
echo "正在启动Web界面..."
echo "启动成功后，请在浏览器访问: http://localhost:7860"
echo ""

# 启动应用
./venv/bin/python app.py



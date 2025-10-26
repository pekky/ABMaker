#!/bin/bash
# ABMaker 环境准备脚本
# 自动安装 miniconda，创建和配置 abmaker310 环境

set -e  # 遇到错误立即退出

echo "🚀 ABMaker 环境准备脚本"
echo "============================================================"
echo "📢 注意：ABMaker 默认使用英语男声 (v2/en_speaker_0)"
echo "   如需使用其他语言，请使用 --voice 参数指定"
echo "============================================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 conda 是否已安装
check_conda() {
    if command -v conda &> /dev/null; then
        print_success "conda 已安装"
        return 0
    else
        print_warning "conda 未安装，开始安装 miniconda..."
        return 1
    fi
}

# 安装 miniconda
install_miniconda() {
    print_info "正在下载 miniconda..."
    
    # 创建临时目录
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # 下载 miniconda 安装包
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    MINICONDA_INSTALLER="Miniconda3-latest-Linux-x86_64.sh"
    
    if ! wget -q "$MINICONDA_URL" -O "$MINICONDA_INSTALLER"; then
        print_error "下载 miniconda 失败"
        exit 1
    fi
    
    print_info "正在安装 miniconda..."
    
    # 安装 miniconda
    bash "$MINICONDA_INSTALLER" -b -p "$HOME/miniconda3"
    
    # 初始化 conda
    "$HOME/miniconda3/bin/conda" init bash
    
    # 清理临时文件
    cd "$HOME"
    rm -rf "$TEMP_DIR"
    
    print_success "miniconda 安装完成"
}

# 检查 abmaker310 环境是否存在
check_environment() {
    if conda env list | grep -q "abmaker310"; then
        print_success "abmaker310 环境已存在"
        return 0
    else
        print_warning "abmaker310 环境不存在，开始创建..."
        return 1
    fi
}

# 创建 abmaker310 环境
create_environment() {
    print_info "正在创建 abmaker310 环境..."
    
    # 创建 Python 3.10 环境
    conda create -n abmaker310 python=3.10 -y
    
    print_success "abmaker310 环境创建完成"
}

# 激活环境并安装依赖
setup_environment() {
    print_info "正在激活 abmaker310 环境..."
    
    # 激活环境
    source ~/.bashrc
    conda activate abmaker310
    
    print_success "环境已激活"
    
    # 检查 requirements.txt 是否存在
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt 文件不存在"
        exit 1
    fi
    
    print_info "正在安装依赖包..."
    
    # 升级 pip
    pip install --upgrade pip
    
    # 使用conda安装pandas以避免编译问题
    print_info "使用conda安装pandas..."
    conda install pandas -y
    
    # 安装gradio时跳过pandas依赖检查
    print_info "安装gradio（跳过pandas依赖）..."
    pip install gradio>=3.0.0 --no-deps
    
    # 安装gradio的依赖（除了pandas）
    print_info "安装gradio依赖..."
    pip install fastapi uvicorn starlette pydantic jinja2 markupsafe pyyaml
    
    # 安装其他依赖
    print_info "安装其他依赖..."
    # pip install "git+https://github.com/suno-ai/bark.git" "pdfplumber>=0.6.0" "numpy>=1.16.0,<1.20.0" "scipy>=1.3.0,<1.7.0" "pydub>=0.25.1" "tqdm>=4.60.0" "nltk>=3.6.0" "soundfile>=0.13.0"
    
    print_success "依赖包安装完成"
}

# 验证环境
verify_environment() {
    print_info "正在验证环境..."
    
    # 检查 Python 版本
    python_version=$(python --version 2>&1)
    print_info "Python 版本: $python_version"
    
    # 检查关键包是否安装
    if python -c "import torch; print(f'PyTorch 版本: {torch.__version__}')" 2>/dev/null; then
        print_success "PyTorch 已安装"
    else
        print_warning "PyTorch 未安装或有问题"
    fi
    
    if python -c "import bark; print('Bark 已安装')" 2>/dev/null; then
        print_success "Bark 已安装"
    else
        print_warning "Bark 未安装或有问题"
    fi
}

# 主函数
main() {
    echo "开始环境准备..."
    
    # 检查并安装 conda
    if ! check_conda; then
        install_miniconda
        # 重新加载 bashrc
        source ~/.bashrc
    fi
    
    # 检查并创建环境
    if ! check_environment; then
        create_environment
    fi
    
    # 设置环境
    setup_environment
    
    # 验证环境
    verify_environment
    
    echo ""
    echo "============================================================"
    print_success "🎉 环境准备完成！"
    echo ""
    print_info "使用方法："
    echo "  source ~/.bashrc && conda activate abmaker310"
    echo ""
    print_info "运行 ABMaker（默认使用英语男声 v2/en_speaker_0）："
    echo "  source ~/.bashrc && conda activate abmaker310 && python3 optimized_audiobook_maker.py docs/RiverTown.pdf --batch-mode"
    echo ""
    print_info "或者使用批量处理模式："
    echo "  source ~/.bashrc && conda activate abmaker310 && python3 optimized_audiobook_maker.py docs/RiverTown.pdf --batch-mode --batch-size 15000"
    echo ""
    print_info "语音选择："
    echo "  --voice v2/en_speaker_0    # 英语男声（默认）"
    echo "  --voice v2/en_speaker_6    # 英语女声"
    echo "  --voice v2/zh_speaker_1    # 中文女声"
    echo "  --voice v2/ja_speaker_1    # 日文女声"
    echo ""
    echo "============================================================"
}

# 运行主函数
main "$@"


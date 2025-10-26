#!/bin/bash
# -*- coding: utf-8 -*-
"""
ABMaker 主启动脚本
自动检查环境、选择质量模式、后台运行并监控进展
"""

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

print_header() {
    echo -e "${CYAN}$1${NC}"
}

# 检查虚拟环境是否已启动
check_environment() {
    print_info "检查虚拟环境状态..."
    
    if [[ "$CONDA_DEFAULT_ENV" == "abmaker310" ]]; then
        print_success "虚拟环境已启动: $CONDA_DEFAULT_ENV"
        return 0
    elif command -v conda &> /dev/null; then
        print_warning "conda 已安装但环境未激活"
        return 1
    else
        print_warning "conda 未安装"
        return 2
    fi
}

# 设置虚拟环境
setup_environment() {
    print_info "设置虚拟环境..."
    
    if [[ ! -f "setup_environment.sh" ]]; then
        print_error "setup_environment.sh 文件不存在"
        exit 1
    fi
    
    print_info "运行环境准备脚本..."
    chmod +x setup_environment.sh
    ./setup_environment.sh
    
    if [[ $? -eq 0 ]]; then
        print_success "环境准备完成"
        source ~/.bashrc
        conda activate abmaker310
    else
        print_error "环境准备失败"
        exit 1
    fi
}

# 选择质量模式
select_quality_mode() {
    print_header "============================================================"
    print_header "🎵 ABMaker 质量模式选择"
    print_header "============================================================"
    echo ""
    echo "请选择音频质量模式："
    echo ""
    echo "1. 🚀 快速模式 (推荐)"
    echo "   • 使用小模型，转换速度快"
    echo "   • 适合快速预览和测试"
    echo "   • 质量: 中等"
    echo ""
    echo "2. 🎯 高质量模式"
    echo "   • 使用大模型，转换时间长"
    echo "   • 适合最终输出和高质量需求"
    echo "   • 质量: 高"
    echo ""
    
    while true; do
        read -p "请选择模式 (1-2，默认为1): " choice
        choice=${choice:-1}
        
        case $choice in
            1)
                QUALITY_MODE="fast"
                QUALITY_NAME="快速模式"
                print_success "已选择: $QUALITY_NAME"
                break
                ;;
            2)
                QUALITY_MODE="high"
                QUALITY_NAME="高质量模式"
                print_success "已选择: $QUALITY_NAME"
                break
                ;;
            *)
                print_error "无效选择，请输入 1 或 2"
                ;;
        esac
    done
}

# 选择PDF文件
select_pdf_file() {
    print_header "============================================================"
    print_header "📚 选择PDF文件"
    print_header "============================================================"
    
    if [[ ! -d "docs" ]]; then
        print_error "docs 目录不存在"
        exit 1
    fi
    
    # 列出可用的PDF文件
    pdf_files=($(find docs -name "*.pdf" -type f))
    
    if [[ ${#pdf_files[@]} -eq 0 ]]; then
        print_error "docs 目录中没有找到PDF文件"
        exit 1
    fi
    
    echo "可用的PDF文件："
    for i in "${!pdf_files[@]}"; do
        echo "$((i+1)). $(basename "${pdf_files[$i]}")"
    done
    echo ""
    
    while true; do
        read -p "请选择PDF文件 (1-${#pdf_files[@]}): " choice
        if [[ "$choice" =~ ^[0-9]+$ ]] && [[ "$choice" -ge 1 ]] && [[ "$choice" -le ${#pdf_files[@]} ]]; then
            PDF_FILE="${pdf_files[$((choice-1))]}"
            print_success "已选择: $(basename "$PDF_FILE")"
            break
        else
            print_error "无效选择，请输入 1-${#pdf_files[@]} 之间的数字"
        fi
    done
}

# 生成输出文件名
generate_output_filename() {
    local pdf_basename=$(basename "$PDF_FILE" .pdf)
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local quality_suffix=""
    
    if [[ "$QUALITY_MODE" == "fast" ]]; then
        quality_suffix="_fast"
    else
        quality_suffix="_high"
    fi
    
    OUTPUT_FILE="output/${pdf_basename}${quality_suffix}_${timestamp}.wav"
    LOG_FILE="logs/${pdf_basename}${quality_suffix}_${timestamp}.log"
    
    # 创建输出目录
    mkdir -p output logs
}

# 运行音频转换
run_audiobook_conversion() {
    print_header "============================================================"
    print_header "🚀 启动音频转换"
    print_header "============================================================"
    
    # 生成输出文件名
    generate_output_filename
    
    print_info "输出文件: $OUTPUT_FILE"
    print_info "日志文件: $LOG_FILE"
    print_info "质量模式: $QUALITY_NAME"
    
    # 构建命令
    local cmd=""
    
    if [[ "$QUALITY_MODE" == "fast" ]]; then
        # 快速模式：使用小模型
        cmd="python3 optimized_audiobook_maker.py \"$PDF_FILE\" --output \"$OUTPUT_FILE\" --batch-mode --batch-size 15000 --small-model --keep-chunks"
    else
        # 高质量模式：使用大模型
        cmd="python3 optimized_audiobook_maker.py \"$PDF_FILE\" --output \"$OUTPUT_FILE\" --batch-mode --batch-size 15000 --keep-chunks"
    fi
    
    print_info "执行命令: $cmd"
    
    # 后台运行
    print_info "在后台启动音频转换..."
    nohup bash -c "$cmd" > "$LOG_FILE" 2>&1 &
    
    # 保存进程ID
    local pid=$!
    echo "$pid" > "conversion.pid"
    
    print_success "音频转换已启动 (PID: $pid)"
    print_info "日志文件: $LOG_FILE"
    
    # 等待一下确保进程启动
    sleep 2
    
    # 检查进程是否还在运行
    if kill -0 "$pid" 2>/dev/null; then
        print_success "进程运行正常"
    else
        print_error "进程启动失败，请检查日志文件"
        return 1
    fi
}

# 启动监控脚本
start_monitoring() {
    print_header "============================================================"
    print_header "📊 启动进展监控"
    print_header "============================================================"
    
    # 创建监控脚本
    create_monitor_script
    
    print_info "启动监控脚本..."
    chmod +x monitor.sh
    ./monitor.sh &
    
    local monitor_pid=$!
    echo "$monitor_pid" > "monitor.pid"
    
    print_success "监控已启动 (PID: $monitor_pid)"
    print_info "监控脚本: monitor.sh"
}

# 创建监控脚本
create_monitor_script() {
    cat > monitor.sh << 'EOF'
#!/bin/bash
# 进展监控脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

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

print_header() {
    echo -e "${CYAN}$1${NC}"
}

# 检查转换进程
check_conversion_process() {
    if [[ -f "conversion.pid" ]]; then
        local pid=$(cat conversion.pid)
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}

# 显示进展信息
show_progress() {
    print_header "============================================================"
    print_header "📊 ABMaker 转换进展监控"
    print_header "============================================================"
    
    while check_conversion_process; do
        clear
        print_header "📊 ABMaker 转换进展监控 - $(date)"
        print_header "============================================================"
        
        # 显示进程信息
        local pid=$(cat conversion.pid)
        print_info "转换进程PID: $pid"
        
        # 显示CPU和内存使用情况
        print_info "系统资源使用情况:"
        ps -p "$pid" -o pid,ppid,cmd,etime,pcpu,pmem --no-headers 2>/dev/null || print_warning "无法获取进程信息"
        
        # 显示日志文件大小
        if [[ -f "$LOG_FILE" ]]; then
            local log_size=$(du -h "$LOG_FILE" | cut -f1)
            print_info "日志文件大小: $log_size"
            
            # 显示最新的日志内容
            print_info "最新日志内容:"
            tail -10 "$LOG_FILE" 2>/dev/null || print_warning "无法读取日志文件"
        fi
        
        # 检查输出文件
        if [[ -f "$OUTPUT_FILE" ]]; then
            local output_size=$(du -h "$OUTPUT_FILE" | cut -f1)
            print_success "输出文件已生成: $OUTPUT_FILE ($output_size)"
        else
            print_info "输出文件尚未生成..."
        fi
        
        # 检查临时文件
        if [[ -d "tmp" ]]; then
            local temp_count=$(find tmp -name "*.wav" 2>/dev/null | wc -l)
            print_info "临时音频文件数量: $temp_count"
        fi
        
        print_header "============================================================"
        print_info "按 Ctrl+C 退出监控"
        
        sleep 10
    done
    
    print_success "转换进程已结束"
    
    # 显示最终结果
    if [[ -f "$OUTPUT_FILE" ]]; then
        local output_size=$(du -h "$OUTPUT_FILE" | cut -f1)
        print_success "🎉 转换完成！"
        print_success "输出文件: $OUTPUT_FILE ($output_size)"
    else
        print_error "转换失败，请检查日志文件"
    fi
}

# 主函数
main() {
    # 获取日志文件路径
    LOG_FILE=$(find logs -name "*.log" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
    OUTPUT_FILE=$(find output -name "*.wav" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
    
    if [[ -z "$LOG_FILE" ]]; then
        print_error "未找到日志文件"
        exit 1
    fi
    
    show_progress
}

# 捕获中断信号
trap 'print_info "监控已停止"; exit 0' INT

# 运行主函数
main "$@"
EOF
}

# 显示使用说明
show_usage() {
    print_header "============================================================"
    print_header "🎵 ABMaker 音频转换工具"
    print_header "============================================================"
    echo ""
    print_info "功能特性:"
    echo "  • 自动环境检查和设置"
    echo "  • 质量模式选择（快速/高质量）"
    echo "  • 批量处理（每15000个token一个batch）"
    echo "  • 后台运行和进展监控"
    echo "  • 详细的日志记录"
    echo ""
    print_info "输出文件:"
    echo "  • 音频文件: output/ 目录"
    echo "  • 日志文件: logs/ 目录"
    echo "  • 临时文件: tmp/ 目录"
    echo ""
}

# 主函数
main() {
    show_usage
    
    # 1. 检查虚拟环境
    check_environment
    case $? in
        0)
            print_success "环境已准备就绪"
            ;;
        1|2)
            print_info "需要设置环境..."
            setup_environment
            ;;
    esac
    
    # 2. 选择质量模式
    select_quality_mode
    
    # 3. 选择PDF文件
    select_pdf_file
    
    # 4. 运行音频转换
    run_audiobook_conversion
    
    # 5. 启动监控
    start_monitoring
    
    print_header "============================================================"
    print_success "🎉 ABMaker 已启动！"
    print_header "============================================================"
    echo ""
    print_info "转换状态:"
    echo "  • 进程ID: $(cat conversion.pid)"
    echo "  • 监控PID: $(cat monitor.pid)"
    echo "  • 日志文件: $LOG_FILE"
    echo "  • 输出文件: $OUTPUT_FILE"
    echo ""
    print_info "监控命令:"
    echo "  • 查看实时进展: tail -f $LOG_FILE"
    echo "  • 停止转换: kill \$(cat conversion.pid)"
    echo "  • 停止监控: kill \$(cat monitor.pid)"
    echo ""
    print_info "按 Ctrl+C 退出监控，转换将继续在后台运行"
    echo ""
    
    # 等待用户中断
    trap 'print_info "监控已停止，转换继续在后台运行"; exit 0' INT
    while true; do
        sleep 1
    done
}

# 运行主函数
main "$@"

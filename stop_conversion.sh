#!/bin/bash
# -*- coding: utf-8 -*-
"""
ABMaker 停止转换脚本
停止音频转换和监控进程
"""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# 停止转换进程
stop_conversion() {
    if [[ -f "conversion.pid" ]]; then
        local pid=$(cat conversion.pid)
        if kill -0 "$pid" 2>/dev/null; then
            print_info "停止转换进程 (PID: $pid)..."
            kill "$pid"
            sleep 2
            
            # 检查进程是否已停止
            if kill -0 "$pid" 2>/dev/null; then
                print_warning "进程未响应，强制终止..."
                kill -9 "$pid"
            fi
            
            print_success "转换进程已停止"
        else
            print_warning "转换进程已停止"
        fi
        rm -f conversion.pid
    else
        print_warning "未找到转换进程PID文件"
    fi
}

# 停止监控进程
stop_monitoring() {
    if [[ -f "monitor.pid" ]]; then
        local pid=$(cat monitor.pid)
        if kill -0 "$pid" 2>/dev/null; then
            print_info "停止监控进程 (PID: $pid)..."
            kill "$pid"
            print_success "监控进程已停止"
        else
            print_warning "监控进程已停止"
        fi
        rm -f monitor.pid
    else
        print_warning "未找到监控进程PID文件"
    fi
}

# 清理临时文件
cleanup_temp_files() {
    print_info "清理临时文件..."
    
    if [[ -d "tmp" ]]; then
        local temp_count=$(find tmp -name "*.wav" 2>/dev/null | wc -l)
        if [[ "$temp_count" -gt 0 ]]; then
            print_info "删除 $temp_count 个临时音频文件..."
            find tmp -name "*.wav" -delete 2>/dev/null
        fi
    fi
    
    print_success "临时文件清理完成"
}

# 显示状态
show_status() {
    print_info "当前状态:"
    
    # 检查转换进程
    if [[ -f "conversion.pid" ]]; then
        local pid=$(cat conversion.pid)
        if kill -0 "$pid" 2>/dev/null; then
            print_warning "转换进程仍在运行 (PID: $pid)"
        else
            print_success "转换进程已停止"
        fi
    else
        print_success "转换进程已停止"
    fi
    
    # 检查监控进程
    if [[ -f "monitor.pid" ]]; then
        local pid=$(cat monitor.pid)
        if kill -0 "$pid" 2>/dev/null; then
            print_warning "监控进程仍在运行 (PID: $pid)"
        else
            print_success "监控进程已停止"
        fi
    else
        print_success "监控进程已停止"
    fi
}

# 主函数
main() {
    echo "🛑 ABMaker 停止转换脚本"
    echo "============================================================"
    
    # 停止监控进程
    stop_monitoring
    
    # 停止转换进程
    stop_conversion
    
    # 显示状态
    show_status
    
    # 询问是否清理临时文件
    echo ""
    read -p "是否清理临时文件? (y/N): " cleanup_choice
    cleanup_choice=${cleanup_choice:-N}
    
    if [[ "$cleanup_choice" =~ ^[Yy]$ ]]; then
        cleanup_temp_files
    fi
    
    echo ""
    print_success "🎉 所有进程已停止"
    print_info "日志文件已保存在 logs/ 目录中"
    print_info "输出文件已保存在 output/ 目录中"
}

# 运行主函数
main "$@"




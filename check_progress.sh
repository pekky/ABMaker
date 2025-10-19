#!/bin/bash
# 快速检查转换进度脚本

echo "🔍 检查转换进度..."
echo "=================="

# 获取转换进程信息
get_process_info() {
    local pid=$(ps aux | grep -E "(fast_optimized_audiobook_maker|fixed_token_batch_audiobook_maker|token_batch_audiobook_maker)" | grep -v grep | awk '{print $2}' | head -1)
    
    if [ -z "$pid" ]; then
        echo "❌ 未找到转换进程"
        return 1
    fi
    
    local etime=$(ps -o etime= -p "$pid" 2>/dev/null | tr -d ' ')
    local cpu=$(ps -o %cpu= -p "$pid" 2>/dev/null | tr -d ' ')
    local mem=$(ps -o %mem= -p "$pid" 2>/dev/null | tr -d ' ')
    
    echo "✅ 转换进程运行中"
    echo "   PID: $pid"
    echo "   运行时间: $etime"
    echo "   CPU使用率: ${cpu}%"
    echo "   内存使用率: ${mem}%"
    
    return 0
}

# 检查输出目录和进度
check_output_progress() {
    local output_dirs=("fast_optimized_audio" "fixed_token_batch_audio_files" "token_batch_audio")
    local found_dir=""
    
    for dir in "${output_dirs[@]}"; do
        if [ -d "$dir" ]; then
            found_dir="$dir"
            break
        fi
    done
    
    if [ -z "$found_dir" ]; then
        echo "⏳ 等待输出目录创建..."
        return 0
    fi
    
    echo "📁 输出目录: $found_dir"
    
    # 检查批次进度
    local batch_dirs=($(ls -d "$found_dir"/batch_*_chunks 2>/dev/null | sort -V))
    local completed_batches=0
    local current_batch=0
    local current_progress=0
    local current_total=0
    
    # 检查已完成的批次
    for batch_dir in "${batch_dirs[@]}"; do
        if [ -d "$batch_dir" ]; then
            local batch_num=$(basename "$batch_dir" | grep -o 'batch_[0-9]*' | grep -o '[0-9]*')
            local audio_file="$found_dir/batch_$(printf "%03d" $batch_num).wav"
            
            if [ -f "$audio_file" ]; then
                completed_batches=$((completed_batches + 1))
                local file_size=$(ls -lh "$audio_file" 2>/dev/null | awk '{print $5}')
                echo "   ✅ 批次 $batch_num: 完成 ($file_size)"
            else
                current_batch=$batch_num
                current_progress=$(ls "$batch_dir" 2>/dev/null | wc -l)
                
                # 估算当前批次的总片段数
                case $batch_num in
                    1) current_total=744 ;;
                    2) current_total=740 ;;
                    3) current_total=700 ;;
                    4) current_total=700 ;;
                    5) current_total=700 ;;
                    6) current_total=300 ;;
                    *) current_total=700 ;;
                esac
                
                local progress_percent=0
                if [ "$current_total" -gt 0 ]; then
                    progress_percent=$((current_progress * 100 / current_total))
                fi
                
                echo "   🔄 批次 $batch_num: $current_progress/$current_total 片段 ($progress_percent%)"
                
                # 估算剩余时间
                if [ "$current_progress" -gt 0 ] && [ "$current_total" -gt 0 ]; then
                    local remaining_chunks=$((current_total - current_progress))
                    local remaining_time_seconds=$((remaining_chunks * 177 / 100))
                    local remaining_time_minutes=$((remaining_time_seconds / 60))
                    
                    if [ "$remaining_time_minutes" -gt 60 ]; then
                        local hours=$((remaining_time_minutes / 60))
                        local minutes=$((remaining_time_minutes % 60))
                        echo "   ⏱️  预计剩余时间: ${hours}小时${minutes}分钟"
                    else
                        echo "   ⏱️  预计剩余时间: ${remaining_time_minutes}分钟"
                    fi
                fi
                break
            fi
        fi
    done
    
    # 显示总进度
    local total_batches=6
    echo ""
    echo "📊 总进度: $completed_batches/$total_batches 批次完成"
    
    # 显示输出目录大小
    local total_size=$(du -sh "$found_dir" 2>/dev/null | cut -f1)
    echo "💾 输出目录大小: $total_size"
}

# 主函数
main() {
    echo "$(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    if get_process_info; then
        echo ""
        check_output_progress
    fi
    
    echo ""
    echo "💡 提示: 运行 './monitor_progress.sh' 可以持续监控进度"
}

main

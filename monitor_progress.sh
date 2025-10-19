#!/bin/bash
# 监控有声读物转换进度脚本

LOG_FILE="conversion_progress.log"
PID_FILE="conversion_pid.txt"

echo "🔍 开始监控转换进度..."
echo "日志文件: $LOG_FILE"
echo "按 Ctrl+C 停止监控"
echo ""

# 清空日志文件
> "$LOG_FILE"

# 获取转换进程PID
get_conversion_pid() {
    ps aux | grep -E "(fast_optimized_audiobook_maker|fixed_token_batch_audiobook_maker|token_batch_audiobook_maker)" | grep -v grep | awk '{print $2}' | head -1
}

# 监控函数
monitor_progress() {
    local pid=$(get_conversion_pid)
    
    if [ -z "$pid" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ❌ 未找到转换进程" | tee -a "$LOG_FILE"
        return 1
    fi
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ✅ 找到转换进程 PID: $pid" | tee -a "$LOG_FILE"
    echo "$pid" > "$PID_FILE"
    
    # 检查输出目录
    local output_dirs=("fast_optimized_audio" "fixed_token_batch_audio_files" "token_batch_audio")
    local found_dir=""
    
    for dir in "${output_dirs[@]}"; do
        if [ -d "$dir" ]; then
            found_dir="$dir"
            break
        fi
    done
    
    if [ -z "$found_dir" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ⏳ 等待输出目录创建..." | tee -a "$LOG_FILE"
        return 0
    fi
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 📁 输出目录: $found_dir" | tee -a "$LOG_FILE"
    
    # 检查批次进度
    local batch_dirs=($(ls -d "$found_dir"/batch_*_chunks 2>/dev/null | sort -V))
    local total_batches=0
    local completed_batches=0
    
    # 计算总批次数（从batch_info.json或估算）
    if [ -f "$found_dir/batch_info.json" ]; then
        total_batches=$(grep -o '"total_batches"' "$found_dir/batch_info.json" | wc -l)
        if [ "$total_batches" -eq 0 ]; then
            total_batches=$(grep -o '"total_batches": [0-9]*' "$found_dir/batch_info.json" | grep -o '[0-9]*')
        fi
    else
        # 估算批次数（基于文件结构）
        total_batches=$(ls -d "$found_dir"/batch_*_chunks 2>/dev/null | wc -l)
        if [ "$total_batches" -eq 0 ]; then
            total_batches=6  # 默认6批
        fi
    fi
    
    # 检查已完成的批次
    for batch_dir in "${batch_dirs[@]}"; do
        if [ -d "$batch_dir" ]; then
            local batch_num=$(basename "$batch_dir" | grep -o 'batch_[0-9]*' | grep -o '[0-9]*')
            local audio_file="$found_dir/batch_$(printf "%03d" $batch_num).wav"
            
            if [ -f "$audio_file" ]; then
                completed_batches=$((completed_batches + 1))
            fi
        fi
    done
    
    # 检查当前正在处理的批次
    local current_batch=0
    local current_progress=0
    local current_total=0
    
    for batch_dir in "${batch_dirs[@]}"; do
        if [ -d "$batch_dir" ]; then
            local batch_num=$(basename "$batch_dir" | grep -o 'batch_[0-9]*' | grep -o '[0-9]*')
            local audio_file="$found_dir/batch_$(printf "%03d" $batch_num).wav"
            
            if [ ! -f "$audio_file" ]; then
                current_batch=$batch_num
                current_progress=$(ls "$batch_dir" 2>/dev/null | wc -l)
                
                # 估算当前批次的总片段数
                if [ -f "$found_dir/batch_info.json" ]; then
                    current_total=$(grep -A 10 "\"batch_number\": $batch_num" "$found_dir/batch_info.json" | grep -o '"paragraph_count": [0-9]*' | grep -o '[0-9]*')
                fi
                
                if [ "$current_total" -eq 0 ]; then
                    # 基于批次大小估算
                    case $batch_num in
                        1) current_total=744 ;;
                        2) current_total=740 ;;
                        3) current_total=700 ;;
                        4) current_total=700 ;;
                        5) current_total=700 ;;
                        6) current_total=300 ;;
                        *) current_total=700 ;;
                    esac
                fi
                break
            fi
        fi
    done
    
    # 输出进度信息
    if [ "$current_batch" -gt 0 ]; then
        local progress_percent=0
        if [ "$current_total" -gt 0 ]; then
            progress_percent=$((current_progress * 100 / current_total))
        fi
        
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 📊 批次 $current_batch/$total_batches: $current_progress/$current_total 片段 ($progress_percent%)" | tee -a "$LOG_FILE"
        
        # 估算剩余时间
        if [ "$current_progress" -gt 0 ] && [ "$current_total" -gt 0 ]; then
            local remaining_chunks=$((current_total - current_progress))
            local remaining_batches=$((total_batches - completed_batches))
            
            # 基于1.77秒/片段的平均速度
            local remaining_time_seconds=$((remaining_chunks * 177 / 100))
            local remaining_time_minutes=$((remaining_time_seconds / 60))
            local remaining_time_hours=$((remaining_time_minutes / 60))
            
            if [ "$remaining_time_hours" -gt 0 ]; then
                echo "$(date '+%Y-%m-%d %H:%M:%S') - ⏱️  预计剩余时间: ${remaining_time_hours}小时${remaining_time_minutes}分钟" | tee -a "$LOG_FILE"
            else
                echo "$(date '+%Y-%m-%d %H:%M:%S') - ⏱️  预计剩余时间: ${remaining_time_minutes}分钟" | tee -a "$LOG_FILE"
            fi
        fi
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ✅ 所有批次已完成: $completed_batches/$total_batches" | tee -a "$LOG_FILE"
    fi
    
    # 显示文件大小信息
    local total_size=$(du -sh "$found_dir" 2>/dev/null | cut -f1)
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 💾 输出目录大小: $total_size" | tee -a "$LOG_FILE"
    
    return 0
}

# 主监控循环
main() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 🚀 开始监控转换进度" | tee -a "$LOG_FILE"
    
    while true; do
        if ! monitor_progress; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - ⚠️  转换进程未运行，等待中..." | tee -a "$LOG_FILE"
        fi
        
        sleep 30  # 每30秒检查一次
    done
}

# 捕获中断信号
trap 'echo "$(date "+%Y-%m-%d %H:%M:%S") - 🛑 监控已停止" | tee -a "$LOG_FILE"; exit 0' INT

# 启动监控
main

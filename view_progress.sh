#!/bin/bash
# 查看转换进度日志脚本

LOG_FILE="conversion_progress.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ 日志文件不存在: $LOG_FILE"
    echo "请先运行 './monitor_progress.sh' 开始监控"
    exit 1
fi

echo "📋 转换进度日志"
echo "==============="
echo ""

# 显示最新的进度信息
echo "🕐 最新进度:"
tail -10 "$LOG_FILE"
echo ""

# 显示进度统计
echo "📊 进度统计:"
echo "总日志行数: $(wc -l < "$LOG_FILE")"
echo "最后更新: $(tail -1 "$LOG_FILE" | cut -d' ' -f1-2)"
echo ""

# 显示关键进度点
echo "🔍 关键进度点:"
grep -E "(批次|完成|预计剩余时间)" "$LOG_FILE" | tail -5
echo ""

echo "💡 提示:"
echo "  - 运行 'tail -f $LOG_FILE' 可以实时查看日志"
echo "  - 运行 './check_progress.sh' 可以快速检查当前状态"
echo "  - 运行 './monitor_progress.sh' 可以开始/重启监控"

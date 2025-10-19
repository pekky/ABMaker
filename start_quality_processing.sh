#!/bin/bash
# 高质量批次处理启动脚本 - 保持音质的同时提升速度

echo "🎵 启动高质量PDF转有声读物处理（保持音质的同时提升速度）"
echo "=========================================================="

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <PDF文件> [输出文件] [语音预设] [并行进程数]"
    echo "示例: $0 RivewTown.pdf quality_RiverTown.wav v2/en_speaker_6 2"
    exit 1
fi

PDF_FILE="$1"
OUTPUT_FILE="${2:-quality_audiobook.wav}"
VOICE_PRESET="${3:-v2/en_speaker_6}"
WORKERS="${4:-2}"

echo "PDF文件: $PDF_FILE"
echo "输出文件: $OUTPUT_FILE"
echo "语音预设: $VOICE_PRESET"
echo "并行进程: $WORKERS（保证质量）"
echo ""

# 检查文件是否存在
if [ ! -f "$PDF_FILE" ]; then
    echo "❌ 错误: PDF文件不存在: $PDF_FILE"
    exit 1
fi

# 激活conda环境
echo "激活conda环境..."
source /home/alai/miniconda3/etc/profile.d/conda.sh
conda activate abmaker310

# 设置环境变量优化（只启用不影响质量的项目）
export SUNO_OFFLOAD_CPU=True  # 这个不影响质量
export CUDA_VISIBLE_DEVICES=0

echo "✓ 环境变量设置完成"
echo "✓ 启用CPU卸载（不影响音频质量）"
echo "✓ 使用完整模型（最高音频质量）"
echo "✓ 使用全精度处理（最高音频质量）"
echo ""

# 启动高质量处理
echo "开始高质量处理..."
python3 high_quality_batch_audiobook_maker.py \
    "$PDF_FILE" \
    -o "$OUTPUT_FILE" \
    -v "$VOICE_PRESET" \
    -c 250 \
    -b 50 \
    -w "$WORKERS" \
    --keep-chunks

echo ""
echo "🎉 高质量处理完成！"
echo "输出文件: $OUTPUT_FILE"

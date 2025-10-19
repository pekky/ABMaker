#!/bin/bash
# 高速批次处理启动脚本 - 5倍速度提升

echo "🚀 启动高速PDF转有声读物处理（5倍速度提升）"
echo "================================================"

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <PDF文件> [输出文件] [语音预设] [并行进程数]"
    echo "示例: $0 RivewTown.pdf fast_RiverTown.wav v2/en_speaker_6 4"
    exit 1
fi

PDF_FILE="$1"
OUTPUT_FILE="${2:-fast_audiobook.wav}"
VOICE_PRESET="${3:-v2/en_speaker_6}"
WORKERS="${4:-4}"

echo "PDF文件: $PDF_FILE"
echo "输出文件: $OUTPUT_FILE"
echo "语音预设: $VOICE_PRESET"
echo "并行进程: $WORKERS"
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

# 设置环境变量优化
export SUNO_USE_SMALL_MODELS=True
export SUNO_OFFLOAD_CPU=True
export SUNO_USE_HALF_PRECISION=True
export CUDA_VISIBLE_DEVICES=0

echo "✓ 环境变量设置完成"
echo "✓ 启用小模型模式"
echo "✓ 启用CPU卸载"
echo "✓ 启用混合精度"
echo ""

# 启动高速处理
echo "开始高速处理..."
python3 fast_batch_audiobook_maker.py \
    "$PDF_FILE" \
    -o "$OUTPUT_FILE" \
    -v "$VOICE_PRESET" \
    -c 300 \
    -b 100 \
    -w "$WORKERS" \
    --keep-chunks

echo ""
echo "🎉 高速处理完成！"
echo "输出文件: $OUTPUT_FILE"

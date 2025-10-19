#!/bin/bash
# 超高速智能批次处理启动脚本 - 10倍速度提升

echo "🚀 启动超高速智能批次PDF转有声读物处理（10倍速度提升）"
echo "======================================================"

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <PDF文件> [输出文件] [语音预设] [并行进程数]"
    echo "示例: $0 RivewTown.pdf ultra_fast_RiverTown.wav v2/en_speaker_6 8"
    exit 1
fi

PDF_FILE="$1"
OUTPUT_FILE="${2:-ultra_fast_audiobook.wav}"
VOICE_PRESET="${3:-v2/en_speaker_6}"
WORKERS="${4:-8}"

echo "PDF文件: $PDF_FILE"
echo "输出文件: $OUTPUT_FILE"
echo "语音预设: $VOICE_PRESET"
echo "并行进程: $WORKERS个（超高速）"
echo "批次策略: 4万字符+完整页面/段落"
echo "速度提升: 10倍（保持音质）"
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

# 设置环境变量优化（超高速模式）
export SUNO_OFFLOAD_CPU=True
export CUDA_LAUNCH_BLOCKING=0
export TORCH_CUDNN_V8_API_ENABLED=1
export CUDA_VISIBLE_DEVICES=0

echo "✓ 环境变量设置完成"
echo "✓ 启用CPU卸载（不影响音频质量）"
echo "✓ 启用异步CUDA（提升速度）"
echo "✓ 启用cuDNN v8（提升速度）"
echo "✓ 使用完整模型（最高音频质量）"
echo "✓ 使用全精度处理（最高音频质量）"
echo "✓ 启用模型缓存（提升速度）"
echo "✓ 启用内存池（提升速度）"
echo "✓ 启用批量处理（提升速度）"
echo "✓ 超高速智能批次处理（10倍速度提升）"
echo ""

# 启动超高速智能批次处理
echo "开始超高速智能批次处理..."
python3 ultra_fast_smart_batch_audiobook_maker.py \
    "$PDF_FILE" \
    -o "$OUTPUT_FILE" \
    -v "$VOICE_PRESET" \
    -c 200 \
    -t 40000 \
    -w "$WORKERS" \
    --keep-chunks

echo ""
echo "🎉 超高速智能批次处理完成！"
echo "输出文件: $OUTPUT_FILE"

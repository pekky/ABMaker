#!/bin/bash
# 修复版按4万token分批处理启动脚本 - 每批生成一个音频文件

echo "📚 启动修复版按4万token分批PDF转有声读物处理（每批一个音频文件）"
echo "=========================================================="

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <PDF文件> [输出目录] [语音预设]"
    echo "示例: $0 RivewTown.pdf fixed_token_batch_audio v2/en_speaker_6"
    exit 1
fi

PDF_FILE="$1"
OUTPUT_DIR="${2:-fixed_token_batch_audio_files}"
VOICE_PRESET="${3:-v2/en_speaker_6}"

echo "PDF文件: $PDF_FILE"
echo "输出目录: $OUTPUT_DIR"
echo "语音预设: $VOICE_PRESET"
echo "处理模式: 单线程（修复CUDA多进程问题）"
echo "批次策略: 4万token+完整页面/段落"
echo "输出方式: 每批一个音频文件"
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
export SUNO_OFFLOAD_CPU=True
export CUDA_LAUNCH_BLOCKING=0
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export CUDA_VISIBLE_DEVICES=0

echo "✓ 环境变量设置完成"
echo "✓ 启用CPU卸载（不影响音频质量）"
echo "✓ 启用异步CUDA（提升速度）"
echo "✓ 启用内存分段优化（提升速度）"
echo "✓ 使用完整模型（最高音频质量）"
echo "✓ 使用全精度处理（最高音频质量）"
echo "✓ 单线程处理（修复CUDA多进程问题）"
echo "✓ 按4万token分批处理（每批一个音频文件）"
echo ""

# 启动修复版按token分批处理
echo "开始修复版按4万token分批处理..."
python3 fixed_token_batch_audiobook_maker.py \
    "$PDF_FILE" \
    -o "$OUTPUT_DIR" \
    -v "$VOICE_PRESET" \
    -c 200 \
    -t 40000 \
    --keep-chunks

echo ""
echo "🎉 修复版按4万token分批处理完成！"
echo "输出目录: $OUTPUT_DIR"
echo "音频文件: 每批一个音频文件"
echo "批次信息: $OUTPUT_DIR/batch_info.json"
echo "播放列表: $OUTPUT_DIR/playlist.m3u"

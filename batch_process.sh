#!/bin/bash

# 分批处理有声读物制作脚本
# 降低长时间处理的风险

echo "======================================"
echo "分批处理有声读物制作工具"
echo "======================================"
echo ""

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: $0 <PDF文件> [选项]"
    echo ""
    echo "选项:"
    echo "  -o <输出文件>    输出音频文件路径（默认: audiobook.wav）"
    echo "  -v <语音预设>    语音预设（默认: v2/zh_speaker_1）"
    echo "  -b <批次大小>    每批处理的片段数量（默认: 500）"
    echo "  --small-model    使用小模型（节省显存）"
    echo "  --keep-chunks    保留音频片段文件"
    echo "  --no-resume      不支持断点续传"
    echo ""
    echo "示例:"
    echo "  $0 novel.pdf"
    echo "  $0 novel.pdf -o my_book.wav -b 300"
    echo "  $0 novel.pdf --small-model -b 200"
    exit 1
fi

PDF_FILE="$1"
shift

# 默认参数
OUTPUT_FILE="audiobook.wav"
VOICE_PRESET="v2/zh_speaker_1"
BATCH_SIZE=500
SMALL_MODEL=""
KEEP_CHUNKS=""
NO_RESUME=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -o)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -v)
            VOICE_PRESET="$2"
            shift 2
            ;;
        -b)
            BATCH_SIZE="$2"
            shift 2
            ;;
        --small-model)
            SMALL_MODEL="--small-model"
            shift
            ;;
        --keep-chunks)
            KEEP_CHUNKS="--keep-chunks"
            shift
            ;;
        --no-resume)
            NO_RESUME="--no-resume"
            shift
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查PDF文件是否存在
if [ ! -f "$PDF_FILE" ]; then
    echo "错误: PDF文件不存在: $PDF_FILE"
    exit 1
fi

echo "配置信息:"
echo "  PDF文件: $PDF_FILE"
echo "  输出文件: $OUTPUT_FILE"
echo "  语音预设: $VOICE_PRESET"
echo "  批次大小: $BATCH_SIZE"
echo "  小模型: ${SMALL_MODEL:-否}"
echo "  保留片段: ${KEEP_CHUNKS:-否}"
echo "  断点续传: ${NO_RESUME:-是}"
echo ""

# 构建命令
CMD="python batch_audiobook_maker.py \"$PDF_FILE\" -o \"$OUTPUT_FILE\" -v \"$VOICE_PRESET\" -b $BATCH_SIZE"

if [ -n "$SMALL_MODEL" ]; then
    CMD="$CMD $SMALL_MODEL"
fi

if [ -n "$KEEP_CHUNKS" ]; then
    CMD="$CMD $KEEP_CHUNKS"
fi

if [ -n "$NO_RESUME" ]; then
    CMD="$CMD $NO_RESUME"
fi

echo "执行命令: $CMD"
echo ""

# 询问用户确认
read -p "是否开始分批处理？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "开始分批处理..."
echo "提示: 可以随时按 Ctrl+C 中断，支持断点续传"
echo ""

# 执行命令
eval $CMD

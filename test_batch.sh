#!/bin/bash

# 快速测试分批处理功能
# 使用小PDF文件进行测试

echo "======================================"
echo "分批处理功能测试"
echo "======================================"
echo ""

# 检查是否有测试PDF文件
if [ ! -f "RivewTown.pdf" ]; then
    echo "错误: 未找到测试PDF文件 RivewTown.pdf"
    echo "请确保PDF文件存在"
    exit 1
fi

echo "使用 RivewTown.pdf 进行测试"
echo ""

# 测试参数
PDF_FILE="RivewTown.pdf"
OUTPUT_FILE="test_batch_audiobook.wav"
BATCH_SIZE=100  # 小批次测试
VOICE_PRESET="v2/zh_speaker_1"

echo "测试配置:"
echo "  PDF文件: $PDF_FILE"
echo "  输出文件: $OUTPUT_FILE"
echo "  批次大小: $BATCH_SIZE"
echo "  语音预设: $VOICE_PRESET"
echo ""

# 询问用户确认
read -p "开始测试分批处理？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消测试"
    exit 0
fi

echo ""
echo "开始测试..."

# 执行测试命令
python batch_audiobook_maker.py "$PDF_FILE" \
    -o "$OUTPUT_FILE" \
    -v "$VOICE_PRESET" \
    -b $BATCH_SIZE \
    --small-model \
    --keep-chunks

echo ""
echo "测试完成！"
echo "输出文件: $OUTPUT_FILE"
echo "临时文件保留在: temp_audio_chunks/"
echo "状态文件: batch_processing_state.json"

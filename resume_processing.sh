#!/bin/bash

# 断点续传脚本

echo "======================================"
echo "断点续传有声读物制作"
echo "======================================"
echo ""

# 检查状态文件是否存在
if [ ! -f "batch_processing_state.json" ]; then
    echo "错误: 未找到状态文件 batch_processing_state.json"
    echo "请确保之前有运行过分批处理"
    exit 1
fi

# 显示当前状态
echo "当前状态:"
python3 -c "
import json
with open('batch_processing_state.json', 'r') as f:
    state = json.load(f)
    print(f'  总片段数: {state[\"total_chunks\"]}')
    print(f'  已处理: {state[\"processed_chunks\"]}')
    print(f'  完成批次: {len(state[\"completed_batches\"])}')
    print(f'  进度: {state[\"processed_chunks\"]/state[\"total_chunks\"]*100:.1f}%')
"

echo ""

# 询问是否继续
read -p "是否继续处理？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "继续处理..."

# 重新启动处理
python batch_audiobook_maker.py RivewTown.pdf \
    -o RiverTown.wav \
    -v v2/en_speaker_6 \
    -b 500 \
    --small-model > batch_processing.log 2>&1 &

echo "处理已重新启动"
echo "查看进度: tail -f batch_processing.log"
echo "进程ID: $!"

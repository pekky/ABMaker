#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试音频生成 - 只生成10个片段
"""
import os
import sys
from audio_generator import AudioGenerator
from smart_pdf_extractor import SmartPDFExtractor
from text_processor import TextProcessor
from scipy.io import wavfile
import numpy as np

def quick_test():
    """快速测试音频生成功能"""
    print("🎵 快速测试音频生成 - 10个片段样本")
    print("=" * 50)
    
    # 创建音频生成器
    print("正在加载Bark模型...")
    audio_gen = AudioGenerator(voice_preset='v2/en_speaker_6', use_small_model=False)
    print("✓ Bark模型加载完成")
    
    # 提取PDF文本
    print("\n正在提取PDF文本...")
    extractor = SmartPDFExtractor('RivewTown.pdf')
    structure_data = extractor.extract_text_with_structure()
    
    # 获取第一批的文本内容（第2-95页）
    batch_1_pages = structure_data['pages'][1:95]  # 第2-95页
    batch_1_text = '\n\n'.join([page['text'] for page in batch_1_pages])
    
    # 分割成片段
    text_processor = TextProcessor(max_chars=200)
    batch_1_chunks = text_processor.split_into_chunks(batch_1_text)
    
    print(f"✓ 第一批总片段数: {len(batch_1_chunks)}")
    print(f"✓ 将生成前10个片段作为样本")
    
    # 创建输出目录
    output_dir = "quick_test_sample"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成前10个片段
    print(f"\n开始生成前10个片段...")
    sample_chunks = batch_1_chunks[:10]
    audio_files = []
    
    for i, chunk in enumerate(sample_chunks):
        print(f"生成片段 {i+1}/10: {chunk[:50]}...")
        
        try:
            # 生成音频
            audio_array = audio_gen.generate_single_audio(chunk)
            
            # 保存音频片段
            chunk_path = os.path.join(output_dir, f"sample_chunk_{i:02d}.wav")
            wavfile.write(chunk_path, audio_gen.sample_rate, audio_array)
            audio_files.append(chunk_path)
            
            # 检查音频质量
            is_silent = np.all(audio_array == 0)
            duration = len(audio_array) / audio_gen.sample_rate
            print(f"  ✓ 时长: {duration:.2f}秒, 静音: {is_silent}")
            
        except Exception as e:
            print(f"  ❌ 生成失败: {e}")
            # 创建静音占位符
            chunk_path = os.path.join(output_dir, f"sample_chunk_{i:02d}.wav")
            silence = np.zeros(int(0.5 * audio_gen.sample_rate), dtype=np.float32)
            wavfile.write(chunk_path, audio_gen.sample_rate, silence)
            audio_files.append(chunk_path)
    
    # 合并所有片段
    print(f"\n正在合并音频片段...")
    merged_audio = audio_gen.merge_audio_files(
        audio_files, 
        os.path.join(output_dir, "sample_merged.wav"),
        silence_duration=0.2
    )
    
    if merged_audio:
        print(f"✓ 样本音频已生成: {output_dir}/sample_merged.wav")
        
        # 检查合并后的音频
        sample_rate, audio_data = wavfile.read(merged_audio)
        is_silent = np.all(audio_data == 0)
        duration = len(audio_data) / sample_rate
        
        print(f"✓ 合并音频时长: {duration:.2f}秒")
        print(f"✓ 音频是否静音: {is_silent}")
        
        if not is_silent:
            print(f"✓ 音频数据范围: {audio_data.min():.6f} 到 {audio_data.max():.6f}")
            print("🎉 样本音频生成成功！")
            return True
        else:
            print("❌ 合并后的音频是静音的")
            return False
    else:
        print("❌ 音频合并失败")
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)

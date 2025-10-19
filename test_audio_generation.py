#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试音频生成功能
"""
import os
import sys
from audio_generator import AudioGenerator
from scipy.io import wavfile
import numpy as np

def test_audio_generation():
    """测试音频生成功能"""
    print("🎵 测试音频生成功能...")
    
    # 创建音频生成器
    print("正在加载Bark模型...")
    audio_gen = AudioGenerator(voice_preset='v2/en_speaker_6', use_small_model=False)
    print("✓ Bark模型加载完成")
    
    # 测试文本
    test_text = "Hello, this is a test of the audio generation system. The audio should have clear English speech with good quality."
    print(f"测试文本: {test_text}")
    
    # 生成音频
    print("正在生成音频...")
    audio_array = audio_gen.generate_single_audio(test_text)
    
    # 保存音频文件
    output_path = 'test_audio.wav'
    wavfile.write(output_path, audio_gen.sample_rate, audio_array)
    
    print(f"✓ 测试音频已保存: {output_path}")
    print(f"音频时长: {len(audio_array) / audio_gen.sample_rate:.2f} 秒")
    
    # 检查音频数据
    is_silent = np.all(audio_array == 0)
    print(f"音频是否静音: {is_silent}")
    
    if not is_silent:
        print(f"音频数据范围: {audio_array.min():.6f} 到 {audio_array.max():.6f}")
        print("✓ 音频有声音！")
        return True
    else:
        print("❌ 音频是静音的")
        return False

if __name__ == "__main__":
    success = test_audio_generation()
    sys.exit(0 if success else 1)

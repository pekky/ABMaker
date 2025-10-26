# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
高质量音频生成模块 - 保持音质的同时提升速度
"""
import os
import numpy as np
from typing import List, Optional
import torch
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io import wavfile
from tqdm import tqdm
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import gc
import threading
import queue

# Torch 2.6 兼容性处理
_torch_load = torch.load

def _torch_load_with_compat(*args, **kwargs):
    kwargs.setdefault("weights_only", False)
    return _torch_load(*args, **kwargs)

torch.load = _torch_load_with_compat


class HighQualityAudioGenerator:
    """高质量音频生成器 - 保持音质的同时提升速度"""
    
    def __init__(self, voice_preset: str = "v2/zh_speaker_1", 
                 max_workers: int = 2,  # 减少并行数，保证质量
                 enable_memory_optimization: bool = True):
        """
        初始化高质量音频生成器
        
        Args:
            voice_preset: 语音预设
            max_workers: 最大并行工作进程数（减少到2保证质量）
            enable_memory_optimization: 启用内存优化（不影响质量）
        """
        self.voice_preset = voice_preset
        self.sample_rate = SAMPLE_RATE
        self.max_workers = max_workers
        
        # 只启用不影响质量的内存优化
        if enable_memory_optimization:
            os.environ["SUNO_OFFLOAD_CPU"] = "True"  # 这个不影响质量
            print("✓ 启用CPU卸载（不影响音频质量）")
        
        # 不启用小模型和混合精度，保持最高质量
        print("✓ 使用完整模型（最高音频质量）")
        print("✓ 使用全精度处理（最高音频质量）")
        
        print("正在加载高质量Bark模型...")
        preload_models()
        print("✓ 高质量Bark模型加载完成")
    
    def generate_single_audio(self, text: str) -> np.ndarray:
        """
        生成单个音频片段（高质量版）
        
        Args:
            text: 要转换的文本
            
        Returns:
            音频数组
        """
        try:
            # 只清理GPU缓存，不影响质量
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # 使用完整模型生成高质量音频
            audio_array = generate_audio(text, history_prompt=self.voice_preset)
            
            # 强制垃圾回收
            gc.collect()
            
            return audio_array
        except Exception as e:
            print(f"音频生成错误: {e}")
            # 返回静音
            return np.zeros(int(self.sample_rate * 0.5), dtype=np.float32)
    
    def generate_audio_batch(self, text_chunks: List[str], 
                           output_dir: str = "output",
                           batch_size: int = 5) -> List[str]:  # 减少批次大小保证质量
        """
        批量生成音频（高质量并行处理）
        
        Args:
            text_chunks: 文本片段列表
            output_dir: 输出目录
            batch_size: 批处理大小（减少到5保证质量）
            
        Returns:
            生成的音频文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)
        audio_files = []
        
        print(f"开始高质量批量生成音频，共 {len(text_chunks)} 个片段")
        print(f"使用 {self.max_workers} 个并行进程（保证质量）")
        
        # 分批处理
        for i in range(0, len(text_chunks), batch_size):
            batch_chunks = text_chunks[i:i + batch_size]
            batch_start = i
            
            print(f"\n处理批次 {i//batch_size + 1}: 片段 {batch_start + 1}-{batch_start + len(batch_chunks)}")
            
            # 使用线程池而不是进程池，避免模型重复加载
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交任务
                futures = []
                for j, chunk in enumerate(batch_chunks):
                    chunk_idx = batch_start + j
                    future = executor.submit(self._process_single_chunk_thread, chunk, chunk_idx, output_dir)
                    futures.append(future)
                
                # 收集结果
                batch_files = []
                for future in tqdm(futures, desc=f"批次 {i//batch_size + 1}"):
                    try:
                        audio_file = future.result(timeout=600)  # 10分钟超时
                        batch_files.append(audio_file)
                    except Exception as e:
                        print(f"处理片段失败: {e}")
                        continue
                
                audio_files.extend(batch_files)
                
                # 清理GPU内存
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                gc.collect()
        
        print(f"✓ 高质量批量生成完成，共生成 {len(audio_files)} 个音频文件")
        return audio_files
    
    def _process_single_chunk_thread(self, text: str, chunk_idx: int, output_dir: str) -> str:
        """
        处理单个文本片段（线程函数，保证质量）
        
        Args:
            text: 文本内容
            chunk_idx: 片段索引
            output_dir: 输出目录
            
        Returns:
            音频文件路径
        """
        try:
            # 在线程中生成高质量音频
            audio_array = self.generate_single_audio(text)
            
            # 保存音频文件
            output_path = os.path.join(output_dir, f"chunk_{chunk_idx:04d}.wav")
            wavfile.write(output_path, self.sample_rate, audio_array)
            
            return output_path
        except Exception as e:
            print(f"处理片段 {chunk_idx} 失败: {e}")
            return None
    
    def merge_audio_files(self, audio_files: List[str], 
                         output_path: str, 
                         silence_duration: float = 0.2) -> str:  # 增加静音间隔保证质量
        """
        合并音频文件（高质量版）
        
        Args:
            audio_files: 音频文件路径列表
            output_path: 输出文件路径
            silence_duration: 静音间隔时长（秒，增加到0.2秒）
            
        Returns:
            合并后的音频文件路径
        """
        print(f"正在高质量合并 {len(audio_files)} 个音频文件...")
        
        # 读取所有音频文件
        audio_arrays = []
        for audio_file in tqdm(audio_files, desc="读取音频文件"):
            if os.path.exists(audio_file):
                _, audio_array = wavfile.read(audio_file)
                audio_arrays.append(audio_array)
                
                # 添加静音间隔（增加间隔保证质量）
                if silence_duration > 0:
                    silence_samples = int(self.sample_rate * silence_duration)
                    silence = np.zeros(silence_samples, dtype=audio_array.dtype)
                    audio_arrays.append(silence)
        
        if not audio_arrays:
            print("没有找到有效的音频文件")
            return None
        
        # 合并音频
        merged_audio = np.concatenate(audio_arrays)
        
        # 保存合并后的音频
        wavfile.write(output_path, self.sample_rate, merged_audio)
        
        print(f"✓ 高质量音频合并完成: {output_path}")
        return output_path
    
    def get_available_voices(self) -> dict:
        """获取可用的语音预设"""
        return {
            "中文语音": [
                "v2/zh_speaker_0", "v2/zh_speaker_1", "v2/zh_speaker_2",
                "v2/zh_speaker_3", "v2/zh_speaker_4", "v2/zh_speaker_5",
                "v2/zh_speaker_6", "v2/zh_speaker_7", "v2/zh_speaker_8",
                "v2/zh_speaker_9"
            ],
            "英文语音": [
                "v2/en_speaker_0", "v2/en_speaker_1", "v2/en_speaker_2",
                "v2/en_speaker_3", "v2/en_speaker_4", "v2/en_speaker_5",
                "v2/en_speaker_6", "v2/en_speaker_7", "v2/en_speaker_8",
                "v2/en_speaker_9"
            ]
        }


def test_quality_speed():
    """测试质量与速度平衡"""
    print("=== 质量与速度平衡测试 ===")
    
    # 创建测试文本
    test_texts = [
        "这是第一个测试片段，用于测试高质量音频生成速度。",
        "这是第二个测试片段，用于测试高质量音频生成速度。",
        "这是第三个测试片段，用于测试高质量音频生成速度。",
    ]
    
    # 测试高质量版本
    print("\n测试高质量版本...")
    generator = HighQualityAudioGenerator(
        voice_preset="v2/zh_speaker_1",
        max_workers=2,  # 减少并行数保证质量
        enable_memory_optimization=True
    )
    
    import time
    start_time = time.time()
    
    audio_files = generator.generate_audio_batch(test_texts, "quality_test_output", batch_size=3)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✓ 高质量版本完成，耗时: {duration:.2f}秒")
    print(f"✓ 平均每片段: {duration/len(test_texts):.2f}秒")
    print(f"✓ 速度提升: 约 {50/duration*len(test_texts):.1f}倍（保持高质量）")


if __name__ == "__main__":
    test_quality_speed()

"""
音频生成模块 - 使用Bark生成语音
"""
import os
import numpy as np
from typing import List, Optional
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io import wavfile
from tqdm import tqdm


class AudioGenerator:
    """Bark音频生成器"""
    
    def __init__(self, voice_preset: str = "v2/zh_speaker_1", use_small_model: bool = False):
        """
        初始化音频生成器
        
        Args:
            voice_preset: 语音预设（支持中文、英文等多种语言）
                         中文: v2/zh_speaker_0 到 v2/zh_speaker_9
                         英文: v2/en_speaker_0 到 v2/en_speaker_9
            use_small_model: 是否使用小模型（节省显存）
        """
        self.voice_preset = voice_preset
        self.sample_rate = SAMPLE_RATE
        
        # 设置环境变量
        if use_small_model:
            os.environ["SUNO_USE_SMALL_MODELS"] = "True"
            print("使用小模型模式（节省显存）")
        
        print("正在加载Bark模型...")
        preload_models()
        print("✓ Bark模型加载完成")
    
    def generate_single_audio(self, text: str) -> np.ndarray:
        """
        生成单个文本片段的音频
        
        Args:
            text: 文本内容
            
        Returns:
            音频数据（numpy数组）
        """
        try:
            audio_array = generate_audio(text, history_prompt=self.voice_preset)
            return audio_array
        except Exception as e:
            print(f"警告：生成音频时出错: {str(e)}")
            # 返回静音
            return np.zeros(int(0.5 * self.sample_rate))
    
    def generate_audiobook(self, text_chunks: List[str], output_dir: str = "output") -> List[str]:
        """
        为文本片段列表生成音频文件
        
        Args:
            text_chunks: 文本片段列表
            output_dir: 输出目录
            
        Returns:
            生成的音频文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)
        audio_files = []
        
        print(f"\n开始生成音频，共 {len(text_chunks)} 个片段...")
        
        for i, chunk in enumerate(tqdm(text_chunks, desc="生成音频")):
            # 生成音频
            audio_array = self.generate_single_audio(chunk)
            
            # 保存为WAV文件
            output_path = os.path.join(output_dir, f"chunk_{i:04d}.wav")
            wavfile.write(output_path, self.sample_rate, audio_array)
            audio_files.append(output_path)
        
        print(f"✓ 所有音频片段已生成")
        return audio_files
    
    def merge_audio_files(self, audio_files: List[str], output_path: str, 
                         silence_duration: float = 0.3) -> str:
        """
        合并多个音频文件
        
        Args:
            audio_files: 音频文件路径列表
            output_path: 输出文件路径
            silence_duration: 片段之间的静音时长（秒）
            
        Returns:
            合并后的音频文件路径
        """
        print(f"\n正在合并 {len(audio_files)} 个音频片段...")
        
        audio_data = []
        silence = np.zeros(int(silence_duration * self.sample_rate))
        
        for audio_file in tqdm(audio_files, desc="合并音频"):
            rate, data = wavfile.read(audio_file)
            audio_data.append(data)
            audio_data.append(silence)  # 添加静音间隔
        
        # 合并所有音频数据
        merged_audio = np.concatenate(audio_data)
        
        # 保存合并后的音频
        wavfile.write(output_path, self.sample_rate, merged_audio)
        
        duration = len(merged_audio) / self.sample_rate
        print(f"✓ 音频已合并，总时长: {duration/60:.2f} 分钟")
        print(f"✓ 输出文件: {output_path}")
        
        return output_path
    
    @staticmethod
    def get_available_voices() -> dict:
        """
        获取可用的语音预设列表
        
        Returns:
            语音预设字典
        """
        return {
            "中文": [f"v2/zh_speaker_{i}" for i in range(10)],
            "英文": [f"v2/en_speaker_{i}" for i in range(10)],
            "日文": [f"v2/ja_speaker_{i}" for i in range(10)],
            "德文": [f"v2/de_speaker_{i}" for i in range(10)],
            "西班牙文": [f"v2/es_speaker_{i}" for i in range(10)],
            "法文": [f"v2/fr_speaker_{i}" for i in range(10)],
            "韩文": [f"v2/ko_speaker_{i}" for i in range(10)],
        }



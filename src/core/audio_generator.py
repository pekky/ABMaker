# -*- coding: utf-8 -*-
"""
音频生成模块 - 使用Bark生成语音
"""
import os
import numpy as np
import torch
import sys

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io import wavfile
from pydub import AudioSegment
from tqdm import tqdm
from utils.config_manager import ConfigManager

# Torch 2.6 flips torch.load(weights_only=True) by default; Bark checkpoints rely on legacy pickles.
# Keep behavior backwards-compatible while we trust upstream Bark releases.
_torch_load = torch.load


def _torch_load_with_compat(*args, **kwargs):
    kwargs.setdefault("weights_only", False)
    return _torch_load(*args, **kwargs)


torch.load = _torch_load_with_compat


class AudioGenerator:
    """Bark音频生成器"""
    
    def __init__(
        self,
        voice_preset=None,
        use_small_model=None,
        config_manager=None,
        **kwargs
    ):
        """
        初始化音频生成器
        
        Args:
            voice_preset: 语音预设（可选，优先使用配置）
            use_small_model: 是否使用小模型（可选，优先使用配置）
            config_manager: 配置管理器实例
            **kwargs: 其他参数（会覆盖配置）
        """
        self.config_manager = config_manager or ConfigManager()
        self.bark_config = self.config_manager.get_bark_config()
        self.resource_config = self.config_manager.get_resource_config()
        
        # 从配置获取参数
        self.voice_preset = voice_preset or self.bark_config.get("default_voice", "v2/en_speaker_0")
        self.use_small_model = use_small_model if use_small_model is not None else self.bark_config.get("use_small_model", False)
        
        # Bark生成参数
        self.text_temp = kwargs.get("text_temp", self.bark_config.get("text_temp", 0.65))
        self.waveform_temp = kwargs.get("waveform_temp", self.bark_config.get("waveform_temp", 0.55))
        self.seed = kwargs.get("seed", self.bark_config.get("seed", 1234))
        
        self.sample_rate = SAMPLE_RATE
        
        # 设置环境变量
        if self.use_small_model:
            os.environ["SUNO_USE_SMALL_MODELS"] = "True"
            print("使用小模型模式（节省显存）")
        
        # 预热和缓存优化
        if self.resource_config.get("preload_models", True):
            print("正在预热Bark模型...")
            preload_models()
        
        # 设置GPU优化
        if self.resource_config.get("enable_gpu_optimization", True) and torch.cuda.is_available():
            torch.backends.cudnn.benchmark = self.resource_config.get("cudnn_benchmark", True)
            torch.backends.cudnn.deterministic = self.resource_config.get("cudnn_deterministic", False)
            print("✓ GPU优化已启用")
        
        print("✓ Bark模型预热完成")
    
    def generate_single_audio(self, text: str) -> np.ndarray:
        """
        生成单个文本片段的音频
        
        Args:
            text: 文本内容
            
        Returns:
            音频数据（numpy数组）
        """
        try:
            if self.seed is not None:
                try:
                    torch.manual_seed(int(self.seed))
                except Exception:
                    pass

            audio_array = generate_audio(
                text,
                history_prompt=self.voice_preset,
                text_temp=self.text_temp,
                waveform_temp=self.waveform_temp,
            )
            return audio_array
        except Exception as e:
            print(f"警告：生成音频时出错: {str(e)}")
            # 返回静音
            return np.zeros(int(0.5 * self.sample_rate))
    
    def _save_audio_as_mp3(self, audio_array, output_path, bitrate="320k"):
        """
        将音频数组保存为 MP3 格式
        
        Args:
            audio_array: 音频数据数组 (numpy array)
            output_path: 输出文件路径 (.mp3)
            bitrate: MP3 比特率 (默认 320k，可选: 256k, 192k, 128k)
        
        Returns:
            str: 输出文件路径
        """
        try:
            # 归一化音频数据到 [-1, 1]
            if np.max(np.abs(audio_array)) > 0:
                audio_normalized = audio_array / np.max(np.abs(audio_array))
            else:
                audio_normalized = audio_array
            
            # 转换为 int16 格式 (WAV 标准)
            audio_int16 = np.int16(audio_normalized * 32767)
            
            # 创建临时 WAV 文件
            temp_wav = output_path.replace('.mp3', '_temp.wav')
            wavfile.write(temp_wav, self.sample_rate, audio_int16)
            
            # 使用 pydub 转换为 MP3
            audio_segment = AudioSegment.from_wav(temp_wav)
            audio_segment.export(
                output_path,
                format="mp3",
                bitrate=bitrate,
                parameters=["-q:a", "0"]  # 最高质量的 VBR 编码
            )
            
            # 删除临时 WAV 文件
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            
            return output_path
            
        except Exception as e:
            print(f"❌ 保存 MP3 失败: {e}")
            # 如果失败，回退到 WAV 格式
            wav_path = output_path.replace('.mp3', '.wav')
            audio_int16 = np.int16(audio_normalized * 32767)
            wavfile.write(wav_path, self.sample_rate, audio_int16)
            print(f"⚠️  已保存为 WAV 格式: {wav_path}")
            return wav_path
    
    def generate_audiobook(self, text_chunks, output_dir="output"):
        """
        为文本片段列表生成音频文件，优化批量处理
        
        Args:
            text_chunks: 文本片段列表
            output_dir: 输出目录
            
        Returns:
            生成的音频文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)
        audio_files = []
        
        print("\n开始批量生成音频，共 " + str(len(text_chunks)) + " 个片段...")
        
        # 批量处理优化
        for i, chunk in enumerate(tqdm(text_chunks, desc="生成音频")):
            # 生成音频
            audio_array = self.generate_single_audio(chunk)
            
            # 保存为MP3文件
            output_path = os.path.join(output_dir, "chunk_" + str(i).zfill(4) + ".mp3")
            self._save_audio_as_mp3(audio_array, output_path, bitrate="320k")
            audio_files.append(output_path)
            
            # 定期清理GPU缓存
            if i % 10 == 0 and torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        print("✓ 所有音频片段已生成")
        return audio_files
    
    def merge_audio_files(
        self,
        audio_files,
        output_path,
        **kwargs
    ):
        """
        合并多个音频文件，优化停顿时长和音频质量
        
        Args:
            audio_files: 音频文件路径列表
            output_path: 输出文件路径
            **kwargs: 其他参数（会覆盖配置）
            
        Returns:
            合并后的音频文件路径
        """
        # 从配置获取音频处理参数
        audio_config = self.config_manager.get_audio_config()
        
        silence_duration = kwargs.get("silence_duration", audio_config.get("segment_silence", 0.3))
        sentence_silence = kwargs.get("sentence_silence", audio_config.get("sentence_silence", 0.08))
        fade_ms = kwargs.get("fade_ms", audio_config.get("fade_ms", 6.0))
        peak_dbfs = kwargs.get("peak_dbfs", audio_config.get("peak_dbfs", -1.0))
        lufs_target = kwargs.get("lufs_target", audio_config.get("lufs_target", -18.0))
        enable_denoise = kwargs.get("enable_denoise", audio_config.get("enable_denoise", True))
        enable_deesser = kwargs.get("enable_deesser", audio_config.get("enable_deesser", True))
        print(f"\n正在合并 {len(audio_files)} 个音频片段...")
        
        def _lufs_normalize(x, target_lufs):
            """简单的LUFS归一化（简化版）"""
            # 计算RMS
            rms = np.sqrt(np.mean(x ** 2))
            if rms > 0:
                # 简化的LUFS计算
                lufs = 20 * np.log10(rms)
                scale = 10 ** ((target_lufs - lufs) / 20)
                return np.clip(x * scale, -1.0, 1.0)
            return x
        
        def _peak_normalize(x, peak_dbfs):
            """峰值归一化"""
            if len(x) == 0:
                return x
            # 计算峰值
            peak = np.max(np.abs(x))
            if peak > 0:
                # 转换为dBFS
                peak_dbfs_actual = 20 * np.log10(peak)
                # 计算缩放因子
                scale = 10 ** ((peak_dbfs - peak_dbfs_actual) / 20)
                return np.clip(x * scale, -1.0, 1.0)
            return x
        
        def _apply_light_denoise(x, threshold=0.01):
            """轻度门限式降噪"""
            # 简单的门限降噪
            mask = np.abs(x) > threshold
            return x * mask
        
        def _apply_deesser(x, sample_rate):
            """轻度去齿音（简化版）"""
            # 简单的去齿音处理
            # 这里使用简单的低通滤波
            from scipy import signal
            if len(x) > 1000:  # 确保有足够的数据
                b, a = signal.butter(4, 8000 / (sample_rate / 2), btype='low')
                return signal.filtfilt(b, a, x)
            return x

        def _to_float32_m1_p1(x):
            """转换为float32格式"""
            if x.dtype.kind in ("i", "u"):
                # 16-bit PCM -> float32 [-1, 1]
                max_int = np.iinfo(x.dtype).max
                x = x.astype(np.float32) / float(max_int)
            else:
                x = x.astype(np.float32)
            return np.clip(x, -1.0, 1.0)

        def _apply_fade(x: np.ndarray, fade_ms_val: float) -> np.ndarray:
            n = int(self.sample_rate * (fade_ms_val / 1000.0))
            if n <= 0 or n * 2 >= len(x):
                return x
            ramp_in = np.linspace(0.0, 1.0, n, dtype=np.float32)
            ramp_out = np.linspace(1.0, 0.0, n, dtype=np.float32)
            y = x.copy()
            y[:n] *= ramp_in
            y[-n:] *= ramp_out
            return y

        audio_data = []
        segment_silence = np.zeros(int(silence_duration * self.sample_rate), dtype=np.float32)
        sentence_silence_array = np.zeros(int(sentence_silence * self.sample_rate), dtype=np.float32)
        
        for i, audio_file in enumerate(tqdm(audio_files, desc="合并音频")):
            # 支持 MP3 和 WAV 格式
            if audio_file.endswith('.mp3'):
                audio_segment = AudioSegment.from_mp3(audio_file)
                rate = audio_segment.frame_rate
                data = np.array(audio_segment.get_array_of_samples())
                if audio_segment.channels == 2:
                    data = data.reshape((-1, 2))
                    data = data.mean(axis=1)  # 转为单声道
            else:
                rate, data = wavfile.read(audio_file)
            
            if rate != self.sample_rate:
                # 保持24kHz采样率
                pass

            # 音频处理流水线
            f = _to_float32_m1_p1(data)
            
            # 轻度去噪和去齿音
            if enable_denoise:
                f = _apply_light_denoise(f, audio_config.get("denoise_threshold", 0.01))
            if enable_deesser:
                f = _apply_deesser(f, self.sample_rate)
            
            # 归一化
            f = _lufs_normalize(f, lufs_target)
            f = _peak_normalize(f, peak_dbfs)
            
            # 交叉淡化
            f = _apply_fade(f, fade_ms)

            audio_data.append(f)
            
            # 添加适当的静音间隔
            if i < len(audio_files) - 1:  # 不是最后一个文件
                audio_data.append(segment_silence)
        
        # 合并所有音频数据
        merged_audio = np.concatenate(audio_data)
        
        # 保存合并后的音频
        if output_path.endswith('.mp3'):
            self._save_audio_as_mp3(merged_audio, output_path, bitrate="320k")
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✓ MP3 文件大小: {file_size_mb:.1f} MB")
        else:
            # 保持 WAV 格式的兼容性，使用 int16 格式
            audio_normalized = merged_audio / np.max(np.abs(merged_audio))
            audio_int16 = np.int16(audio_normalized * 32767)
            wavfile.write(output_path, self.sample_rate, audio_int16)
        
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


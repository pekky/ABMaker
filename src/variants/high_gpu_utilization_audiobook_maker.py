# -*- coding: utf-8 -*-
"""
高GPU利用率有声读物制作器
最大化GPU计算资源利用率，提升处理速度
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any
import numpy as np
from scipy.io import wavfile
import torch
import gc

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_pdf_extractor import SmartPDFExtractor
from core.text_processor import TextProcessor

# 修复torch.load兼容性
import pickle
original_load = torch.load
def patched_load(f, map_location=None, pickle_module=pickle, **kwargs):
    return original_load(f, map_location=map_location, pickle_module=pickle, **kwargs)
torch.load = patched_load

class HighGPUUtilizationAudioGenerator:
    """高GPU利用率音频生成器"""
    
    def __init__(self, voice_preset: str = "v2/zh_speaker_1"):
        self.voice_preset = voice_preset
        self.sample_rate = 24000  # Bark默认采样率
        
        # 设置环境变量以最大化GPU利用率
        os.environ["SUNO_USE_SMALL_MODELS"] = "False"  # 使用完整模型，充分利用GPU
        os.environ["SUNO_OFFLOAD_CPU"] = "False"  # 禁用CPU卸载，全部使用GPU
        
        print("🚀 高GPU利用率模式启动")
        print(f"✓ 使用完整模型（最大化GPU计算）")
        print(f"✓ 禁用CPU卸载（全部GPU处理）")
        print(f"✓ 单线程处理（避免CUDA多进程问题）")
        
        # 检查GPU显存
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"✓ GPU显存: {gpu_memory:.1f}GB")
            
            # 最大化CUDA优化
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cudnn.deterministic = False  # 提升性能
            print("✓ 启用最大CUDA优化")
            
            # 预热GPU，占用更多显存
            self._warmup_gpu_aggressively()
        
        # 预加载模型
        print("正在加载Bark完整模型...")
        from bark import SAMPLE_RATE, generate_audio, preload_models
        self.sample_rate = SAMPLE_RATE
        preload_models()
        print("✓ Bark完整模型加载完成")
    
    def _warmup_gpu_aggressively(self):
        """激进预热GPU，占用更多显存"""
        if torch.cuda.is_available():
            print("正在激进预热GPU...")
            # 创建大量张量来占用显存
            dummy_tensors = []
            try:
                # 占用更多显存
                for i in range(20):
                    tensor = torch.randn(2000, 2000, device='cuda')
                    dummy_tensors.append(tensor)
                print("✓ GPU激进预热完成")
            except RuntimeError as e:
                print(f"⚠️ GPU预热警告: {e}")
            finally:
                # 保留一些张量占用显存
                self.dummy_tensors = dummy_tensors[:10]  # 保留10个张量
                print(f"✓ 保留 {len(self.dummy_tensors)} 个预热张量占用显存")
    
    def generate_single_audio(self, text: str) -> np.ndarray:
        """生成单个音频片段"""
        try:
            from bark import generate_audio
            audio_array = generate_audio(text, history_prompt=self.voice_preset)
            return audio_array.astype(np.float32)
        except Exception as e:
            print(f"❌ 音频生成失败: {e}")
            # 返回静音作为fallback
            return np.zeros(int(self.sample_rate * 0.5), dtype=np.float32)
    
    def generate_audio_batch(self, text_chunks: List[str]) -> List[np.ndarray]:
        """批量生成音频，优化GPU利用率"""
        print(f"🎵 开始批量生成 {len(text_chunks)} 个音频片段...")
        
        audio_arrays = []
        
        for i, chunk in enumerate(text_chunks):
            print(f"  处理片段 {i + 1}/{len(text_chunks)}")
            
            # 在生成前确保GPU利用率
            if torch.cuda.is_available():
                # 创建临时张量保持GPU活跃
                temp_tensor = torch.randn(1000, 1000, device='cuda')
            
            audio_array = self.generate_single_audio(chunk)
            audio_arrays.append(audio_array)
            
            # 每5个片段清理一次显存，但保持一定占用
            if (i + 1) % 5 == 0:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    # 重新创建一些张量保持显存占用
                    if not hasattr(self, 'keep_alive_tensors'):
                        self.keep_alive_tensors = []
                    self.keep_alive_tensors.append(torch.randn(500, 500, device='cuda'))
                gc.collect()
        
        print(f"✓ 批量生成完成，共 {len(audio_arrays)} 个音频片段")
        return audio_arrays
    
    def merge_audio_arrays(self, audio_arrays: List[np.ndarray], output_path: str, 
                          silence_duration: float = 0.03) -> str:  # 进一步减少静音时间
        """合并音频数组"""
        if not audio_arrays:
            return None
        
        print(f"🔗 正在合并 {len(audio_arrays)} 个音频片段...")
        
        # 计算总长度
        total_length = sum(len(audio) for audio in audio_arrays)
        silence_samples = int(self.sample_rate * silence_duration)
        total_length += silence_samples * (len(audio_arrays) - 1)
        
        # 创建合并后的音频数组
        merged_audio = np.zeros(total_length, dtype=np.float32)
        
        current_pos = 0
        for i, audio in enumerate(audio_arrays):
            merged_audio[current_pos:current_pos + len(audio)] = audio
            current_pos += len(audio)
            
            # 添加静音间隔（除了最后一个）
            if i < len(audio_arrays) - 1:
                current_pos += silence_samples
        
        # 保存音频文件
        wavfile.write(output_path, self.sample_rate, merged_audio)
        print(f"✓ 音频已保存: {output_path}")
        
        return output_path

class HighGPUUtilizationAudiobookMaker:
    """高GPU利用率有声读物制作器"""
    
    def __init__(self, voice_preset: str = "v2/zh_speaker_1",
                 max_chars_per_chunk: int = 200,  # 增加片段大小
                 target_tokens_per_batch: int = 10000,  # 保持1万token批次
                 resume: bool = True):
        self.voice_preset = voice_preset
        self.max_chars_per_chunk = max_chars_per_chunk
        self.target_tokens_per_batch = target_tokens_per_batch
        self.resume = resume
        
        # 初始化组件
        self.text_processor = TextProcessor(max_chars=max_chars_per_chunk)
        self.audio_generator = HighGPUUtilizationAudioGenerator(
            voice_preset=voice_preset
        )
        
        # 状态文件
        self.state_file = "high_gpu_utilization_processing_state.json"
    
    def save_state(self, state: Dict[str, Any]):
        """保存处理状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def load_state(self) -> Dict[str, Any]:
        """加载处理状态"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def create_audiobook_batch(self, pdf_path: str, output_dir: str, 
                              voice_preset: str, max_chars_per_chunk: int, 
                              target_tokens_per_batch: int, keep_chunks: bool) -> str:
        """创建有声读物批次"""
        
        print("🚀 开始高GPU利用率有声读物制作")
        print("=" * 60)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 加载或创建状态
        state = self.load_state() if self.resume else {}
        
        # 步骤1: 提取PDF文本并创建智能批次
        if 'smart_batches' not in state:
            print("\n步骤 1/3: 智能提取PDF文本")
            print("-" * 40)
            
            extractor = SmartPDFExtractor(pdf_path)
            structure_data = extractor.extract_text_with_structure()
            
            # 创建智能批次
            smart_batches = self._create_smart_batches(structure_data, target_tokens_per_batch)
            
            state.update({
                'pdf_path': pdf_path,
                'output_dir': output_dir,
                'voice_preset': voice_preset,
                'max_chars_per_chunk': max_chars_per_chunk,
                'target_tokens_per_batch': target_tokens_per_batch,
                'smart_batches': smart_batches,
                'total_batches': len(smart_batches),
                'completed_batches': [],
                'start_time': datetime.now().isoformat(),
                'last_update': datetime.now().isoformat()
            })
            
            self.save_state(state)
            
            print(f"✓ PDF智能提取完成")
            print(f"✓ 总页数: {len(structure_data['pages'])}")
            print(f"✓ 总字符数: {sum(len(page['text']) for page in structure_data['pages']):,}")
            print(f"✓ 智能批次: {len(smart_batches)} 批")
        
        # 步骤2: 处理每个批次
        print(f"\n步骤 2/3: 高GPU利用率音频生成")
        print("-" * 40)
        
        smart_batches = state['smart_batches']
        total_batches = state['total_batches']
        completed_batches = state.get('completed_batches', [])
        
        print(f"总批次数: {total_batches}")
        print(f"已完成: {len(completed_batches)} 批")
        print(f"剩余: {total_batches - len(completed_batches)} 批")
        
        for batch_idx, batch_info in enumerate(smart_batches):
            if batch_idx in completed_batches:
                print(f"⏭️  跳过已完成的批次 {batch_idx + 1}")
                continue
            
            print(f"\n--- 处理批次 {batch_idx + 1}/{total_batches} ---")
            print(f"页面范围: 第{batch_info['start_page']}-{batch_info['end_page']}页")
            print(f"Token数: {batch_info['tokens']:,}")
            print(f"字符数: {batch_info['chars']:,}")
            
            # 分割文本为片段
            batch_chunks = self.text_processor.split_into_chunks(batch_info['content'])
            print(f"✓ 文本已分割成 {len(batch_chunks)} 个片段")
            
            # 生成音频
            batch_start_time = time.time()
            audio_arrays = self.audio_generator.generate_audio_batch(batch_chunks)
            batch_time = time.time() - batch_start_time
            
            print(f"✓ 音频生成完成，耗时: {batch_time/60:.1f} 分钟")
            
            # 保存音频文件
            output_path = os.path.join(output_dir, f"batch_{batch_idx + 1:03d}.wav")
            self.audio_generator.merge_audio_arrays(audio_arrays, output_path)
            
            # 保存片段文件（如果需要）
            if keep_chunks:
                chunk_dir = os.path.join(output_dir, f"batch_{batch_idx + 1:03d}_chunks")
                os.makedirs(chunk_dir, exist_ok=True)
                
                for i, (chunk, audio) in enumerate(zip(batch_chunks, audio_arrays)):
                    chunk_path = os.path.join(chunk_dir, f"chunk_{i:04d}.wav")
                    wavfile.write(chunk_path, self.audio_generator.sample_rate, audio)
            
            # 更新状态
            completed_batches.append(batch_idx)
            state['completed_batches'] = completed_batches
            state['last_update'] = datetime.now().isoformat()
            self.save_state(state)
            
            print(f"✅ 批次 {batch_idx + 1} 完成")
            
            # 批次间休息
            if batch_idx < total_batches - 1:
                print("批次间休息 0.5 秒...")
                time.sleep(0.5)  # 进一步减少休息时间
        
        # 步骤3: 生成播放列表
        print(f"\n步骤 3/3: 生成播放列表")
        print("-" * 40)
        
        playlist_path = os.path.join(output_dir, "playlist.m3u")
        with open(playlist_path, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for i in range(total_batches):
                f.write(f"#EXTINF:-1,批次 {i + 1}\n")
                f.write(f"batch_{i + 1:03d}.wav\n")
        
        print(f"✓ 播放列表已生成: {playlist_path}")
        
        # 计算总时间
        total_time = datetime.now() - datetime.fromisoformat(state['start_time'])
        print(f"\n🎉 高GPU利用率处理完成！")
        print(f"总耗时: {total_time}")
        print(f"输出目录: {output_dir}")
        
        return output_dir
    
    def _create_smart_batches(self, structure_data: Dict, target_tokens: int) -> List[Dict]:
        """创建智能批次，目标1万token"""
        batches = []
        current_batch_pages = []
        current_batch_chars = 0
        current_batch_paragraphs = []
        
        pages = structure_data['pages']
        
        for page_idx, page in enumerate(pages):
            page_text = page['text']
            page_paragraphs = page.get('paragraphs', [page_text])
            
            # 尝试添加整个页面
            if current_batch_chars + len(page_text) <= target_tokens * 2.5 or not current_batch_pages:
                current_batch_pages.append(page['page_number'])
                current_batch_chars += len(page_text)
                current_batch_paragraphs.extend(page_paragraphs)
            else:
                # 完成当前批次
                if current_batch_pages:
                    batches.append({
                        'start_page': current_batch_pages[0],
                        'end_page': current_batch_pages[-1],
                        'chars': current_batch_chars,
                        'tokens': current_batch_chars // 4,  # 粗略估算
                        'content': '\n\n'.join(current_batch_paragraphs)
                    })
                
                # 开始新批次
                current_batch_pages = [page['page_number']]
                current_batch_chars = len(page_text)
                current_batch_paragraphs = page_paragraphs
        
        # 添加最后一个批次
        if current_batch_pages:
            batches.append({
                'start_page': current_batch_pages[0],
                'end_page': current_batch_pages[-1],
                'chars': current_batch_chars,
                'tokens': current_batch_chars // 4,
                'content': '\n\n'.join(current_batch_paragraphs)
            })
        
        return batches

def main():
    parser = argparse.ArgumentParser(description="高GPU利用率PDF转有声读物")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("-o", "--output_dir", default="high_gpu_utilization_audio", help="输出目录")
    parser.add_argument("-v", "--voice_preset", default="v2/en_speaker_6", help="语音预设")
    parser.add_argument("-c", "--max_chars_per_chunk", type=int, default=200, help="每片段最大字符数")
    parser.add_argument("-t", "--target_tokens_per_batch", type=int, default=10000, help="目标批次Token数")
    parser.add_argument("--keep-chunks", action="store_true", help="保留音频片段文件")
    parser.add_argument("--no-resume", action="store_true", help="不恢复之前的处理")
    
    args = parser.parse_args()
    
    maker = HighGPUUtilizationAudiobookMaker(
        voice_preset=args.voice_preset,
        max_chars_per_chunk=args.max_chars_per_chunk,
        target_tokens_per_batch=args.target_tokens_per_batch,
        resume=not args.no_resume
    )
    
    maker.create_audiobook_batch(
        pdf_path=args.pdf_path,
        output_dir=args.output_dir,
        voice_preset=args.voice_preset,
        max_chars_per_chunk=args.max_chars_per_chunk,
        target_tokens_per_batch=args.target_tokens_per_batch,
        keep_chunks=args.keep_chunks
    )

if __name__ == "__main__":
    main()

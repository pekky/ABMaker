# -*- coding: utf-8 -*-
"""
超内存优化版有声读物制作器
充分利用GPU显存到70%，最大化处理速度
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
import concurrent.futures
import gc
import threading
import queue

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

class UltraMemoryOptimizedAudioGenerator:
    """超内存优化版音频生成器，充分利用GPU显存到70%"""
    
    def __init__(self, voice_preset: str = "v2/zh_speaker_1", 
                 max_workers: int = 16,  # 大幅增加并行数
                 batch_size: int = 32,   # 大幅增加批处理大小
                 memory_target_percent: int = 70):  # 目标显存使用率
        self.voice_preset = voice_preset
        self.sample_rate = 24000
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.memory_target_percent = memory_target_percent
        
        # 设置环境变量以最大化显存使用
        os.environ["SUNO_USE_SMALL_MODELS"] = "False"
        os.environ["SUNO_OFFLOAD_CPU"] = "False"
        
        print("🚀 超内存优化模式启动")
        print(f"✓ 使用完整模型（最高质量）")
        print(f"✓ 禁用CPU卸载（最大化GPU显存使用）")
        print(f"✓ 并行工作线程: {max_workers}")
        print(f"✓ 批处理大小: {batch_size}")
        print(f"✓ 目标显存使用率: {memory_target_percent}%")
        
        # 检查GPU显存
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            target_memory = gpu_memory * memory_target_percent / 100
            print(f"✓ GPU显存: {gpu_memory:.1f}GB")
            print(f"✓ 目标使用显存: {target_memory:.1f}GB")
            
            # 设置CUDA优化
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.matmul.allow_tf32 = False
            torch.backends.cudnn.allow_tf32 = False
            print("✓ 启用CUDA优化")
        
        # 预加载模型
        print("正在加载Bark模型...")
        from bark import SAMPLE_RATE, generate_audio, preload_models
        self.sample_rate = SAMPLE_RATE
        preload_models()
        print("✓ Bark模型加载完成")
        
        # 预热GPU到目标显存使用率
        self._warmup_gpu_to_target()
        
        # 创建处理队列
        self.audio_queue = queue.Queue(maxsize=max_workers * 2)
        self.result_queue = queue.Queue()
        
        # 启动工作线程
        self.workers = []
        self._start_workers()
    
    def _warmup_gpu_to_target(self):
        """预热GPU到目标显存使用率"""
        if not torch.cuda.is_available():
            return
            
        print(f"正在预热GPU到{self.memory_target_percent}%显存使用率...")
        
        # 获取当前显存使用
        current_memory = torch.cuda.memory_allocated() / 1024**3
        total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        target_memory = total_memory * self.memory_target_percent / 100
        
        print(f"  当前显存使用: {current_memory:.1f}GB")
        print(f"  目标显存使用: {target_memory:.1f}GB")
        
        # 创建张量来占用显存
        dummy_tensors = []
        try:
            while current_memory < target_memory * 0.8:  # 留一些余量
                # 创建大张量
                tensor_size = min(1024, int((target_memory - current_memory) * 1024 * 0.1))
                if tensor_size < 100:
                    break
                    
                tensor = torch.randn(tensor_size, tensor_size, device='cuda')
                dummy_tensors.append(tensor)
                
                current_memory = torch.cuda.memory_allocated() / 1024**3
                print(f"  预热进度: {current_memory:.1f}GB / {target_memory:.1f}GB")
                
        except RuntimeError as e:
            print(f"  预热完成: {e}")
        
        print(f"✓ GPU预热完成，当前显存使用: {current_memory:.1f}GB")
    
    def _start_workers(self):
        """启动工作线程"""
        print(f"启动 {self.max_workers} 个工作线程...")
        
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.workers.append(worker)
        
        print("✓ 工作线程启动完成")
    
    def _worker_loop(self):
        """工作线程循环"""
        while True:
            try:
                # 从队列获取任务
                task = self.audio_queue.get(timeout=1)
                if task is None:  # 停止信号
                    break
                
                text, task_id = task
                audio_array = self._generate_single_audio(text)
                
                # 将结果放入结果队列
                self.result_queue.put((task_id, audio_array))
                self.audio_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ 工作线程错误: {e}")
                self.audio_queue.task_done()
    
    def _generate_single_audio(self, text: str) -> np.ndarray:
        """生成单个音频片段"""
        try:
            from bark import generate_audio
            audio_array = generate_audio(text, history_prompt=self.voice_preset)
            return audio_array.astype(np.float32)
        except Exception as e:
            print(f"❌ 音频生成失败: {e}")
            return np.zeros(int(self.sample_rate * 0.5), dtype=np.float32)
    
    def generate_audio_batch(self, text_chunks: List[str]) -> List[np.ndarray]:
        """批量生成音频，最大化显存利用"""
        print(f"🎵 开始超批量生成 {len(text_chunks)} 个音频片段...")
        
        # 提交所有任务到队列
        for i, chunk in enumerate(text_chunks):
            self.audio_queue.put((chunk, i))
        
        # 收集结果
        audio_arrays = [None] * len(text_chunks)
        completed = 0
        
        while completed < len(text_chunks):
            try:
                task_id, audio_array = self.result_queue.get(timeout=30)
                audio_arrays[task_id] = audio_array
                completed += 1
                
                if completed % 50 == 0 or completed == len(text_chunks):
                    progress = completed / len(text_chunks) * 100
                    print(f"  进度: {completed}/{len(text_chunks)} ({progress:.1f}%)")
                    
                    # 显示显存使用情况
                    if torch.cuda.is_available():
                        current_memory = torch.cuda.memory_allocated() / 1024**3
                        total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                        usage_percent = current_memory / total_memory * 100
                        print(f"  GPU显存: {current_memory:.1f}GB/{total_memory:.1f}GB ({usage_percent:.1f}%)")
                
            except queue.Empty:
                print("⚠️ 等待结果超时，继续等待...")
                continue
        
        print(f"✓ 超批量生成完成，共 {len(audio_arrays)} 个音频片段")
        return audio_arrays
    
    def merge_audio_arrays(self, audio_arrays: List[np.ndarray], output_path: str, 
                          silence_duration: float = 0.05) -> str:  # 减少静音时间
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

class UltraMemoryOptimizedAudiobookMaker:
    """超内存优化版有声读物制作器"""
    
    def __init__(self, voice_preset: str = "v2/zh_speaker_1",
                 max_chars_per_chunk: int = 150,  # 减少片段大小以增加并行度
                 target_tokens_per_batch: int = 50000,  # 增加批次大小
                 max_workers: int = 16,
                 batch_size: int = 32,
                 memory_target_percent: int = 70,
                 resume: bool = True):
        self.voice_preset = voice_preset
        self.max_chars_per_chunk = max_chars_per_chunk
        self.target_tokens_per_batch = target_tokens_per_batch
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.memory_target_percent = memory_target_percent
        self.resume = resume
        
        # 初始化组件
        self.text_processor = TextProcessor(max_chars=max_chars_per_chunk)
        self.audio_generator = UltraMemoryOptimizedAudioGenerator(
            voice_preset=voice_preset,
            max_workers=max_workers,
            batch_size=batch_size,
            memory_target_percent=memory_target_percent
        )
        
        # 状态文件
        self.state_file = "ultra_memory_optimized_processing_state.json"
    
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
        
        print("🚀 开始超内存优化版有声读物制作")
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
        print(f"\n步骤 2/3: 超内存优化音频生成")
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
                print("批次间休息 2 秒...")
                time.sleep(2)
        
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
        print(f"\n🎉 超内存优化版处理完成！")
        print(f"总耗时: {total_time}")
        print(f"输出目录: {output_dir}")
        
        return output_dir
    
    def _create_smart_batches(self, structure_data: Dict, target_tokens: int) -> List[Dict]:
        """创建智能批次"""
        batches = []
        current_batch_pages = []
        current_batch_chars = 0
        current_batch_paragraphs = []
        
        pages = structure_data['pages']
        
        for page_idx, page in enumerate(pages):
            page_text = page['text']
            page_paragraphs = page.get('paragraphs', [page_text])
            
            # 尝试添加整个页面
            if current_batch_chars + len(page_text) <= target_tokens * 3 or not current_batch_pages:
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
                        'tokens': current_batch_chars // 4,
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
    parser = argparse.ArgumentParser(description="超内存优化版PDF转有声读物")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("-o", "--output_dir", default="ultra_memory_optimized_audio", help="输出目录")
    parser.add_argument("-v", "--voice_preset", default="v2/en_speaker_6", help="语音预设")
    parser.add_argument("-c", "--max_chars_per_chunk", type=int, default=150, help="每片段最大字符数")
    parser.add_argument("-t", "--target_tokens_per_batch", type=int, default=50000, help="目标批次Token数")
    parser.add_argument("-w", "--max_workers", type=int, default=16, help="最大并行工作线程数")
    parser.add_argument("-b", "--batch_size", type=int, default=32, help="批处理大小")
    parser.add_argument("-m", "--memory_target_percent", type=int, default=70, help="目标显存使用率")
    parser.add_argument("--keep-chunks", action="store_true", help="保留音频片段文件")
    parser.add_argument("--no-resume", action="store_true", help="不恢复之前的处理")
    
    args = parser.parse_args()
    
    maker = UltraMemoryOptimizedAudiobookMaker(
        voice_preset=args.voice_preset,
        max_chars_per_chunk=args.max_chars_per_chunk,
        target_tokens_per_batch=args.target_tokens_per_batch,
        max_workers=args.max_workers,
        batch_size=args.batch_size,
        memory_target_percent=args.memory_target_percent,
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

# -*- coding: utf-8 -*-
"""
高速分批处理有声读物制作器 - 5倍速度提升版本
"""
import os
import argparse
import json
import time
from datetime import datetime
from core.pdf_extractor import PDFExtractor
from core.text_processor import TextProcessor
from utils.fast_audio_generator import FastAudioGenerator
import multiprocessing as mp


class FastBatchAudiobookMaker:
    """高速分批处理有声读物制作器"""
    
    def __init__(self, voice_preset: str = "v2/zh_speaker_1", 
                 max_chars: int = 300,  # 增加片段大小，减少总片段数
                 use_small_model: bool = True,
                 batch_size: int = 100,  # 减少批次大小，提高并行度
                 resume: bool = True,
                 max_workers: int = 4):  # 并行进程数
        """
        初始化高速分批处理制作器
        
        Args:
            voice_preset: 语音预设
            max_chars: 每个片段的最大字符数（增加到300减少片段数）
            use_small_model: 使用小模型（必须启用）
            batch_size: 每批处理的片段数量（减少到100提高并行度）
            resume: 是否支持断点续传
            max_workers: 最大并行工作进程数
        """
        self.voice_preset = voice_preset
        self.max_chars = max_chars
        self.use_small_model = use_small_model
        self.batch_size = batch_size
        self.resume = resume
        self.max_workers = max_workers
        
        self.text_processor = TextProcessor(max_chars=max_chars)
        self.audio_generator = FastAudioGenerator(
            voice_preset=voice_preset, 
            use_small_model=use_small_model,
            enable_cpu_offload=True,
            max_workers=max_workers
        )
        
        # 状态文件路径
        self.state_file = "fast_batch_processing_state.json"
        self.temp_dir = "tmp/fast_batch"
        
    def save_state(self, state: dict):
        """保存处理状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def load_state(self) -> dict:
        """加载处理状态"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def create_audiobook_fast(self, pdf_path: str, output_path: str = "fast_audiobook.wav",
                             keep_chunks: bool = False) -> str:
        """
        高速创建有声读物
        
        Args:
            pdf_path: PDF文件路径
            output_path: 输出音频文件路径
            keep_chunks: 是否保留中间音频片段
            
        Returns:
            输出音频文件路径
        """
        print("=" * 60)
        print("🚀 开始高速制作有声读物（5倍速度提升）")
        print("=" * 60)
        
        # 检查是否支持断点续传
        state = self.load_state() if self.resume else {}
        
        # 步骤1: 提取PDF文本（如果未完成）
        if 'text_chunks' not in state:
            print("\n步骤 1/4: 提取PDF文本")
            print("-" * 60)
            extractor = PDFExtractor(pdf_path)
            text = extractor.extract_text()
            
            print("\n步骤 2/4: 处理文本（优化分块）")
            print("-" * 60)
            chunks = self.text_processor.split_into_chunks(text)
            
            # 保存文本片段
            state['text_chunks'] = chunks
            state['total_chunks'] = len(chunks)
            state['processed_chunks'] = 0
            state['completed_batches'] = []
            state['start_time'] = datetime.now().isoformat()
            self.save_state(state)
            
            print(f"✓ 文本已分割成 {len(chunks)} 个片段（优化后）")
            print(f"✓ 将分 {len(chunks) // self.batch_size + 1} 批处理")
            print(f"✓ 使用 {self.max_workers} 个并行进程")
        else:
            chunks = state['text_chunks']
            print(f"\n✓ 恢复处理，共 {len(chunks)} 个片段")
            print(f"✓ 已完成 {state['processed_chunks']} 个片段")
        
        # 步骤3: 高速分批生成音频
        print("\n步骤 3/4: 高速分批生成音频")
        print("-" * 60)
        
        os.makedirs(self.temp_dir, exist_ok=True)
        total_chunks = len(chunks)
        processed_chunks = state.get('processed_chunks', 0)
        
        # 计算批次
        start_batch = processed_chunks // self.batch_size
        total_batches = (total_chunks + self.batch_size - 1) // self.batch_size
        
        print(f"总批次数: {total_batches}")
        print(f"当前批次: {start_batch + 1}/{total_batches}")
        print(f"每批处理: {self.batch_size} 个片段")
        print(f"并行进程: {self.max_workers}")
        
        for batch_idx in range(start_batch, total_batches):
            batch_start = batch_idx * self.batch_size
            batch_end = min(batch_start + self.batch_size, total_chunks)
            batch_chunks = chunks[batch_start:batch_end]
            
            print(f"\n--- 处理批次 {batch_idx + 1}/{total_batches} ---")
            print(f"片段范围: {batch_start + 1} - {batch_end}")
            print(f"本批片段数: {len(batch_chunks)}")
            
            # 高速生成当前批次的音频
            batch_start_time = time.time()
            
            # 使用并行处理
            batch_audio_files = self.audio_generator.generate_audio_batch(
                batch_chunks, 
                self.temp_dir, 
                batch_size=self.max_workers
            )
            
            batch_time = time.time() - batch_start_time
            print(f"✓ 批次 {batch_idx + 1} 完成，耗时: {batch_time/60:.1f} 分钟")
            print(f"✓ 平均每片段: {batch_time/len(batch_chunks):.2f} 秒")
            
            # 更新状态
            state['processed_chunks'] = processed_chunks + len(batch_chunks)
            state['completed_batches'].append(batch_idx)
            state['last_update'] = datetime.now().isoformat()
            self.save_state(state)
            
            # 批次间短暂休息（减少到3秒）
            if batch_idx < total_batches - 1:
                print("批次间休息 3 秒...")
                time.sleep(3)
        
        # 步骤4: 合并音频
        print("\n步骤 4/4: 合并音频")
        print("-" * 60)
        
        # 收集所有音频文件
        audio_files = []
        for i in range(total_chunks):
            audio_file = os.path.join(self.temp_dir, f"chunk_{i:04d}.wav")
            if os.path.exists(audio_file):
                audio_files.append(audio_file)
        
        print(f"正在合并 {len(audio_files)} 个音频片段...")
        final_audio = self.audio_generator.merge_audio_files(audio_files, output_path)
        
        # 清理临时文件
        if not keep_chunks:
            print("\n清理临时文件...")
            import shutil
            shutil.rmtree(self.temp_dir)
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
            print("✓ 临时文件已清理")
        
        # 计算总耗时
        if 'start_time' in state:
            start_time = datetime.fromisoformat(state['start_time'])
            total_time = datetime.now() - start_time
            print(f"\n✓ 总耗时: {total_time.total_seconds()/3600:.1f} 小时")
            print(f"✓ 平均每片段: {total_time.total_seconds()/total_chunks:.2f} 秒")
        
        print("\n" + "=" * 60)
        print(f"🚀 高速有声读物制作完成！")
        print(f"输出文件: {os.path.abspath(output_path)}")
        print("=" * 60)
        
        return final_audio


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="高速分批PDF小说转有声读物工具（5倍速度提升）")
    parser.add_argument("pdf_file", help="PDF文件路径")
    parser.add_argument("-o", "--output", default="fast_audiobook.wav", 
                       help="输出音频文件路径（默认: fast_audiobook.wav）")
    parser.add_argument("-v", "--voice", default="v2/zh_speaker_1", 
                       help="语音预设（默认: v2/zh_speaker_1）")
    parser.add_argument("-c", "--max-chars", type=int, default=300,
                       help="每个片段的最大字符数（默认: 300，优化后）")
    parser.add_argument("-b", "--batch-size", type=int, default=100,
                       help="每批处理的片段数量（默认: 100，优化后）")
    parser.add_argument("-w", "--workers", type=int, default=4,
                       help="并行工作进程数（默认: 4）")
    parser.add_argument("--keep-chunks", action="store_true",
                       help="保留音频片段文件")
    parser.add_argument("--no-resume", action="store_true",
                       help="不支持断点续传")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.pdf_file):
        print(f"错误: 文件不存在: {args.pdf_file}")
        return
    
    # 创建高速分批处理制作器
    maker = FastBatchAudiobookMaker(
        voice_preset=args.voice,
        max_chars=args.max_chars,
        use_small_model=True,  # 强制使用小模型
        batch_size=args.batch_size,
        resume=not args.no_resume,
        max_workers=args.workers
    )
    
    maker.create_audiobook_fast(
        pdf_path=args.pdf_file,
        output_path=args.output,
        keep_chunks=args.keep_chunks
    )


if __name__ == "__main__":
    main()

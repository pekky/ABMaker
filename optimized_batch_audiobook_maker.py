# -*- coding: utf-8 -*-
"""
4万字符批次处理有声读物制作器 - 优化批次大小
"""
import os
import argparse
import json
import time
from datetime import datetime
from pdf_extractor import PDFExtractor
from text_processor import TextProcessor
from high_quality_audio_generator import HighQualityAudioGenerator


class OptimizedBatchAudiobookMaker:
    """4万字符批次处理有声读物制作器"""
    
    def __init__(self, voice_preset: str = "v2/zh_speaker_1", 
                 max_chars: int = 200,  # 保持原始片段大小
                 target_batch_chars: int = 40000,  # 目标批次字符数
                 resume: bool = True,
                 max_workers: int = 2):
        """
        初始化4万字符批次处理制作器
        
        Args:
            voice_preset: 语音预设
            max_chars: 每个片段的最大字符数
            target_batch_chars: 目标批次字符数（4万字符）
            resume: 是否支持断点续传
            max_workers: 最大并行工作进程数
        """
        self.voice_preset = voice_preset
        self.max_chars = max_chars
        self.target_batch_chars = target_batch_chars
        self.resume = resume
        self.max_workers = max_workers
        
        self.text_processor = TextProcessor(max_chars=max_chars)
        self.audio_generator = HighQualityAudioGenerator(
            voice_preset=voice_preset, 
            max_workers=max_workers,
            enable_memory_optimization=True
        )
        
        # 状态文件路径
        self.state_file = "optimized_batch_processing_state.json"
        self.temp_dir = "optimized_temp_audio_chunks"
        
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
    
    def create_batches_by_chars(self, chunks: list) -> list:
        """
        按字符数创建批次
        
        Args:
            chunks: 文本片段列表
            
        Returns:
            批次列表
        """
        batches = []
        current_batch = []
        current_chars = 0
        
        for chunk in chunks:
            chunk_chars = len(chunk)
            
            # 如果添加当前片段会超过目标字符数，且当前批次不为空
            if current_chars + chunk_chars > self.target_batch_chars and current_batch:
                batches.append(current_batch)
                current_batch = [chunk]
                current_chars = chunk_chars
            else:
                current_batch.append(chunk)
                current_chars += chunk_chars
        
        # 添加最后一个批次
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def create_audiobook_optimized(self, pdf_path: str, output_path: str = "optimized_audiobook.wav",
                                  keep_chunks: bool = False) -> str:
        """
        4万字符批次创建有声读物
        
        Args:
            pdf_path: PDF文件路径
            output_path: 输出音频文件路径
            keep_chunks: 是否保留中间音频片段
            
        Returns:
            输出音频文件路径
        """
        print("=" * 60)
        print(f"📚 开始4万字符批次制作有声读物")
        print("=" * 60)
        
        # 检查是否支持断点续传
        state = self.load_state() if self.resume else {}
        
        # 步骤1: 提取PDF文本（如果未完成）
        if 'text_chunks' not in state:
            print("\n步骤 1/4: 提取PDF文本")
            print("-" * 60)
            extractor = PDFExtractor(pdf_path)
            text = extractor.extract_text()
            
            print("\n步骤 2/4: 处理文本（按4万字符分批）")
            print("-" * 60)
            chunks = self.text_processor.split_into_chunks(text)
            
            # 按字符数创建批次
            batches = self.create_batches_by_chars(chunks)
            
            # 保存状态
            state['text_chunks'] = chunks
            state['batches'] = batches
            state['total_chunks'] = len(chunks)
            state['total_batches'] = len(batches)
            state['processed_chunks'] = 0
            state['completed_batches'] = []
            state['start_time'] = datetime.now().isoformat()
            self.save_state(state)
            
            print(f"✓ 文本已分割成 {len(chunks)} 个片段")
            print(f"✓ 按4万字符分批，共 {len(batches)} 批")
            print(f"✓ 平均每批: {sum(len(batch) for batch in batches) / len(batches):.0f} 个片段")
            print(f"✓ 平均每批: {sum(sum(len(chunk) for chunk in batch) for batch in batches) / len(batches):.0f} 字符")
        else:
            chunks = state['text_chunks']
            batches = state['batches']
            print(f"\n✓ 恢复处理，共 {len(chunks)} 个片段")
            print(f"✓ 共 {len(batches)} 批")
            print(f"✓ 已完成 {state['processed_chunks']} 个片段")
        
        # 步骤3: 4万字符批次生成音频
        print("\n步骤 3/4: 4万字符批次生成音频")
        print("-" * 60)
        
        os.makedirs(self.temp_dir, exist_ok=True)
        total_batches = len(batches)
        processed_chunks = state.get('processed_chunks', 0)
        
        print(f"总批次数: {total_batches}")
        print(f"并行进程: {self.max_workers}（保证质量）")
        
        for batch_idx, batch_chunks in enumerate(batches):
            batch_chars = sum(len(chunk) for chunk in batch_chunks)
            
            print(f"\n--- 处理批次 {batch_idx + 1}/{total_batches} ---")
            print(f"片段数: {len(batch_chunks)}")
            print(f"字符数: {batch_chars:,}字符 ({batch_chars/10000:.1f}万字)")
            
            # 生成当前批次的音频
            batch_start_time = time.time()
            
            # 使用高质量并行处理
            batch_audio_files = self.audio_generator.generate_audio_batch(
                batch_chunks, 
                self.temp_dir, 
                batch_size=5  # 小批次保证质量
            )
            
            batch_time = time.time() - batch_start_time
            print(f"✓ 批次 {batch_idx + 1} 完成，耗时: {batch_time/60:.1f} 分钟")
            print(f"✓ 平均每片段: {batch_time/len(batch_chunks):.2f} 秒")
            print(f"✓ 处理速度: {batch_chars/batch_time:.0f} 字符/秒")
            
            # 更新状态
            state['processed_chunks'] = processed_chunks + len(batch_chunks)
            state['completed_batches'].append(batch_idx)
            state['last_update'] = datetime.now().isoformat()
            self.save_state(state)
            
            # 批次间休息
            if batch_idx < total_batches - 1:
                print("批次间休息 5 秒（保证质量）...")
                time.sleep(5)
        
        # 步骤4: 合并音频
        print("\n步骤 4/4: 合并音频")
        print("-" * 60)
        
        # 收集所有音频文件
        audio_files = []
        for i in range(len(chunks)):
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
            print(f"✓ 平均每片段: {total_time.total_seconds()/len(chunks):.2f} 秒")
            print(f"✓ 总处理速度: {sum(len(chunk) for chunk in chunks)/total_time.total_seconds():.0f} 字符/秒")
        
        print("\n" + "=" * 60)
        print(f"📚 4万字符批次有声读物制作完成！")
        print(f"输出文件: {os.path.abspath(output_path)}")
        print("=" * 60)
        
        return final_audio


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="4万字符批次PDF小说转有声读物工具")
    parser.add_argument("pdf_file", help="PDF文件路径")
    parser.add_argument("-o", "--output", default="optimized_audiobook.wav", 
                       help="输出音频文件路径（默认: optimized_audiobook.wav）")
    parser.add_argument("-v", "--voice", default="v2/zh_speaker_1", 
                       help="语音预设（默认: v2/zh_speaker_1）")
    parser.add_argument("-c", "--max-chars", type=int, default=200,
                       help="每个片段的最大字符数（默认: 200）")
    parser.add_argument("-t", "--target-chars", type=int, default=40000,
                       help="目标批次字符数（默认: 40000）")
    parser.add_argument("-w", "--workers", type=int, default=2,
                       help="并行工作进程数（默认: 2，保证质量）")
    parser.add_argument("--keep-chunks", action="store_true",
                       help="保留音频片段文件")
    parser.add_argument("--no-resume", action="store_true",
                       help="不支持断点续传")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.pdf_file):
        print(f"错误: 文件不存在: {args.pdf_file}")
        return
    
    # 创建4万字符批次处理制作器
    maker = OptimizedBatchAudiobookMaker(
        voice_preset=args.voice,
        max_chars=args.max_chars,
        target_batch_chars=args.target_chars,
        resume=not args.no_resume,
        max_workers=args.workers
    )
    
    maker.create_audiobook_optimized(
        pdf_path=args.pdf_file,
        output_path=args.output,
        keep_chunks=args.keep_chunks
    )


if __name__ == "__main__":
    main()

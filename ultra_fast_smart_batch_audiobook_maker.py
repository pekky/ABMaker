# -*- coding: utf-8 -*-
"""
超高速智能批次处理有声读物制作器 - 10倍速度提升，保持音质
"""
import os
import argparse
import json
import time
from datetime import datetime
from smart_pdf_extractor import SmartPDFExtractor
from text_processor import TextProcessor
from ultra_fast_audio_generator import UltraFastAudioGenerator


class UltraFastSmartBatchAudiobookMaker:
    """超高速智能批次处理有声读物制作器"""
    
    def __init__(self, voice_preset: str = "v2/zh_speaker_1", 
                 max_chars: int = 200,  # 片段大小
                 target_batch_chars: int = 40000,  # 目标批次字符数
                 resume: bool = True,
                 max_workers: int = 8):  # 增加到8个并行进程
        """
        初始化超高速智能批次处理制作器
        
        Args:
            voice_preset: 语音预设
            max_chars: 每个片段的最大字符数
            target_batch_chars: 目标批次字符数（4万字符）
            resume: 是否支持断点续传
            max_workers: 最大并行工作进程数（8个）
        """
        self.voice_preset = voice_preset
        self.max_chars = max_chars
        self.target_batch_chars = target_batch_chars
        self.resume = resume
        self.max_workers = max_workers
        
        self.text_processor = TextProcessor(max_chars=max_chars)
        self.audio_generator = UltraFastAudioGenerator(
            voice_preset=voice_preset, 
            max_workers=max_workers,
            enable_model_caching=True,
            enable_batch_processing=True,
            enable_memory_pool=True
        )
        
        # 状态文件路径
        self.state_file = "ultra_fast_batch_processing_state.json"
        self.temp_dir = "ultra_fast_temp_audio_chunks"
        
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
    
    def create_audiobook_ultra_fast(self, pdf_path: str, output_path: str = "ultra_fast_audiobook.wav",
                                   keep_chunks: bool = False) -> str:
        """
        超高速智能批次创建有声读物
        
        Args:
            pdf_path: PDF文件路径
            output_path: 输出音频文件路径
            keep_chunks: 是否保留中间音频片段
            
        Returns:
            输出音频文件路径
        """
        print("=" * 60)
        print(f"🚀 开始超高速智能批次制作有声读物（10倍速度提升）")
        print("=" * 60)
        
        # 检查是否支持断点续传
        state = self.load_state() if self.resume else {}
        
        # 步骤1: 智能提取PDF文本（如果未完成）
        if 'batches' not in state:
            print("\n步骤 1/4: 智能提取PDF文本")
            print("-" * 60)
            
            extractor = SmartPDFExtractor(pdf_path)
            batches = extractor.create_smart_batches(self.target_batch_chars)
            
            # 保存状态
            state['batches'] = batches
            state['total_batches'] = len(batches)
            state['processed_batches'] = 0
            state['completed_batches'] = []
            state['start_time'] = datetime.now().isoformat()
            state['has_page_numbers'] = extractor.has_page_numbers
            self.save_state(state)
            
            print(f"✓ 智能批次创建完成，共 {len(batches)} 批")
            print(f"✓ 页码检测: {'有' if extractor.has_page_numbers else '无'}")
            print(f"✓ 平均每批: {sum(batch['char_count'] for batch in batches) / len(batches):.0f} 字符")
            print(f"✓ 并行进程: {self.max_workers}个")
        else:
            batches = state['batches']
            print(f"\n✓ 恢复处理，共 {len(batches)} 批")
            print(f"✓ 已完成 {state['processed_batches']} 批")
        
        # 步骤2: 超高速分批生成音频
        print("\n步骤 2/4: 超高速分批生成音频")
        print("-" * 60)
        
        os.makedirs(self.temp_dir, exist_ok=True)
        total_batches = len(batches)
        processed_batches = state.get('processed_batches', 0)
        
        print(f"总批次数: {total_batches}")
        print(f"并行进程: {self.max_workers}个（超高速）")
        
        # 重新创建提取器以获取批次文本
        extractor = SmartPDFExtractor(pdf_path)
        
        for batch_idx in range(processed_batches, total_batches):
            batch = batches[batch_idx]
            batch_text = extractor.get_batch_text(batch)
            
            # 将批次文本分割成片段
            batch_chunks = self.text_processor.split_into_chunks(batch_text)
            
            print(f"\n--- 处理批次 {batch_idx + 1}/{total_batches} ---")
            if state.get('has_page_numbers', False):
                print(f"页面范围: 第{batch['start_page']}-{batch['end_page']}页")
            else:
                print(f"页面范围: 第{batch['start_page']}-{batch['end_page']}页")
                print(f"段落数: {len(batch['paragraphs'])}个段落")
            print(f"字符数: {batch['char_count']:,}字符 ({batch['char_count']/10000:.1f}万字)")
            print(f"片段数: {len(batch_chunks)}个片段")
            
            # 超高速生成当前批次的音频
            batch_start_time = time.time()
            
            # 使用超高速并行处理
            batch_audio_files = self.audio_generator.generate_audio_batch_ultra_fast(
                batch_chunks, 
                self.temp_dir, 
                batch_size=20  # 增加批次大小
            )
            
            batch_time = time.time() - batch_start_time
            print(f"✓ 批次 {batch_idx + 1} 完成，耗时: {batch_time/60:.1f} 分钟")
            print(f"✓ 平均每片段: {batch_time/len(batch_chunks):.2f} 秒")
            print(f"✓ 处理速度: {len(batch_chunks)/batch_time:.1f} it/s")
            print(f"✓ 字符处理速度: {batch['char_count']/batch_time:.0f} 字符/秒")
            
            # 更新状态
            state['processed_batches'] = batch_idx + 1
            state['completed_batches'].append(batch_idx)
            state['last_update'] = datetime.now().isoformat()
            self.save_state(state)
            
            # 批次间短暂休息（减少到2秒）
            if batch_idx < total_batches - 1:
                print("批次间休息 2 秒（超高速模式）...")
                time.sleep(2)
        
        # 步骤3: 合并音频
        print("\n步骤 3/4: 合并音频")
        print("-" * 60)
        
        # 收集所有音频文件
        audio_files = []
        chunk_idx = 0
        for batch_idx, batch in enumerate(batches):
            batch_text = extractor.get_batch_text(batch)
            batch_chunks = self.text_processor.split_into_chunks(batch_text)
            
            for chunk in batch_chunks:
                audio_file = os.path.join(self.temp_dir, f"chunk_{chunk_idx:04d}.wav")
                if os.path.exists(audio_file):
                    audio_files.append(audio_file)
                chunk_idx += 1
        
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
            total_chars = sum(batch['char_count'] for batch in batches)
            total_chunks = sum(len(self.text_processor.split_into_chunks(extractor.get_batch_text(batch))) for batch in batches)
            
            print(f"\n✓ 总耗时: {total_time.total_seconds()/3600:.1f} 小时")
            print(f"✓ 总字符数: {total_chars:,}字符")
            print(f"✓ 总片段数: {total_chunks:,}个片段")
            print(f"✓ 平均每片段: {total_time.total_seconds()/total_chunks:.2f} 秒")
            print(f"✓ 总处理速度: {total_chunks/total_time.total_seconds():.1f} it/s")
            print(f"✓ 字符处理速度: {total_chars/total_time.total_seconds():.0f} 字符/秒")
            print(f"✓ 速度提升: 约 {total_chunks/total_time.total_seconds()/50:.1f}倍")
        
        print("\n" + "=" * 60)
        print(f"🚀 超高速智能批次有声读物制作完成！")
        print(f"输出文件: {os.path.abspath(output_path)}")
        print("=" * 60)
        
        return final_audio


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="超高速智能批次PDF小说转有声读物工具（10倍速度提升）")
    parser.add_argument("pdf_file", help="PDF文件路径")
    parser.add_argument("-o", "--output", default="ultra_fast_audiobook.wav", 
                       help="输出音频文件路径（默认: ultra_fast_audiobook.wav）")
    parser.add_argument("-v", "--voice", default="v2/zh_speaker_1", 
                       help="语音预设（默认: v2/zh_speaker_1）")
    parser.add_argument("-c", "--max-chars", type=int, default=200,
                       help="每个片段的最大字符数（默认: 200）")
    parser.add_argument("-t", "--target-chars", type=int, default=40000,
                       help="目标批次字符数（默认: 40000）")
    parser.add_argument("-w", "--workers", type=int, default=8,
                       help="并行工作进程数（默认: 8，超高速）")
    parser.add_argument("--keep-chunks", action="store_true",
                       help="保留音频片段文件")
    parser.add_argument("--no-resume", action="store_true",
                       help="不支持断点续传")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.pdf_file):
        print(f"错误: 文件不存在: {args.pdf_file}")
        return
    
    # 创建超高速智能批次处理制作器
    maker = UltraFastSmartBatchAudiobookMaker(
        voice_preset=args.voice,
        max_chars=args.max_chars,
        target_batch_chars=args.target_chars,
        resume=not args.no_resume,
        max_workers=args.workers
    )
    
    maker.create_audiobook_ultra_fast(
        pdf_path=args.pdf_file,
        output_path=args.output,
        keep_chunks=args.keep_chunks
    )


if __name__ == "__main__":
    main()

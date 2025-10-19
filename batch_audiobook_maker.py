# -*- coding: utf-8 -*-
"""
分批处理有声读物制作器 - 降低长时间处理的风险
"""
import os
import argparse
import json
import time
from datetime import datetime
from pdf_extractor import PDFExtractor
from text_processor import TextProcessor
from audio_generator import AudioGenerator


class BatchAudiobookMaker:
    """分批处理有声读物制作器"""
    
    def __init__(self, voice_preset: str = "v2/zh_speaker_1", 
                 max_chars: int = 200, use_small_model: bool = False,
                 batch_size: int = 500, resume: bool = True):
        """
        初始化分批处理制作器
        
        Args:
            voice_preset: 语音预设
            max_chars: 每个片段的最大字符数
            use_small_model: 是否使用小模型
            batch_size: 每批处理的片段数量
            resume: 是否支持断点续传
        """
        self.voice_preset = voice_preset
        self.max_chars = max_chars
        self.use_small_model = use_small_model
        self.batch_size = batch_size
        self.resume = resume
        
        self.text_processor = TextProcessor(max_chars=max_chars)
        self.audio_generator = AudioGenerator(voice_preset=voice_preset, 
                                             use_small_model=use_small_model)
        
        # 状态文件路径
        self.state_file = "batch_processing_state.json"
        self.temp_dir = "temp_audio_chunks"
        
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
    
    def create_audiobook_batch(self, pdf_path: str, output_path: str = "audiobook.wav",
                               keep_chunks: bool = False) -> str:
        """
        分批创建有声读物
        
        Args:
            pdf_path: PDF文件路径
            output_path: 输出音频文件路径
            keep_chunks: 是否保留中间音频片段
            
        Returns:
            输出音频文件路径
        """
        print("=" * 60)
        print("开始分批制作有声读物")
        print("=" * 60)
        
        # 检查是否支持断点续传
        state = self.load_state() if self.resume else {}
        
        # 步骤1: 提取PDF文本（如果未完成）
        if 'text_chunks' not in state:
            print("\n步骤 1/4: 提取PDF文本")
            print("-" * 60)
            extractor = PDFExtractor(pdf_path)
            text = extractor.extract_text()
            
            print("\n步骤 2/4: 处理文本")
            print("-" * 60)
            chunks = self.text_processor.split_into_chunks(text)
            
            # 保存文本片段
            state['text_chunks'] = chunks
            state['total_chunks'] = len(chunks)
            state['processed_chunks'] = 0
            state['completed_batches'] = []
            state['start_time'] = datetime.now().isoformat()
            self.save_state(state)
            
            print(f"✓ 文本已分割成 {len(chunks)} 个片段")
            print(f"✓ 将分 {len(chunks) // self.batch_size + 1} 批处理")
        else:
            chunks = state['text_chunks']
            print(f"\n✓ 恢复处理，共 {len(chunks)} 个片段")
            print(f"✓ 已完成 {state['processed_chunks']} 个片段")
        
        # 步骤3: 分批生成音频
        print("\n步骤 3/4: 分批生成音频")
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
        
        for batch_idx in range(start_batch, total_batches):
            batch_start = batch_idx * self.batch_size
            batch_end = min(batch_start + self.batch_size, total_chunks)
            batch_chunks = chunks[batch_start:batch_end]
            
            print(f"\n--- 处理批次 {batch_idx + 1}/{total_batches} ---")
            print(f"片段范围: {batch_start + 1} - {batch_end}")
            print(f"本批片段数: {len(batch_chunks)}")
            
            # 生成当前批次的音频
            batch_start_time = time.time()
            batch_audio_files = []
            
            for i, chunk in enumerate(batch_chunks):
                chunk_idx = batch_start + i
                audio_array = self.audio_generator.generate_single_audio(chunk)
                
                # 保存音频文件
                output_path_chunk = os.path.join(self.temp_dir, f"chunk_{chunk_idx:04d}.wav")
                from scipy.io import wavfile
                wavfile.write(output_path_chunk, self.audio_generator.sample_rate, audio_array)
                batch_audio_files.append(output_path_chunk)
                
                # 更新进度
                processed_chunks += 1
                if (i + 1) % 50 == 0 or i == len(batch_chunks) - 1:
                    progress = processed_chunks / total_chunks * 100
                    print(f"  进度: {processed_chunks}/{total_chunks} ({progress:.1f}%)")
            
            batch_time = time.time() - batch_start_time
            print(f"✓ 批次 {batch_idx + 1} 完成，耗时: {batch_time/60:.1f} 分钟")
            
            # 更新状态
            state['processed_chunks'] = processed_chunks
            state['completed_batches'].append(batch_idx)
            state['last_update'] = datetime.now().isoformat()
            self.save_state(state)
            
            # 批次间休息（可选）
            if batch_idx < total_batches - 1:
                print("批次间休息 10 秒...")
                time.sleep(10)
        
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
        
        print("\n" + "=" * 60)
        print(f"✓ 有声读物制作完成！")
        print(f"输出文件: {os.path.abspath(output_path)}")
        print("=" * 60)
        
        return final_audio


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="分批PDF小说转有声读物工具")
    parser.add_argument("pdf_file", help="PDF文件路径")
    parser.add_argument("-o", "--output", default="audiobook.wav", 
                       help="输出音频文件路径（默认: audiobook.wav）")
    parser.add_argument("-v", "--voice", default="v2/zh_speaker_1", 
                       help="语音预设（默认: v2/zh_speaker_1）")
    parser.add_argument("-c", "--max-chars", type=int, default=200,
                       help="每个片段的最大字符数（默认: 200）")
    parser.add_argument("-b", "--batch-size", type=int, default=500,
                       help="每批处理的片段数量（默认: 500）")
    parser.add_argument("--small-model", action="store_true",
                       help="使用小模型（节省显存）")
    parser.add_argument("--keep-chunks", action="store_true",
                       help="保留音频片段文件")
    parser.add_argument("--no-resume", action="store_true",
                       help="不支持断点续传")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.pdf_file):
        print(f"错误: 文件不存在: {args.pdf_file}")
        return
    
    # 创建分批处理制作器
    maker = BatchAudiobookMaker(
        voice_preset=args.voice,
        max_chars=args.max_chars,
        use_small_model=args.small_model,
        batch_size=args.batch_size,
        resume=not args.no_resume
    )
    
    maker.create_audiobook_batch(
        pdf_path=args.pdf_file,
        output_path=args.output,
        keep_chunks=args.keep_chunks
    )


if __name__ == "__main__":
    main()

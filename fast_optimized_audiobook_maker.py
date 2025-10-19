# -*- coding: utf-8 -*-
"""
高速优化版有声读物制作器 - 使用小模型和优化设置
"""
import os
import argparse
import json
import time
from datetime import datetime
from typing import List
from smart_pdf_extractor import SmartPDFExtractor
from text_processor import TextProcessor
from audio_generator import AudioGenerator


class FastOptimizedAudiobookMaker:
    """高速优化版有声读物制作器"""
    
    def __init__(self, voice_preset: str = "v2/en_speaker_6", 
                 max_chars: int = 300,  # 增加片段大小减少片段数量
                 target_tokens: int = 40000,
                 resume: bool = True):
        """
        初始化高速优化版制作器
        
        Args:
            voice_preset: 语音预设
            max_chars: 每个片段的最大字符数（增加到300）
            target_tokens: 目标token数（4万）
            resume: 是否支持断点续传
        """
        self.voice_preset = voice_preset
        self.max_chars = max_chars
        self.target_tokens = target_tokens
        self.resume = resume
        
        self.text_processor = TextProcessor(max_chars=max_chars)
        # 使用小模型提升速度
        self.audio_generator = AudioGenerator(voice_preset=voice_preset, use_small_model=True)
        
        # 状态文件路径
        self.state_file = "fast_optimized_processing_state.json"
        self.output_dir = "fast_optimized_audio_files"
        
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
    
    def estimate_tokens(self, text: str) -> int:
        """估算文本的token数量"""
        import re
        
        # 统计中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        
        # 统计英文单词
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        
        # 估算token数
        estimated_tokens = chinese_chars + int(english_words * 1.3)
        
        return estimated_tokens
    
    def create_token_batches(self, structure_data: dict) -> List[dict]:
        """按4万token创建批次，保证页面或段落完整性"""
        pages = structure_data['pages']
        has_page_numbers = structure_data['has_page_numbers']
        
        batches = []
        current_batch = {
            'pages': [],
            'paragraphs': [],
            'text': '',
            'token_count': 0,
            'char_count': 0,
            'start_page': None,
            'end_page': None,
            'start_para': None,
            'end_para': None
        }
        
        print(f"\n开始创建4万token批次（优化版）...")
        print(f"目标token数: {self.target_tokens:,}")
        print(f"每片段最大字符数: {self.max_chars}")
        print(f"页码检测: {'有' if has_page_numbers else '无'}")
        
        for page_idx, page_data in enumerate(pages):
            page_text = page_data['text']
            page_tokens = self.estimate_tokens(page_text)
            page_chars = len(page_text)
            
            # 如果添加当前页会超过目标token数，且当前批次不为空
            if current_batch['token_count'] + page_tokens > self.target_tokens and current_batch['pages']:
                # 完成当前批次
                current_batch['end_page'] = current_batch['pages'][-1]['page_num']
                batches.append(current_batch.copy())
                
                # 开始新批次
                current_batch = {
                    'pages': [page_data],
                    'paragraphs': page_data['paragraphs'].copy(),
                    'text': page_text,
                    'token_count': page_tokens,
                    'char_count': page_chars,
                    'start_page': page_data['page_num'],
                    'end_page': None,
                    'start_para': 0,
                    'end_para': len(page_data['paragraphs']) - 1
                }
            else:
                # 添加当前页到批次
                if not current_batch['pages']:
                    current_batch['start_page'] = page_data['page_num']
                    current_batch['start_para'] = 0
                
                current_batch['pages'].append(page_data)
                current_batch['paragraphs'].extend(page_data['paragraphs'])
                current_batch['text'] += '\n\n' + page_text if current_batch['text'] else page_text
                current_batch['token_count'] += page_tokens
                current_batch['char_count'] += page_chars
                current_batch['end_page'] = page_data['page_num']
                current_batch['end_para'] = len(current_batch['paragraphs']) - 1
        
        # 添加最后一个批次
        if current_batch['pages']:
            batches.append(current_batch)
        
        print(f"✓ 4万token批次创建完成，共 {len(batches)} 批")
        
        # 打印批次信息
        for i, batch in enumerate(batches, 1):
            if has_page_numbers:
                print(f"批次 {i}: 第{batch['start_page']}-{batch['end_page']}页, "
                      f"{batch['token_count']:,}tokens, {batch['char_count']:,}字符")
            else:
                print(f"批次 {i}: 第{batch['start_page']}-{batch['end_page']}页, "
                      f"{len(batch['paragraphs'])}个段落, "
                      f"{batch['token_count']:,}tokens, {batch['char_count']:,}字符")
        
        return batches
    
    def create_audiobook_fast(self, pdf_path: str, output_dir: str = "fast_optimized_audio_files",
                            keep_chunks: bool = False) -> List[str]:
        """高速创建有声读物"""
        print("=" * 60)
        print(f"🚀 开始高速优化版有声读物制作")
        print("=" * 60)
        
        # 检查是否支持断点续传
        state = self.load_state() if self.resume else {}
        
        # 步骤1: 智能提取PDF文本
        if 'batches' not in state:
            print("\n步骤 1/3: 智能提取PDF文本")
            print("-" * 60)
            
            extractor = SmartPDFExtractor(pdf_path)
            structure_data = extractor.extract_text_with_structure()
            batches = self.create_token_batches(structure_data)
            
            # 保存状态
            state['batches'] = batches
            state['total_batches'] = len(batches)
            state['processed_batches'] = 0
            state['completed_batches'] = []
            state['start_time'] = datetime.now().isoformat()
            state['has_page_numbers'] = structure_data['has_page_numbers']
            self.save_state(state)
            
            print(f"✓ 4万token批次创建完成，共 {len(batches)} 批")
            print(f"✓ 页码检测: {'有' if structure_data['has_page_numbers'] else '无'}")
            print(f"✓ 平均每批: {sum(batch['token_count'] for batch in batches) / len(batches):.0f} tokens")
        else:
            batches = state['batches']
            print(f"\n✓ 恢复处理，共 {len(batches)} 批")
            print(f"✓ 已完成 {state['processed_batches']} 批")
        
        # 步骤2: 按批次生成音频文件
        print("\n步骤 2/3: 高速生成音频文件")
        print("-" * 60)
        
        os.makedirs(output_dir, exist_ok=True)
        total_batches = len(batches)
        processed_batches = state.get('processed_batches', 0)
        
        print(f"总批次数: {total_batches}")
        print(f"处理模式: 小模型高速模式")
        print(f"每片段字符数: {self.max_chars}")
        print(f"输出目录: {output_dir}")
        
        audio_files = []
        
        for batch_idx in range(processed_batches, total_batches):
            batch = batches[batch_idx]
            
            print(f"\n--- 处理批次 {batch_idx + 1}/{total_batches} ---")
            if state.get('has_page_numbers', False):
                print(f"页面范围: 第{batch['start_page']}-{batch['end_page']}页")
            else:
                print(f"页面范围: 第{batch['start_page']}-{batch['end_page']}页")
                print(f"段落数: {len(batch['paragraphs'])}个段落")
            print(f"Token数: {batch['token_count']:,}tokens")
            print(f"字符数: {batch['char_count']:,}字符")
            
            # 将批次文本分割成片段（更大的片段）
            batch_chunks = self.text_processor.split_into_chunks(batch['text'])
            print(f"片段数: {len(batch_chunks)}个片段")
            
            # 生成当前批次的音频（高速模式）
            batch_start_time = time.time()
            
            # 创建临时目录
            temp_chunk_dir = os.path.join(output_dir, f"batch_{batch_idx + 1:03d}_chunks")
            os.makedirs(temp_chunk_dir, exist_ok=True)
            
            # 逐个生成音频片段
            batch_audio_files = []
            for i, chunk in enumerate(batch_chunks):
                try:
                    # 生成单个音频片段
                    audio_array = self.audio_generator.generate_single_audio(chunk)
                    
                    # 保存音频片段
                    chunk_path = os.path.join(temp_chunk_dir, f"chunk_{i:04d}.wav")
                    from scipy.io import wavfile
                    wavfile.write(chunk_path, self.audio_generator.sample_rate, audio_array)
                    batch_audio_files.append(chunk_path)
                    
                    # 显示进度
                    if (i + 1) % 20 == 0 or i == len(batch_chunks) - 1:
                        progress = (i + 1) / len(batch_chunks) * 100
                        print(f"  进度: {i + 1}/{len(batch_chunks)} ({progress:.1f}%)")
                        
                except Exception as e:
                    print(f"  错误: 生成片段 {i} 失败 - {e}")
                    # 创建一个静音片段作为占位符
                    chunk_path = os.path.join(temp_chunk_dir, f"chunk_{i:04d}.wav")
                    from scipy.io import wavfile
                    import numpy as np
                    silence = np.zeros(int(0.5 * self.audio_generator.sample_rate), dtype=np.float32)
                    wavfile.write(chunk_path, self.audio_generator.sample_rate, silence)
                    batch_audio_files.append(chunk_path)
            
            # 合并当前批次的音频
            batch_output_path = os.path.join(output_dir, f"batch_{batch_idx + 1:03d}.wav")
            merged_audio = self.audio_generator.merge_audio_files(
                batch_audio_files, 
                batch_output_path,
                silence_duration=0.1  # 减少静音时间
            )
            
            batch_time = time.time() - batch_start_time
            print(f"✓ 批次 {batch_idx + 1} 完成，耗时: {batch_time/60:.1f} 分钟")
            print(f"✓ 平均每片段: {batch_time/len(batch_chunks):.2f} 秒")
            print(f"✓ 处理速度: {len(batch_chunks)/batch_time:.1f} it/s")
            print(f"✓ 输出文件: {batch_output_path}")
            
            # 保存音频文件路径
            if merged_audio:
                audio_files.append(batch_output_path)
            
            # 更新状态
            state['processed_batches'] = batch_idx + 1
            state['completed_batches'].append(batch_idx)
            state['last_update'] = datetime.now().isoformat()
            self.save_state(state)
            
            # 清理临时片段文件
            if not keep_chunks and batch_audio_files:
                import shutil
                if os.path.exists(temp_chunk_dir):
                    shutil.rmtree(temp_chunk_dir)
            
            # 批次间休息（减少休息时间）
            if batch_idx < total_batches - 1:
                print("批次间休息 1 秒...")
                time.sleep(1)
        
        # 步骤3: 生成批次列表文件
        print("\n步骤 3/3: 生成批次列表文件")
        print("-" * 60)
        
        # 生成批次信息文件
        batch_info = {
            'total_batches': total_batches,
            'audio_files': audio_files,
            'batches': []
        }
        
        for i, batch in enumerate(batches):
            batch_info['batches'].append({
                'batch_number': i + 1,
                'audio_file': audio_files[i] if i < len(audio_files) else None,
                'page_range': f"{batch['start_page']}-{batch['end_page']}",
                'token_count': batch['token_count'],
                'char_count': batch['char_count'],
                'paragraph_count': len(batch['paragraphs'])
            })
        
        # 保存批次信息
        info_file = os.path.join(output_dir, "batch_info.json")
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(batch_info, f, ensure_ascii=False, indent=2)
        
        # 生成播放列表文件
        playlist_file = os.path.join(output_dir, "playlist.m3u")
        with open(playlist_file, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for i, audio_file in enumerate(audio_files, 1):
                f.write(f"#EXTINF:-1,批次 {i}\n")
                f.write(f"{os.path.basename(audio_file)}\n")
        
        # 清理状态文件
        if not keep_chunks and os.path.exists(self.state_file):
            os.remove(self.state_file)
        
        # 计算总耗时
        if 'start_time' in state:
            start_time = datetime.fromisoformat(state['start_time'])
            total_time = datetime.now() - start_time
            total_tokens = sum(batch['token_count'] for batch in batches)
            total_chunks = sum(len(self.text_processor.split_into_chunks(batch['text'])) for batch in batches)
            
            print(f"\n✓ 总耗时: {total_time.total_seconds()/3600:.1f} 小时")
            print(f"✓ 总Token数: {total_tokens:,}tokens")
            print(f"✓ 总片段数: {total_chunks:,}个片段")
            print(f"✓ 平均每片段: {total_time.total_seconds()/total_chunks:.2f} 秒")
            print(f"✓ 总处理速度: {total_chunks/total_time.total_seconds():.1f} it/s")
        
        print("\n" + "=" * 60)
        print(f"🚀 高速优化版有声读物制作完成！")
        print(f"输出目录: {os.path.abspath(output_dir)}")
        print(f"音频文件: {len(audio_files)}个")
        print(f"批次信息: {info_file}")
        print(f"播放列表: {playlist_file}")
        print("=" * 60)
        
        return audio_files


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="高速优化版PDF小说转有声读物工具")
    parser.add_argument("pdf_file", help="PDF文件路径")
    parser.add_argument("-o", "--output-dir", default="fast_optimized_audio_files", 
                       help="输出目录（默认: fast_optimized_audio_files）")
    parser.add_argument("-v", "--voice", default="v2/en_speaker_6", 
                       help="语音预设（默认: v2/en_speaker_6）")
    parser.add_argument("-c", "--max-chars", type=int, default=300,
                       help="每个片段的最大字符数（默认: 300）")
    parser.add_argument("-t", "--target-tokens", type=int, default=40000,
                       help="目标token数（默认: 40000）")
    parser.add_argument("--keep-chunks", action="store_true",
                       help="保留音频片段文件")
    parser.add_argument("--no-resume", action="store_true",
                       help="不支持断点续传")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.pdf_file):
        print(f"错误: 文件不存在: {args.pdf_file}")
        return
    
    # 创建高速优化版制作器
    maker = FastOptimizedAudiobookMaker(
        voice_preset=args.voice,
        max_chars=args.max_chars,
        target_tokens=args.target_tokens,
        resume=not args.no_resume
    )
    
    maker.create_audiobook_fast(
        pdf_path=args.pdf_file,
        output_dir=args.output_dir,
        keep_chunks=args.keep_chunks
    )


if __name__ == "__main__":
    main()

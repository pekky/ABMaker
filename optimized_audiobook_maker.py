#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版有声读物制作器启动脚本
使用优化后的参数和音频处理流程
"""
import os
import sys
import argparse
import logging
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.audiobook_maker import AudiobookMaker
from core.audiobook_maker_batch import AudiobookMaker as BatchAudiobookMaker
from utils.document_selector import DocumentSelector

def create_timestamped_tmp_dir():
    """创建带时间戳的临时目录"""
    now = datetime.now()
    # 格式: chunks_yymmdd_hhmm
    timestamp = now.strftime("chunks_%y%m%d_%H%M")
    tmp_dir = os.path.join("tmp", timestamp)
    
    # 确保tmp目录存在
    os.makedirs("tmp", exist_ok=True)
    
    # 创建时间戳目录
    os.makedirs(tmp_dir, exist_ok=True)
    
    print(f"📁 创建临时目录: {tmp_dir}")
    return tmp_dir

def get_pdf_basename(pdf_path):
    """获取PDF文件的基础名称（不含扩展名）"""
    return os.path.splitext(os.path.basename(pdf_path))[0]

def create_batch_output_filename(pdf_basename, batch_index):
    """创建batch音频输出文件名"""
    now = datetime.now()
    # 格式: pdf文件名_yymmdd_batchnumber.mp3
    timestamp = now.strftime("%y%m%d")
    return f"{pdf_basename}_{timestamp}_{batch_index:03d}.mp3"

def setup_logging(pdf_basename):
    """设置日志文件"""
    # 确保tmp目录存在
    os.makedirs("tmp", exist_ok=True)
    
    # 创建日志文件名：pdf名_yymmdd.log
    now = datetime.now()
    log_filename = f"{pdf_basename}_{now.strftime('%y%m%d')}.log"
    log_path = os.path.join("tmp", log_filename)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)  # 同时输出到控制台
        ]
    )
    
    print(f"📝 日志文件: {log_path}")
    return log_path

def select_language_interactive():
    """交互式选择语言"""
    print("\n🌍 请选择文本语言 / Select Text Language:")
    print("  1. English (英语) [默认]")
    print("  2. 中文 (Chinese)")
    print("  3. 日本語 (Japanese)")
    print()
    
    choice = input("请输入选项 (1-3，直接回车选择默认): ").strip()
    
    language_map = {
        "1": "en",
        "2": "zh",
        "3": "ja",
        "": "en",  # 默认英语
    }
    
    selected = language_map.get(choice, "en")
    language_names = {"en": "English", "zh": "中文", "ja": "日本語"}
    print(f"✓ 已选择: {language_names[selected]}\n")
    
    return selected

def select_voice_interactive(language="en"):
    """交互式选择语音"""
    # 定义可用的语音选项
    voice_options = {
        "en": {
            "1": ("v2/en_speaker_0", "英语男声 (Male) [默认]"),
            "2": ("v2/en_speaker_1", "英语女声 (Female)"),
            "3": ("v2/en_speaker_2", "英语男声2 (Male 2)"),
            "4": ("v2/en_speaker_3", "英语女声2 (Female 2)"),
            "5": ("v2/en_speaker_4", "英语男声3 (Male 3)"),
            "6": ("v2/en_speaker_5", "英语女声3 (Female 3)"),
            "7": ("v2/en_speaker_6", "英语男声4 (Male 4)"),
            "8": ("v2/en_speaker_7", "英语女声4 (Female 4)"),
            "9": ("v2/en_speaker_8", "英语男声5 (Male 5)"),
        },
        "zh": {
            "1": ("v2/zh_speaker_0", "中文男声 (Male)"),
            "2": ("v2/zh_speaker_1", "中文女声 (Female) [默认]"),
            "3": ("v2/zh_speaker_2", "中文男声2 (Male 2)"),
            "4": ("v2/zh_speaker_3", "中文女声2 (Female 2)"),
            "5": ("v2/zh_speaker_4", "中文男声3 (Male 3)"),
            "6": ("v2/zh_speaker_5", "中文女声3 (Female 3)"),
            "7": ("v2/zh_speaker_6", "中文男声4 (Male 4)"),
            "8": ("v2/zh_speaker_7", "中文女声4 (Female 4)"),
            "9": ("v2/zh_speaker_8", "中文男声5 (Male 5)"),
        },
        "ja": {
            "1": ("v2/ja_speaker_0", "日语男声 (Male)"),
            "2": ("v2/ja_speaker_1", "日语女声 (Female) [默认]"),
            "3": ("v2/ja_speaker_2", "日语男声2 (Male 2)"),
            "4": ("v2/ja_speaker_3", "日语女声2 (Female 2)"),
            "5": ("v2/ja_speaker_4", "日语男声3 (Male 3)"),
            "6": ("v2/ja_speaker_5", "日语女声3 (Female 3)"),
            "7": ("v2/ja_speaker_6", "日语男声4 (Male 4)"),
            "8": ("v2/ja_speaker_7", "日语女声4 (Female 4)"),
        }
    }
    
    options = voice_options.get(language, voice_options["en"])
    
    print(f"🎤 请选择语音 / Select Voice:")
    for key, (voice_id, description) in options.items():
        print(f"  {key}. {description}")
    print()
    
    choice = input("请输入选项 (直接回车选择默认): ").strip()
    
    # 默认选择：英语男声 (v2/en_speaker_0)
    default_voice = "v2/en_speaker_0" if language == "en" else options.get("1", ("v2/en_speaker_0", ""))[0]
    
    if choice == "":
        selected_voice = default_voice
    else:
        selected_voice = options.get(choice, (default_voice, ""))[0]
    
    # 显示选择的语音
    selected_desc = next((desc for key, (vid, desc) in options.items() if vid == selected_voice), "")
    print(f"✓ 已选择: {selected_desc}\n")
    
    return selected_voice

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="优化版PDF小说转有声读物工具")
    parser.add_argument("pdf_file", nargs='?', help="PDF文件路径（可选，不提供则从docs目录选择）")
    parser.add_argument("-o", "--output", default="audiobook_optimized.mp3", 
                       help="输出音频文件路径（默认: audiobook_optimized.mp3）")
    parser.add_argument("-l", "--language", default=None,
                       help="文本语言 (en/zh/ja，如不提供，将交互式选择，默认: en)")
    parser.add_argument("-v", "--voice", default=None, 
                       help="语音预设（如不提供，将交互式选择，默认: v2/en_speaker_0）")
    parser.add_argument("-c", "--max-chars", type=int, default=700,
                       help="每个片段的最大字符数（默认: 700，范围600-800）")
    parser.add_argument("--small-model", action="store_true",
                       help="使用小模型（节省显存）")
    parser.add_argument("--keep-chunks", action="store_true",
                       help="保留音频片段文件")
    parser.add_argument("--batch-mode", action="store_true", default=True,
                       help="启用批量处理模式（每15000个token分成一个batch,默认启用）")
    parser.add_argument("--batch-size", type=int, default=15000,
                       help="每个batch的token数量（默认: 15000）")
    parser.add_argument("--docs-dir", default="docs",
                       help="文档目录路径（默认: docs）")
    
    args = parser.parse_args()
    
    # 交互式选择语言（如果未通过参数指定）
    if args.language is None:
        language = select_language_interactive()
    else:
        language = args.language
    
    # 交互式选择语音（如果未通过参数指定）
    if args.voice is None:
        voice = select_voice_interactive(language)
    else:
        voice = args.voice
    
    # 更新 args
    args.language = language
    args.voice = voice
    
    print("🎵 优化版PDF小说转有声读物工具")
    print("=" * 60)
    print("✨ 优化特性:")
    print("  • 600-800字符智能分段，优先句号分割")
    print("  • 优化Bark参数，减少噪声和爆破音")
    print("  • 24kHz采样率，LUFS归一化")
    print("  • 轻度去噪和去齿音处理")
    print("  • 3-8ms交叉淡化，避免爆音")
    print("  • 韵律注释，自然停顿")
    if args.batch_mode:
        print(f"  • 📦 批量处理模式：每{args.batch_size}个token分成一个batch")
        print("  • 每个batch处理完生成一个单独的音频文件")
    print("=" * 60)
    
    # 如果没有提供PDF文件路径，则从docs目录选择
    if not args.pdf_file:
        selector = DocumentSelector(args.docs_dir)
        pdf_path = selector.select_document()
        
        if not pdf_path:
            print("❌ 未选择文档，程序退出")
            return
    else:
        pdf_path = args.pdf_file
        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            print("❌ 错误: 文件不存在: " + pdf_path)
            return
    
    # 获取PDF基础名称
    pdf_basename = get_pdf_basename(pdf_path)
    
    # 设置日志文件
    log_path = setup_logging(pdf_basename)
    logging.info(f"开始处理PDF文件: {pdf_path}")
    
    # 创建时间戳临时目录
    timestamped_tmp_dir = create_timestamped_tmp_dir()
    
    # 根据模式选择制作器
    if args.batch_mode:
        print(f"\n📦 启用批量处理模式")
        print(f"Batch大小: {args.batch_size} tokens")
        print(f"📁 临时目录: {timestamped_tmp_dir}")
        print(f"📄 PDF基础名称: {pdf_basename}")
        
        # 创建批量处理制作器
        maker = BatchAudiobookMaker(
            voice_preset=args.voice,
            max_chars=args.max_chars,
            use_small_model=args.small_model
        )
        
        # 设置临时目录
        maker.temp_dir = timestamped_tmp_dir
        
        # 使用批量处理模式
        maker.create_audiobook(
            pdf_path=pdf_path,
            output_path=args.output,
            keep_chunks=args.keep_chunks
        )
    else:
        # 创建标准优化版有声读物制作器
        maker = AudiobookMaker(
            voice_preset=args.voice,
            max_chars=args.max_chars,
            use_small_model=args.small_model
        )
        
        # 设置临时目录
        maker.temp_dir = timestamped_tmp_dir
        
        maker.create_audiobook(
            pdf_path=pdf_path,
            output_path=args.output,
            keep_chunks=args.keep_chunks
        )

if __name__ == "__main__":
    main()


# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
有声读物制作器 - 主程序
"""
import os
import sys
import argparse

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.pdf_extractor import PDFExtractor
from core.text_processor import TextProcessor
from core.audio_generator import AudioGenerator
from core.batch_processor import BatchProcessor
from utils.document_selector import DocumentSelector
from utils.config_manager import ConfigManager


class AudiobookMaker:
    """有声读物制作器"""
    
    def __init__(self, voice_preset=None, max_chars=None, use_small_model=None, 
                 config_manager=None, preset=None, temp_dir=None):
        """
        初始化有声读物制作器
        
        Args:
            voice_preset: 语音预设（可选，优先使用配置）
            max_chars: 每个片段的最大字符数（可选，优先使用配置）
            use_small_model: 是否使用小模型（可选，优先使用配置）
            config_manager: 配置管理器实例
            preset: 预设名称（如'high_quality', 'fast', 'balanced'）
            temp_dir: 临时目录路径
        """
        self.config_manager = config_manager or ConfigManager()
        self.temp_dir = temp_dir or "tmp"
        
        # 应用预设
        if preset:
            self.config_manager.apply_preset(preset)
        
        # 创建组件
        self.text_processor = TextProcessor(max_chars=max_chars, config_manager=self.config_manager)
        self.audio_generator = AudioGenerator(
            voice_preset=voice_preset,
            use_small_model=use_small_model,
            config_manager=self.config_manager
        )
        self.batch_processor = BatchProcessor(config_manager=self.config_manager)
    
    def create_audiobook(self, pdf_path, output_path="audiobook.wav",
                        keep_chunks=False):
        """
        从PDF文件创建有声读物
        
        Args:
            pdf_path: PDF文件路径
            output_path: 输出音频文件路径
            keep_chunks: 是否保留中间音频片段
            
        Returns:
            输出音频文件路径
        """
        print("=" * 60)
        print("开始制作有声读物")
        print("=" * 60)
        
        # 1. 提取PDF文本
        print("\n步骤 1/4: 提取PDF文本")
        print("-" * 60)
        extractor = PDFExtractor(pdf_path)
        text = extractor.extract_text()
        
        # 2. 分割文本
        print("\n步骤 2/4: 处理文本")
        print("-" * 60)
        chunks = self.text_processor.split_into_chunks(text)
        
        # 显示前几个片段作为预览
        print("\n文本片段预览（前3个）:")
        for i, chunk in enumerate(chunks[:3]):
            if len(chunk) > 50:
                print("  片段 " + str(i+1) + ": " + chunk[:50] + "...")
            else:
                print("  片段 " + str(i+1) + ": " + chunk)
        
        # 3. 生成音频片段
        print("\n步骤 3/4: 生成音频")
        print("-" * 60)
        temp_dir = self.temp_dir
        audio_files = self.audio_generator.generate_audiobook(chunks, output_dir=temp_dir)
        
        # 4. 合并音频
        print("\n步骤 4/4: 合并音频")
        print("-" * 60)
        final_audio = self.audio_generator.merge_audio_files(audio_files, output_path)
        
        # 清理临时文件
        if not keep_chunks:
            print("\n清理临时文件...")
            import shutil
            shutil.rmtree(temp_dir)
            print("✓ 临时文件已清理")
        
        print("\n" + "=" * 60)
        print("✓ 有声读物制作完成！")
        print("输出文件: " + os.path.abspath(output_path))
        print("=" * 60)
        
        return final_audio


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="PDF小说转有声读物工具")
    parser.add_argument("pdf_file", nargs='?', help="PDF文件路径（可选，不提供则从docs目录选择）")
    parser.add_argument("-o", "--output", default="audiobook.wav", 
                       help="输出音频文件路径（默认: audiobook.wav）")
    parser.add_argument("-v", "--voice", default="v2/en_speaker_0", 
                       help="语音预设（默认: v2/en_speaker_0）")
    parser.add_argument("-c", "--max-chars", type=int, default=700,
                       help="每个片段的最大字符数（默认: 700，范围600-800）")
    parser.add_argument("--small-model", action="store_true",
                       help="使用小模型（节省显存）")
    parser.add_argument("--keep-chunks", action="store_true",
                       help="保留音频片段文件")
    parser.add_argument("--preset", choices=["high_quality", "fast", "balanced", "conservative"],
                       help="使用预设配置（high_quality/fast/balanced/conservative）")
    
    args = parser.parse_args()
    
    # 如果没有提供PDF文件路径，则从docs目录选择
    if not args.pdf_file:
        print("📚 PDF小说转有声读物工具")
        print("=" * 50)
        
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
    
    # 创建有声读物
    maker = AudiobookMaker(
        voice_preset=args.voice,
        max_chars=args.max_chars,
        use_small_model=args.small_model,
        preset=args.preset
    )
    
    maker.create_audiobook(
        pdf_path=pdf_path,
        output_path=args.output,
        keep_chunks=args.keep_chunks
    )


if __name__ == "__main__":
    main()



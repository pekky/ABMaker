"""
有声读物制作器 - 主程序
"""
import os
import argparse
from pdf_extractor import PDFExtractor
from text_processor import TextProcessor
from audio_generator import AudioGenerator


class AudiobookMaker:
    """有声读物制作器"""
    
    def __init__(self, voice_preset: str = "v2/zh_speaker_1", 
                 max_chars: int = 200, use_small_model: bool = False):
        """
        初始化有声读物制作器
        
        Args:
            voice_preset: 语音预设
            max_chars: 每个片段的最大字符数
            use_small_model: 是否使用小模型
        """
        self.text_processor = TextProcessor(max_chars=max_chars)
        self.audio_generator = AudioGenerator(voice_preset=voice_preset, 
                                             use_small_model=use_small_model)
    
    def create_audiobook(self, pdf_path: str, output_path: str = "audiobook.wav",
                        keep_chunks: bool = False) -> str:
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
            print(f"  片段 {i+1}: {chunk[:50]}..." if len(chunk) > 50 else f"  片段 {i+1}: {chunk}")
        
        # 3. 生成音频片段
        print("\n步骤 3/4: 生成音频")
        print("-" * 60)
        temp_dir = "temp_audio_chunks"
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
        print(f"✓ 有声读物制作完成！")
        print(f"输出文件: {os.path.abspath(output_path)}")
        print("=" * 60)
        
        return final_audio


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="PDF小说转有声读物工具")
    parser.add_argument("pdf_file", help="PDF文件路径")
    parser.add_argument("-o", "--output", default="audiobook.wav", 
                       help="输出音频文件路径（默认: audiobook.wav）")
    parser.add_argument("-v", "--voice", default="v2/zh_speaker_1", 
                       help="语音预设（默认: v2/zh_speaker_1）")
    parser.add_argument("-c", "--max-chars", type=int, default=200,
                       help="每个片段的最大字符数（默认: 200）")
    parser.add_argument("--small-model", action="store_true",
                       help="使用小模型（节省显存）")
    parser.add_argument("--keep-chunks", action="store_true",
                       help="保留音频片段文件")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.pdf_file):
        print(f"错误: 文件不存在: {args.pdf_file}")
        return
    
    # 创建有声读物
    maker = AudiobookMaker(
        voice_preset=args.voice,
        max_chars=args.max_chars,
        use_small_model=args.small_model
    )
    
    maker.create_audiobook(
        pdf_path=args.pdf_file,
        output_path=args.output,
        keep_chunks=args.keep_chunks
    )


if __name__ == "__main__":
    main()



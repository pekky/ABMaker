# -*- coding: utf-8 -*-
"""
有声读物制作器 - 支持批量处理
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
    """有声读物制作器 - 支持批量处理"""
    
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
        从PDF文件创建有声读物（支持批量处理）
        
        Args:
            pdf_path: PDF文件路径
            output_path: 输出文件路径
            keep_chunks: 是否保留音频片段文件
            
        Returns:
            生成的音频文件路径列表
        """
        print("=" * 60)
        print("开始制作有声读物")
        print("=" * 60)
        
        # 步骤1: 提取PDF文本
        print("\n步骤 1/5: 提取PDF文本")
        print("-" * 60)
        pdf_extractor = PDFExtractor(pdf_path)
        full_text = pdf_extractor.extract_text()
        
        if not full_text.strip():
            print("❌ 错误: 无法从PDF中提取文本")
            return []
        
        # 检查是否启用批量处理
        batch_config = self.config_manager.get_batch_config()
        enable_batch = batch_config.get("enable_batch_processing", True)
        
        if enable_batch and len(full_text) > batch_config.get("batch_size_chars", 15000):
            return self._create_audiobook_batch(full_text, output_path, keep_chunks, pdf_path)
        else:
            return self._create_audiobook_single(full_text, output_path, keep_chunks)
    
    def _create_audiobook_single(self, text, output_path, keep_chunks):
        """创建单个有声读物文件"""
        # 步骤2: 处理文本
        print("\n步骤 2/4: 处理文本")
        print("-" * 60)
        text_chunks = self.text_processor.split_into_chunks(text)
        
        # 显示前几个片段作为预览
        print("\n文本片段预览（前3个）:")
        for i, chunk in enumerate(text_chunks[:3]):
            if len(chunk) > 50:
                print("  片段 " + str(i+1) + ": " + chunk[:50] + "...")
            else:
                print("  片段 " + str(i+1) + ": " + chunk)
        
        # 步骤3: 生成音频
        print("\n步骤 3/4: 生成音频")
        print("-" * 60)
        audio_files = self.audio_generator.generate_audiobook(text_chunks, output_dir=self.temp_dir)
        
        # 步骤4: 合并音频
        print("\n步骤 4/4: 合并音频")
        print("-" * 60)
        final_audio = self.audio_generator.merge_audio_files(audio_files, output_path)
        
        # 清理临时文件
        if not keep_chunks:
            self._cleanup_temp_files(audio_files)
        
        print(f"\n✅ 有声读物制作完成: {output_path}")
        return [output_path]
    
    def _create_audiobook_batch(self, text, output_path, keep_chunks, pdf_path):
        """创建批量有声读物文件"""
        print(f"\n📦 启用批量处理模式")
        print(f"文本长度: {len(text)} 字符")
        
        # 步骤2: 分割成batch
        print("\n步骤 2/6: 分割成batch")
        print("-" * 60)
        batches = self.batch_processor.split_into_batches(text)
        
        # 记录batch数量到日志
        import logging
        logging.info(f"文本已分割成 {len(batches)} 个batch")
        print(f"📊 总共分割成 {len(batches)} 个batch")
        
        batch_outputs = []
        # 从 PDF 文件路径提取文件名作为 base_name
        original_name = os.path.splitext(os.path.basename(pdf_path))[0]
        base_name = self._truncate_filename(original_name)
        
        if original_name != base_name:
            print(f"📝 原始 PDF 文件名: {original_name}")
            print(f"📝 使用截断后的文件名: {base_name}")
        else:
            print(f"📝 使用 PDF 文件名: {base_name}")
        
        # 步骤3-5: 处理每个batch
        for i, batch_text in enumerate(batches):
            print(f"\n步骤 3-5/6: 处理Batch {i+1}/{len(batches)}")
            print("-" * 60)
            
            # 处理文本
            text_chunks = self.text_processor.split_into_chunks(batch_text)
            
            # 生成音频
            batch_temp_dir = os.path.join(self.temp_dir, f"batch_{i}")
            audio_files = self.audio_generator.generate_audiobook(text_chunks, output_dir=batch_temp_dir)
            
            # 合并音频 - 使用新的输出格式
            batch_output = self._get_batch_output_path(base_name, i)
            final_audio = self.audio_generator.merge_audio_files(audio_files, batch_output)
            batch_outputs.append(batch_output)
            
            # 清理临时文件
            if not keep_chunks:
                self._cleanup_temp_files(audio_files)
            
            print(f"✅ Batch {i+1} 完成: {batch_output}")
        
        # 步骤6: 合并所有batch（可选）
        batch_config = self.config_manager.get_batch_config()
        if batch_config.get("create_final_merge", True):
            print(f"\n步骤 6/6: 合并所有batch")
            print("-" * 60)
            final_output = self.batch_processor.get_final_output_path(base_name)
            self._merge_batch_files(batch_outputs, final_output)
            batch_outputs.append(final_output)
            print(f"✅ 最终合并完成: {final_output}")
        
        print(f"\n🎉 批量有声读物制作完成，共生成 {len(batch_outputs)} 个文件")
        return batch_outputs
    
    def _truncate_filename(self, filename, max_length=None):
        """
        智能截断文件名到指定长度
        
        Args:
            filename: 原始文件名
            max_length: 最大长度（默认从配置读取）
        
        Returns:
            截断后的文件名
        
        策略:
        1. 如果已经够短，不截断
        2. 尝试在分隔符处截断（保留更有意义的部分）
        3. 如果没有合适的分隔符，直接截断
        """
        # 从配置获取最大长度
        if max_length is None:
            output_config = self.config_manager.config.get("OUTPUT_CONFIG", {})
            max_length = output_config.get("max_filename_length", 20)
        
        # 如果文件名已经足够短，直接返回
        if len(filename) <= max_length:
            return filename
        
        # 获取截断策略
        output_config = self.config_manager.config.get("OUTPUT_CONFIG", {})
        strategy = output_config.get("filename_truncate_strategy", "separator")
        
        if strategy == "separator":
            # 策略1: 在分隔符处截断
            separators = ['-', '_', ' ', '.', '—']
            best_cut = None
            
            for sep in separators:
                # 在前max_length个字符中查找所有分隔符位置
                positions = [i for i, c in enumerate(filename[:max_length]) if c == sep]
                if positions:
                    # 找到最后一个分隔符位置
                    last_pos = max(positions)
                    # 确保至少保留60%的长度
                    if last_pos >= max_length * 0.6:
                        best_cut = last_pos
                        break
            
            # 如果找到合适的分隔符位置
            if best_cut and best_cut >= 10:  # 确保不会太短
                truncated = filename[:best_cut].rstrip('-_ ')
                print(f"📏 文件名截断: '{filename}' → '{truncated}' ({len(filename)} → {len(truncated)} 字符)")
                return truncated
        
        # 策略2: 直接截断（如果没有找到合适的分隔符或使用direct策略）
        truncated = filename[:max_length].rstrip('-_ ')
        print(f"📏 文件名截断: '{filename}' → '{truncated}' ({len(filename)} → {len(truncated)} 字符)")
        return truncated
    
    def _get_batch_output_path(self, base_name, batch_index):
        """获取batch输出文件路径（新格式）"""
        from datetime import datetime
        
        # 确保输出目录存在
        output_dir = "output/audio"
        os.makedirs(output_dir, exist_ok=True)
        
        # 格式: pdf文件名_yymmdd_batchnumber.mp3
        now = datetime.now()
        timestamp = now.strftime("%y%m%d")
        filename = f"{base_name}_{timestamp}_{batch_index+1:03d}.mp3"
        
        return os.path.join(output_dir, filename)
    
    def _merge_batch_files(self, batch_files, output_path):
        """合并多个batch文件"""
        if not batch_files:
            return
        
        print(f"正在合并 {len(batch_files)} 个batch文件...")
        
        # 使用audio_generator的合并功能
        self.audio_generator.merge_audio_files(batch_files, output_path)
    
    def _cleanup_temp_files(self, audio_files):
        """清理临时文件"""
        print("\n清理临时文件...")
        for audio_file in audio_files:
            if os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except Exception as e:
                    print(f"警告: 无法删除临时文件 {audio_file}: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="ABMaker - 有声读物制作器")
    parser.add_argument("pdf_file", nargs="?", help="PDF文件路径")
    parser.add_argument("--output", "-o", default="audiobook.wav",
                       help="输出音频文件路径")
    parser.add_argument("--voice", "-v", default="v2/en_speaker_0",
                       help="语音预设")
    parser.add_argument("--max-chars", type=int, default=700,
                       help="每个片段的最大字符数（默认: 700，范围600-800）")
    parser.add_argument("--small-model", action="store_true",
                       help="使用小模型（节省显存）")
    parser.add_argument("--keep-chunks", action="store_true",
                       help="保留音频片段文件")
    parser.add_argument("--preset", choices=["high_quality", "fast", "balanced", "conservative"],
                       help="使用预设配置（high_quality/fast/balanced/conservative）")
    parser.add_argument("--docs-dir", default="docs",
                       help="文档目录路径（默认: docs）")
    
    args = parser.parse_args()
    
    # 如果没有提供PDF文件路径，则从docs目录选择
    if not args.pdf_file:
        print("📚 从文档库选择PDF文件")
        print("=" * 50)
        
        selector = DocumentSelector(args.docs_dir)
        pdf_files = selector.list_pdf_files()
        
        if not pdf_files:
            print("❌ 错误: 在 " + args.docs_dir + " 目录中没有找到PDF文件")
            return
        
        print("可用的PDF文件:")
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"  {i}. {pdf_file}")
        
        try:
            choice = int(input("\n请选择文件编号: ")) - 1
            if 0 <= choice < len(pdf_files):
                pdf_path = os.path.join(args.docs_dir, pdf_files[choice])
            else:
                print("❌ 错误: 无效的选择")
                return
        except ValueError:
            print("❌ 错误: 请输入有效的数字")
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


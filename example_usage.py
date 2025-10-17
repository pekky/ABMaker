"""
使用示例 - 展示如何使用各个模块
"""

# ==================== 示例 1: 完整流程（推荐） ====================
def example_full_workflow():
    """完整的有声读物生成流程"""
    from audiobook_maker import AudiobookMaker
    
    # 创建制作器
    maker = AudiobookMaker(
        voice_preset="v2/zh_speaker_1",  # 中文语音
        max_chars=200,  # 每段200字符
        use_small_model=False  # 使用完整模型
    )
    
    # 生成有声读物
    maker.create_audiobook(
        pdf_path="your_novel.pdf",
        output_path="audiobook.wav",
        keep_chunks=False  # 不保留临时文件
    )


# ==================== 示例 2: 仅提取PDF文本 ====================
def example_pdf_extraction():
    """仅提取PDF文本"""
    from pdf_extractor import PDFExtractor
    
    # 创建提取器
    extractor = PDFExtractor("your_novel.pdf")
    
    # 提取全部文本
    text = extractor.extract_text()
    print(f"提取的文本长度: {len(text)} 字符")
    print(f"前100字符: {text[:100]}")
    
    # 按页提取
    pages = extractor.extract_text_by_pages()
    print(f"总页数: {len(pages)}")


# ==================== 示例 3: 文本处理 ====================
def example_text_processing():
    """文本分割和处理"""
    from text_processor import TextProcessor
    
    # 创建处理器
    processor = TextProcessor(max_chars=200)
    
    # 示例文本
    text = """
    这是一个很长的文本。它包含多个句子。
    我们需要将它分割成适合语音合成的小段。
    每一段都不应该太长，否则会影响生成效果。
    """
    
    # 清理文本
    clean_text = processor.clean_text(text)
    print(f"清理后: {clean_text}")
    
    # 分割成句子
    sentences = processor.split_into_sentences(text)
    print(f"句子数量: {len(sentences)}")
    
    # 分割成chunks
    chunks = processor.split_into_chunks(text)
    print(f"片段数量: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"片段 {i+1}: {chunk}")


# ==================== 示例 4: 仅生成音频 ====================
def example_audio_generation():
    """仅使用音频生成功能"""
    from audio_generator import AudioGenerator
    
    # 创建生成器
    generator = AudioGenerator(
        voice_preset="v2/zh_speaker_1",
        use_small_model=False
    )
    
    # 生成单个音频
    text = "你好，这是一段测试文本。"
    audio = generator.generate_single_audio(text)
    print(f"生成的音频长度: {len(audio)} 采样点")
    
    # 保存音频
    from scipy.io import wavfile
    wavfile.write("test.wav", generator.sample_rate, audio)
    print("音频已保存为 test.wav")


# ==================== 示例 5: 批量生成和合并 ====================
def example_batch_generation():
    """批量生成多个音频片段并合并"""
    from audio_generator import AudioGenerator
    
    generator = AudioGenerator(voice_preset="v2/zh_speaker_1")
    
    # 文本片段
    chunks = [
        "这是第一段文本。",
        "这是第二段文本。",
        "这是第三段文本。"
    ]
    
    # 批量生成
    audio_files = generator.generate_audiobook(chunks, output_dir="my_output")
    print(f"生成了 {len(audio_files)} 个音频文件")
    
    # 合并音频
    merged = generator.merge_audio_files(
        audio_files, 
        "merged.wav",
        silence_duration=0.5  # 片段间隔0.5秒
    )
    print(f"合并后的文件: {merged}")


# ==================== 示例 6: 使用不同的语音 ====================
def example_different_voices():
    """尝试不同的语音预设"""
    from audio_generator import AudioGenerator
    
    # 获取可用语音列表
    voices = AudioGenerator.get_available_voices()
    
    print("可用的语音预设:")
    for lang, speakers in voices.items():
        print(f"\n{lang}:")
        for speaker in speakers[:3]:  # 只显示前3个
            print(f"  - {speaker}")
    
    # 使用英文语音
    generator_en = AudioGenerator(voice_preset="v2/en_speaker_6")
    audio_en = generator_en.generate_single_audio("Hello, this is a test.")
    
    # 使用中文语音
    generator_zh = AudioGenerator(voice_preset="v2/zh_speaker_3")
    audio_zh = generator_zh.generate_single_audio("你好，这是一个测试。")


# ==================== 示例 7: 自定义参数 ====================
def example_custom_parameters():
    """使用自定义参数"""
    from audiobook_maker import AudiobookMaker
    
    # 创建制作器，使用小模型和更短的片段
    maker = AudiobookMaker(
        voice_preset="v2/zh_speaker_5",
        max_chars=150,  # 更短的片段
        use_small_model=True  # 使用小模型节省显存
    )
    
    # 生成时保留中间文件
    maker.create_audiobook(
        pdf_path="your_novel.pdf",
        output_path="custom_audiobook.wav",
        keep_chunks=True  # 保留音频片段
    )


# ==================== 示例 8: 错误处理 ====================
def example_error_handling():
    """错误处理示例"""
    from audiobook_maker import AudiobookMaker
    import os
    
    pdf_path = "your_novel.pdf"
    
    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误: 文件不存在 {pdf_path}")
        return
    
    try:
        maker = AudiobookMaker()
        maker.create_audiobook(pdf_path, "output.wav")
    except Exception as e:
        print(f"生成失败: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("有声读物生成工具 - 使用示例")
    print("=" * 60)
    
    # 取消注释下面的行来运行示例
    
    # example_full_workflow()
    # example_pdf_extraction()
    # example_text_processing()
    # example_audio_generation()
    # example_batch_generation()
    # example_different_voices()
    # example_custom_parameters()
    # example_error_handling()
    
    print("\n请编辑此文件，取消注释要运行的示例")



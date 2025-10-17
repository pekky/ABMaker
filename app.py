"""
Web界面 - 使用Gradio创建简单的上传界面
"""
import os
import gradio as gr
from audiobook_maker import AudiobookMaker
from audio_generator import AudioGenerator


def create_audiobook_web(pdf_file, voice_preset, max_chars, use_small_model, progress=gr.Progress()):
    """
    Web界面的有声读物生成函数
    
    Args:
        pdf_file: 上传的PDF文件
        voice_preset: 语音预设
        max_chars: 最大字符数
        use_small_model: 是否使用小模型
        progress: 进度条
        
    Returns:
        音频文件路径和状态消息
    """
    if pdf_file is None:
        return None, "请先上传PDF文件"
    
    try:
        progress(0, desc="初始化...")
        
        # 创建制作器
        maker = AudiobookMaker(
            voice_preset=voice_preset,
            max_chars=int(max_chars),
            use_small_model=use_small_model
        )
        
        progress(0.1, desc="提取PDF文本...")
        
        # 生成输出文件名
        base_name = os.path.splitext(os.path.basename(pdf_file.name))[0]
        output_path = f"{base_name}_audiobook.wav"
        
        progress(0.3, desc="生成音频...")
        
        # 创建有声读物
        result = maker.create_audiobook(
            pdf_path=pdf_file.name,
            output_path=output_path,
            keep_chunks=False
        )
        
        progress(1.0, desc="完成！")
        
        return result, f"✓ 有声读物生成成功！\n文件已保存为: {output_path}"
    
    except Exception as e:
        return None, f"❌ 生成失败: {str(e)}"


# 获取可用的语音选项
voices = AudioGenerator.get_available_voices()
voice_choices = []
for lang, speakers in voices.items():
    voice_choices.extend(speakers)


# 创建Gradio界面
with gr.Blocks(title="PDF小说转有声读物", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 📖 PDF小说转有声读物工具
    
    使用AI语音合成技术（Bark）将PDF小说转换为有声读物
    
    ### 使用说明：
    1. 上传PDF格式的小说文件
    2. 选择语音预设和其他参数
    3. 点击"开始生成"按钮
    4. 等待处理完成，下载生成的音频文件
    
    **注意**: 生成时间取决于文本长度和硬件性能，可能需要较长时间。
    """)
    
    with gr.Row():
        with gr.Column():
            # 输入部分
            pdf_input = gr.File(
                label="📁 上传PDF文件",
                file_types=[".pdf"],
                type="filepath"
            )
            
            voice_input = gr.Dropdown(
                choices=voice_choices,
                value="v2/zh_speaker_1",
                label="🎤 选择语音",
                info="不同的语音预设会产生不同的音色"
            )
            
            with gr.Row():
                max_chars_input = gr.Slider(
                    minimum=100,
                    maximum=300,
                    value=200,
                    step=10,
                    label="每段最大字符数",
                    info="较小的值会产生更多片段，但语音更自然"
                )
                
                use_small_model_input = gr.Checkbox(
                    label="使用小模型",
                    value=False,
                    info="节省显存，但音质略有下降"
                )
            
            generate_btn = gr.Button("🚀 开始生成", variant="primary", size="lg")
        
        with gr.Column():
            # 输出部分
            audio_output = gr.Audio(
                label="🎵 生成的有声读物",
                type="filepath"
            )
            
            status_output = gr.Textbox(
                label="📋 状态信息",
                lines=10,
                max_lines=15
            )
    
    # 示例说明
    gr.Markdown("""
    ### 💡 提示：
    - **中文小说**: 选择 `v2/zh_speaker_0` 到 `v2/zh_speaker_9`
    - **英文小说**: 选择 `v2/en_speaker_0` 到 `v2/en_speaker_9`
    - **其他语言**: 支持日语、韩语、德语、法语、西班牙语等
    - 如果显存不足，请勾选"使用小模型"选项
    - 生成的音频为WAV格式，可以用任何音频播放器播放
    
    ### 🔧 技术支持：
    - 使用 [Bark](https://github.com/suno-ai/bark) 进行语音合成
    - 支持多种语言和音色
    - 自动处理长文本分段
    """)
    
    # 绑定事件
    generate_btn.click(
        fn=create_audiobook_web,
        inputs=[pdf_input, voice_input, max_chars_input, use_small_model_input],
        outputs=[audio_output, status_output]
    )


if __name__ == "__main__":
    print("正在启动Web界面...")
    print("请在浏览器中打开显示的URL")
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)



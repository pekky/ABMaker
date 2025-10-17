# 📖 PDF小说转有声读物工具

这是一个基于AI语音合成技术的PDF小说转有声读物工具，使用 [Bark](https://github.com/suno-ai/bark) 模型生成高质量的语音音频。

## ✨ 功能特点

- 📄 支持PDF格式小说文件
- 🎤 支持多种语言和音色（中文、英文、日语、韩语等）
- 🤖 使用Bark AI模型生成自然流畅的语音
- 🎵 自动合并音频片段，生成完整有声读物
- 🌐 提供Web界面，操作简单便捷
- 💻 支持命令行模式，适合批量处理

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆或下载项目
cd ttlnovel

# 安装Python依赖（建议使用Python 3.8+）
pip install -r requirements.txt

# 下载NLTK数据（首次运行时会自动下载）
```

### 2. 使用Web界面（推荐）

```bash
# 启动Web界面
python app.py
```

然后在浏览器中打开 `http://localhost:7860`

#### Web界面使用步骤：
1. 上传PDF文件
2. 选择语音预设（例如：`v2/zh_speaker_1` 用于中文）
3. 调整参数（可选）
4. 点击"开始生成"
5. 等待处理完成，下载音频文件

### 3. 使用命令行

```bash
# 基本用法
python audiobook_maker.py your_novel.pdf

# 指定输出文件
python audiobook_maker.py your_novel.pdf -o my_audiobook.wav

# 选择不同的语音
python audiobook_maker.py your_novel.pdf -v v2/zh_speaker_3

# 使用小模型（节省显存）
python audiobook_maker.py your_novel.pdf --small-model

# 保留中间音频片段
python audiobook_maker.py your_novel.pdf --keep-chunks
```

#### 命令行参数说明：

- `pdf_file`: PDF文件路径（必需）
- `-o, --output`: 输出音频文件路径（默认：audiobook.wav）
- `-v, --voice`: 语音预设（默认：v2/zh_speaker_1）
- `-c, --max-chars`: 每个片段的最大字符数（默认：200）
- `--small-model`: 使用小模型，节省显存
- `--keep-chunks`: 保留音频片段文件

## 🎤 可用的语音预设

### 中文
- `v2/zh_speaker_0` 到 `v2/zh_speaker_9`

### 英文
- `v2/en_speaker_0` 到 `v2/en_speaker_9`

### 其他语言
- 日语: `v2/ja_speaker_0` 到 `v2/ja_speaker_9`
- 韩语: `v2/ko_speaker_0` 到 `v2/ko_speaker_9`
- 德语: `v2/de_speaker_0` 到 `v2/de_speaker_9`
- 法语: `v2/fr_speaker_0` 到 `v2/fr_speaker_9`
- 西班牙语: `v2/es_speaker_0` 到 `v2/es_speaker_9`

更多语音预设请参考 [Bark文档](https://github.com/suno-ai/bark)

## 💻 系统要求

### 硬件要求
- **GPU推荐**: NVIDIA GPU with 12GB+ VRAM（完整模型）
- **GPU最低**: 4GB+ VRAM（使用 `--small-model` 选项）
- **CPU**: 支持，但速度较慢
- **内存**: 8GB+ RAM

### 软件要求
- Python 3.8+
- CUDA 11.7+ （如果使用GPU）

## 📂 项目结构

```
ttlnovel/
├── pdf_extractor.py      # PDF文本提取模块
├── text_processor.py     # 文本处理和分割模块
├── audio_generator.py    # Bark音频生成模块
├── audiobook_maker.py    # 主程序（命令行）
├── app.py               # Web界面（Gradio）
├── requirements.txt     # 依赖列表
└── README.md           # 说明文档
```

## ⚙️ 工作原理

1. **PDF提取**: 使用 `pdfplumber` 从PDF文件中提取文本
2. **文本分割**: 智能分割文本成适合Bark处理的片段（约13秒音频）
3. **音频生成**: 使用Bark模型为每个文本片段生成语音
4. **音频合并**: 将所有音频片段合并成完整的有声读物

## 🔧 高级用法

### 自定义文本处理

```python
from audiobook_maker import AudiobookMaker

# 创建制作器，自定义参数
maker = AudiobookMaker(
    voice_preset="v2/zh_speaker_1",
    max_chars=250,  # 每段更多字符
    use_small_model=True  # 使用小模型
)

# 生成有声读物
maker.create_audiobook(
    pdf_path="novel.pdf",
    output_path="audiobook.wav",
    keep_chunks=True  # 保留中间文件
)
```

### 仅使用音频生成器

```python
from audio_generator import AudioGenerator

# 初始化生成器
generator = AudioGenerator(voice_preset="v2/zh_speaker_1")

# 生成单个音频
audio = generator.generate_single_audio("这是一段测试文本。")

# 批量生成
chunks = ["第一段文本。", "第二段文本。", "第三段文本。"]
audio_files = generator.generate_audiobook(chunks)

# 合并音频
generator.merge_audio_files(audio_files, "output.wav")
```

## ⚠️ 注意事项

1. **处理时间**: 生成有声读物需要较长时间，取决于文本长度和硬件性能
2. **显存占用**: 完整模型需要约12GB显存，可使用 `--small-model` 减少占用
3. **音质**: Bark生成的音频是完全合成的，可能不如专业录音
4. **语言检测**: 请根据PDF内容选择正确的语音预设
5. **版权**: 请确保您有权使用PDF内容制作有声读物

## 🐛 常见问题

### Q: 显存不足怎么办？
A: 使用 `--small-model` 选项，或设置环境变量：
```bash
export SUNO_USE_SMALL_MODELS=True
export SUNO_OFFLOAD_CPU=True
```

### Q: 生成速度太慢？
A: 
- 使用GPU可以显著提升速度
- 减少 `max_chars` 参数会增加片段数量，但每个片段生成更快
- 考虑使用更强大的硬件

### Q: 音频质量不好？
A: 
- 尝试不同的语音预设
- 确保PDF文本提取质量良好
- 调整 `max_chars` 参数以优化分段

### Q: 支持其他格式的文档吗？
A: 目前只支持PDF格式。如需支持其他格式，可以先转换为PDF。

## 📝 许可证

本项目使用 MIT 许可证。Bark模型也使用 MIT 许可证。

## 🙏 致谢

- [Bark](https://github.com/suno-ai/bark) - Suno AI的开源文本转语音模型
- [Gradio](https://gradio.app/) - 用于构建Web界面
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF文本提取

## 📧 联系方式

如有问题或建议，欢迎提交Issue或Pull Request。

---

**享受您的AI有声读物！** 🎧



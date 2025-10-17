# 快速入门指南

## 📋 目录
1. [环境准备](#环境准备)
2. [安装步骤](#安装步骤)
3. [快速开始](#快速开始)
4. [常见问题](#常见问题)

## 🔧 环境准备

### 必需软件
- Python 3.8 或更高版本
- pip（Python包管理器）

### 硬件建议
- **推荐配置**: NVIDIA GPU (12GB+ VRAM)
- **最低配置**: 4GB+ VRAM 或 CPU（速度较慢）
- **内存**: 8GB+ RAM

## 📦 安装步骤

### 方法1: 自动安装（推荐）

**Windows用户:**
```bash
双击运行 start_web.bat
```

**Mac/Linux用户:**
```bash
./start_web.sh
```

### 方法2: 手动安装

```bash
# 1. 进入项目目录
cd ttlnovel

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动Web界面
python app.py
```

## 🚀 快速开始

### 使用Web界面（最简单）

1. **启动服务**
   ```bash
   python app.py
   ```

2. **打开浏览器**
   - 访问 `http://localhost:7860`

3. **上传PDF并生成**
   - 点击"上传PDF文件"按钮
   - 选择您的PDF小说文件
   - 选择语音预设（中文选择 `v2/zh_speaker_1`）
   - 点击"开始生成"
   - 等待处理完成

4. **下载音频**
   - 生成完成后，播放预听
   - 点击下载按钮保存音频文件

### 使用命令行

```bash
# 基础用法
python audiobook_maker.py your_novel.pdf

# 指定输出文件名
python audiobook_maker.py your_novel.pdf -o my_audiobook.wav

# 使用不同的语音
python audiobook_maker.py your_novel.pdf -v v2/zh_speaker_3

# 如果显存不足，使用小模型
python audiobook_maker.py your_novel.pdf --small-model
```

## 🎤 语音选择指南

### 中文小说
```
v2/zh_speaker_0  # 中文女声1
v2/zh_speaker_1  # 中文女声2（推荐）
v2/zh_speaker_2  # 中文男声1
v2/zh_speaker_3  # 中文男声2
...（共10个）
```

### 英文小说
```
v2/en_speaker_0  # 英文女声1
v2/en_speaker_1  # 英文女声2
v2/en_speaker_6  # 英文男声（推荐）
...（共10个）
```

### 其他语言
- 日语: `v2/ja_speaker_0` ~ `v2/ja_speaker_9`
- 韩语: `v2/ko_speaker_0` ~ `v2/ko_speaker_9`
- 德语: `v2/de_speaker_0` ~ `v2/de_speaker_9`

## ⚙️ 参数调整

### 每段字符数（max_chars）
- **默认**: 200
- **建议范围**: 150-250
- **说明**: 
  - 较小值：片段更多，语音更自然，生成时间更长
  - 较大值：片段更少，速度更快，可能不够自然

### 使用小模型（small_model）
- **何时使用**: 显存不足（<8GB VRAM）
- **效果**: 节省显存，音质略有下降
- **开启方式**: 
  ```bash
  python audiobook_maker.py your_novel.pdf --small-model
  ```

## ❓ 常见问题

### Q1: 显存不足（CUDA out of memory）
**解决方案**:
```bash
# 方法1: 使用小模型
python audiobook_maker.py your_novel.pdf --small-model

# 方法2: 设置环境变量
export SUNO_USE_SMALL_MODELS=True
export SUNO_OFFLOAD_CPU=True
python audiobook_maker.py your_novel.pdf
```

### Q2: 生成速度很慢
**原因和解决**:
- 使用CPU生成（慢）→ 建议使用GPU
- PDF文件太大 → 先测试小文件
- 网络问题 → 首次运行需下载模型，请耐心等待

### Q3: 音频质量不好
**优化建议**:
- 尝试不同的语音预设（`-v` 参数）
- 确保PDF文本提取质量好
- 调整 `max_chars` 参数

### Q4: PDF提取失败
**可能原因**:
- PDF是扫描版（图片）→ 需要先OCR转换
- PDF有密码保护 → 先解除密码
- PDF格式损坏 → 尝试修复或重新生成PDF

### Q5: 首次运行很慢
**说明**: 
- 首次运行会自动下载Bark模型（约2GB）
- 下载完成后会自动缓存
- 后续运行会快很多

## 📝 完整示例

### 示例1: 生成中文小说有声读物
```bash
# 使用默认设置
python audiobook_maker.py chinese_novel.pdf

# 使用自定义语音和输出文件名
python audiobook_maker.py chinese_novel.pdf \
  -v v2/zh_speaker_3 \
  -o chinese_audiobook.wav
```

### 示例2: 生成英文小说有声读物
```bash
python audiobook_maker.py english_novel.pdf \
  -v v2/en_speaker_6 \
  -o english_audiobook.wav
```

### 示例3: 低显存设备
```bash
python audiobook_maker.py novel.pdf \
  --small-model \
  -c 150 \
  -o audiobook.wav
```

## 🔗 更多资源

- 详细文档: [README.md](README.md)
- 代码示例: [example_usage.py](example_usage.py)
- Bark项目: https://github.com/suno-ai/bark

## 💡 提示

1. **首次使用**: 建议先用小PDF文件（1-2页）测试
2. **批量处理**: 可以编写脚本循环调用命令行工具
3. **音频格式**: 生成的WAV文件可以用其他工具转换为MP3等格式
4. **中断恢复**: 如果中断，重新运行即可，已生成的片段会被覆盖
5. **存储空间**: 确保有足够的磁盘空间（音频文件可能很大）

---

**开始享受您的AI有声读物吧！** 🎧



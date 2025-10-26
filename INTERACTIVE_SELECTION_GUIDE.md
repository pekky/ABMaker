# 交互式语言和语音选择指南

## 📋 功能概述

`optimized_audiobook_maker.py` 现在支持交互式选择文本语言和语音，让您在运行时轻松配置转换参数。

## 🎯 使用方法

### 方法 1：完全交互式（推荐新手）

直接运行脚本，系统会提示您选择：

```bash
cd /home/alai/projects/ABMaker
source ~/.bashrc && conda activate abmaker310
python3 optimized_audiobook_maker.py
```

运行后会看到：

```
🌍 请选择文本语言 / Select Text Language:
  1. English (英语) [默认]
  2. 中文 (Chinese)
  3. 日本語 (Japanese)

请输入选项 (1-3，直接回车选择默认): 
```

**直接按回车** = 选择默认选项（英语 + 英语男声）

### 方法 2：命令行参数（推荐高级用户）

跳过交互，直接指定参数：

```bash
# 英语，男声
python3 optimized_audiobook_maker.py -l en -v v2/en_speaker_0

# 中文，女声
python3 optimized_audiobook_maker.py -l zh -v v2/zh_speaker_1

# 日语，男声
python3 optimized_audiobook_maker.py -l ja -v v2/ja_speaker_0
```

### 方法 3：混合模式

只指定语言，交互式选择语音：

```bash
python3 optimized_audiobook_maker.py -l en
```

## 🎤 可用语音列表

### 英语 (English)
- `v2/en_speaker_0` - 英语男声 (Male) **[默认]**
- `v2/en_speaker_1` - 英语女声 (Female)
- `v2/en_speaker_2` - 英语男声2 (Male 2)
- `v2/en_speaker_3` - 英语女声2 (Female 2)
- `v2/en_speaker_4` - 英语男声3 (Male 3)
- `v2/en_speaker_5` - 英语女声3 (Female 3)
- `v2/en_speaker_6` - 英语男声4 (Male 4)
- `v2/en_speaker_7` - 英语女声4 (Female 4)
- `v2/en_speaker_8` - 英语男声5 (Male 5)

### 中文 (Chinese)
- `v2/zh_speaker_0` - 中文男声 (Male)
- `v2/zh_speaker_1` - 中文女声 (Female) **[默认]**
- `v2/zh_speaker_2` - 中文男声2 (Male 2)
- `v2/zh_speaker_3` - 中文女声2 (Female 2)
- `v2/zh_speaker_4` - 中文男声3 (Male 3)
- `v2/zh_speaker_5` - 中文女声3 (Female 3)
- `v2/zh_speaker_6` - 中文男声4 (Male 4)
- `v2/zh_speaker_7` - 中文女声4 (Female 4)
- `v2/zh_speaker_8` - 中文男声5 (Male 5)

### 日语 (Japanese)
- `v2/ja_speaker_0` - 日语男声 (Male)
- `v2/ja_speaker_1` - 日语女声 (Female) **[默认]**
- `v2/ja_speaker_2` - 日语男声2 (Male 2)
- `v2/ja_speaker_3` - 日语女声2 (Female 2)
- `v2/ja_speaker_4` - 日语男声3 (Male 3)
- `v2/ja_speaker_5` - 日语女声3 (Female 3)
- `v2/ja_speaker_6` - 日语男声4 (Male 4)
- `v2/ja_speaker_7` - 日语女声4 (Female 4)

## 💡 默认行为

如果您在所有提示中直接按回车（不输入任何内容）：
- **语言**: English (英语)
- **语音**: v2/en_speaker_0 (英语男声)

这是最常用的配置，适合英文文档转换。

## 🔧 完整命令示例

### 示例 1：转换英文PDF，使用默认设置

```bash
python3 optimized_audiobook_maker.py docs/MyBook.pdf
# 在提示时直接按回车两次
```

### 示例 2：转换中文PDF，指定女声

```bash
python3 optimized_audiobook_maker.py docs/中文小说.pdf -l zh -v v2/zh_speaker_1
```

### 示例 3：转换日文PDF，交互式选择语音

```bash
python3 optimized_audiobook_maker.py docs/日本の本.pdf -l ja
# 在语音选择时输入 1 或 2
```

### 示例 4：使用小模型（节省显存）

```bash
python3 optimized_audiobook_maker.py docs/MyBook.pdf -l en -v v2/en_speaker_0 --small-model
```

## 📝 测试交互式选择

运行测试脚本体验交互式选择：

```bash
python3 test_interactive_selection.py
```

## ⚙️ 技术细节

- 语言参数：`-l` 或 `--language`
- 语音参数：`-v` 或 `--voice`
- 如果不提供参数，系统会自动进入交互式选择模式
- 交互式选择支持直接回车使用默认值
- 命令行参数优先级高于交互式选择

## 🎯 最佳实践

1. **首次使用**：建议使用交互式模式，熟悉可用选项
2. **批量处理**：使用命令行参数，可以编写脚本自动化处理
3. **测试语音**：先用短文档测试不同语音，找到最喜欢的
4. **默认配置**：如果主要处理英文文档，直接按回车即可

## 🚀 快速开始

最简单的使用方式：

```bash
cd /home/alai/projects/ABMaker
source ~/.bashrc && conda activate abmaker310
python3 optimized_audiobook_maker.py
# 按回车 → 选择英语
# 按回车 → 选择英语男声
# 从 docs 目录选择文件
```

就这么简单！🎉


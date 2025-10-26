# Batch 文件命名修复说明

## 📋 修复内容

修复了 batch 音频文件命名不符合规定的问题。

## 🐛 问题描述

### 修复前
生成的文件名使用了 `output_path` 的基础名称：
```
audiobook_optimized_251026_001.mp3
audiobook_optimized_251026_002.mp3
audiobook_optimized_251026_003.mp3
```

### 修复后
现在使用 PDF 文件名作为基础名称：
```
CHASE-CHANCE-CREATIVITY_251026_001.mp3
CHASE-CHANCE-CREATIVITY_251026_002.mp3
CHASE-CHANCE-CREATIVITY_251026_003.mp3
```

## 🔧 技术细节

### 问题原因

在 `src/core/audiobook_maker_batch.py` 中：

**原代码**：
```python
def _create_audiobook_batch(self, text, output_path, keep_chunks):
    # ...
    base_name = os.path.splitext(os.path.basename(output_path))[0]
    # output_path 默认是 "audiobook_optimized.mp3"
    # 所以 base_name = "audiobook_optimized" ❌
```

### 修复方案

1. **传递 PDF 路径参数**（第 84 行）：
```python
# 修改前
return self._create_audiobook_batch(full_text, output_path, keep_chunks)

# 修改后
return self._create_audiobook_batch(full_text, output_path, keep_chunks, pdf_path)
```

2. **更新函数签名**（第 120 行）：
```python
# 修改前
def _create_audiobook_batch(self, text, output_path, keep_chunks):

# 修改后
def _create_audiobook_batch(self, text, output_path, keep_chunks, pdf_path):
```

3. **从 PDF 路径提取文件名**（第 137-138 行）：
```python
# 修改前
base_name = os.path.splitext(os.path.basename(output_path))[0]

# 修改后
base_name = os.path.splitext(os.path.basename(pdf_path))[0]
print(f"📝 使用 PDF 文件名: {base_name}")
```

## 📊 命名规则

根据 `config.py` 和 `AGENTS.md` 的规定：

### 格式
```
pdf文件名_yymmdd_batchnumber.mp3
```

### 说明
- **pdf文件名**: 从 PDF 文件路径提取（不含扩展名）
- **yymmdd**: 2位年份 + 2位月份 + 2位日期
- **batchnumber**: 3位数字，从 001 开始

### 示例
| PDF 文件 | 日期 | Batch | 输出文件名 |
|---------|------|-------|-----------|
| RiverTown.pdf | 2025-10-25 | 1 | `RiverTown_251025_001.mp3` |
| RiverTown.pdf | 2025-10-25 | 2 | `RiverTown_251025_002.mp3` |
| CHASE-CHANCE-CREATIVITY.pdf | 2025-10-26 | 1 | `CHASE-CHANCE-CREATIVITY_251026_001.mp3` |
| 中文书名.pdf | 2025-10-26 | 1 | `中文书名_251026_001.mp3` |

## ✅ 验证

下次运行转换时，您会看到：

```
📦 启用批量处理模式
📊 总共分割成 15 个batch
📝 使用 PDF 文件名: CHASE-CHANCE-CREATIVITY

步骤 3-5/6: 处理Batch 1/15
------------------------------------------------------------
...
✅ Batch 1 完成: output/audio/CHASE-CHANCE-CREATIVITY_251026_001.mp3
```

## 🎯 相关修复

同时修复了 batch 编号从 002 开始的问题（见另一个修复）：
- 修改 `enumerate(batches)` 从 0 开始
- 文件编号现在正确从 001 开始

## 📝 配置文件

相关配置在 `config.py` 中：

```python
OUTPUT_CONFIG = {
    "batch_output_format": "%s_%y%m%d_%03d.mp3",
    "batch_output_example": "RiverTown_251025_001.mp3",
}

BATCH_PROCESSING = {
    "optimized_batch_mode": {
        "batch_filename_format": "%s_%y%m%d_%03d.mp3",
    }
}
```

## 🚀 下次使用

下次运行 `optimized_audiobook_maker.py` 时，生成的文件将正确命名：

```bash
python3 optimized_audiobook_maker.py docs/YourBook.pdf
```

输出：
```
output/audio/YourBook_251026_001.mp3
output/audio/YourBook_251026_002.mp3
output/audio/YourBook_251026_003.mp3
...
```

完美符合命名规范！✨

---

**修复日期**: 2025-10-26  
**修复文件**: `src/core/audiobook_maker_batch.py`  
**修复行数**: 84, 120, 137-138


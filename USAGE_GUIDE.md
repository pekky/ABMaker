# ABMaker 使用指南

## 🚀 快速开始

### 方法一：一键启动（推荐）

```bash
./run_audiobook_maker.sh
```

这个脚本会自动完成所有步骤：
1. 检查并设置虚拟环境
2. 选择质量模式（快速/高质量）
3. 选择PDF文件
4. 后台运行转换
5. 启动进展监控

### 方法二：分步操作

1. **设置环境**：
   ```bash
   ./setup_environment.sh
   ```

2. **激活环境**：
   ```bash
   ./activate_env.sh
   ```

3. **手动运行转换**：
   ```bash
   source ~/.bashrc && conda activate abmaker310 && python3 optimized_audiobook_maker.py docs/RiverTown.pdf --batch-mode --batch-size 15000
   ```

## 📊 监控和管理

### 监控转换进展

```bash
./monitor.sh
```

监控脚本会显示：
- 进程状态和资源使用情况
- 实时日志内容
- 输出文件生成情况
- 临时文件数量

### 停止转换

```bash
./stop_conversion.sh
```

停止脚本会：
- 停止转换进程
- 停止监控进程
- 清理临时文件（可选）

## 🎯 质量模式选择

### 快速模式（推荐）
- **特点**: 使用小模型，转换速度快
- **适用**: 快速预览和测试
- **质量**: 中等
- **参数**: `--small-model`

### 高质量模式
- **特点**: 使用大模型，转换时间长
- **适用**: 最终输出和高质量需求
- **质量**: 高
- **参数**: 无 `--small-model`

## 📁 输出文件

### 目录结构
```
ABMaker/
├── output/          # 音频输出文件
├── logs/           # 日志文件
├── tmp/            # 临时文件
└── docs/           # PDF源文件
```

### 文件命名规则
- 音频文件: `{PDF名称}_{质量模式}_{时间戳}.wav`
- 日志文件: `{PDF名称}_{质量模式}_{时间戳}.log`

## 🔧 高级配置

### 批量处理参数
- `--batch-mode`: 启用批量处理
- `--batch-size`: 每个batch的token数量（默认15000）
- `--keep-chunks`: 保留音频片段文件

### 音频参数
- `--max-chars`: 每个片段的最大字符数（默认700）
- `--voice`: 语音预设（默认v2/en_speaker_0）

### 示例命令
```bash
# 高质量模式，自定义batch大小
python3 optimized_audiobook_maker.py docs/RiverTown.pdf --batch-mode --batch-size 20000 --output high_quality.wav

# 快速模式，保留片段文件
python3 optimized_audiobook_maker.py docs/RiverTown.pdf --batch-mode --small-model --keep-chunks
```

## 🐛 故障排除

### 常见问题

1. **环境问题**：
   ```bash
   ./setup_environment.sh
   ```

2. **权限问题**：
   ```bash
   chmod +x *.sh
   ```

3. **进程卡死**：
   ```bash
   ./stop_conversion.sh
   ```

4. **查看日志**：
   ```bash
   tail -f logs/*.log
   ```

### 手动清理

```bash
# 清理临时文件
rm -rf tmp/*

# 清理进程文件
rm -f *.pid

# 重新启动
./run_audiobook_maker.sh
```

## 📝 注意事项

1. **首次运行**: 环境准备可能需要较长时间
2. **网络要求**: 需要稳定的网络连接下载依赖
3. **磁盘空间**: 确保有足够的磁盘空间（至少5GB）
4. **内存要求**: 建议8GB以上内存
5. **GPU支持**: 可选，支持CUDA加速

## 🔄 更新和维护

### 更新依赖
```bash
source ~/.bashrc && conda activate abmaker310 && pip install -r requirements.txt --upgrade
```

### 重新创建环境
```bash
conda env remove -n abmaker310
./setup_environment.sh
```

## 📞 获取帮助

如果遇到问题：
1. 查看本文档的故障排除部分
2. 检查日志文件
3. 查看项目README文件
4. 检查AGENTS.md文件中的项目规则


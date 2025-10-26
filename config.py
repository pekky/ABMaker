# -*- coding: utf-8 -*-
"""
ABMaker配置文件
包含所有可调参数，实现代码与配置的解耦
"""

# 文本分段配置
TEXT_SEGMENTATION = {
    # 片段长度范围
    "min_chars": 600,           # 最小字符数
    "max_chars": 800,           # 最大字符数
    "default_chars": 700,       # 默认字符数
    
    # 分割策略
    "split_at_sentences": True,  # 优先在句号处分割
    "split_at_paragraphs": True, # 优先在段落处分割
    "split_at_commas": True,     # 在逗号处分割长句
    
    # 文本清理
    "normalize_numbers": True,   # 规范化数字
    "normalize_punctuation": True, # 规范化标点
    "add_rhythm_annotations": True, # 添加韵律注释
}

# Bark生成参数配置
BARK_GENERATION = {
    # 温度参数（控制生成稳定性）
    "text_temp": 0.65,          # 文本温度 0.6-0.75
    "waveform_temp": 0.55,      # 波形温度 0.5-0.65
    
    # 随机种子（保证一致性）
    "seed": 1234,              # 固定种子
    "use_fixed_seed": True,     # 是否使用固定种子
    
    # 模型选择
    "use_small_model": False,  # 是否使用小模型
    "default_voice": "v2/en_speaker_0", # 默认语音
}

# 音频后处理配置
AUDIO_POST_PROCESSING = {
    # 采样率设置
    "sample_rate": 24000,       # 保持24kHz采样率
    
    # 停顿时长
    "segment_silence": 0.3,     # 段与段之间 0.2-0.4s
    "sentence_silence": 0.08,  # 段内句间 0.06-0.12s
    
    # 交叉淡化
    "fade_ms": 6.0,            # 3-8ms交叉淡化
    
    # 归一化
    "peak_dbfs": -1.0,         # 峰值归一化到-1.0 dBFS
    "lufs_target": -18.0,      # LUFS目标-16~-20
    
    # 去噪处理
    "enable_denoise": True,     # 启用轻度去噪
    "denoise_threshold": 0.01,  # 门限降噪阈值
    
    # 去齿音
    "enable_deesser": True,     # 启用轻度去齿音
    "deesser_freq": 8000,      # 去齿音频率
}

# 语速与韵律配置
RHYTHM_CONTROL = {
    # 韵律注释
    "add_pause_annotations": True,    # 添加停顿注释
    "pause_after_comma": True,        # 逗号后添加停顿
    "pause_after_numbers": True,      # 数字后添加停顿
    
    # 数字处理
    "normalize_chinese_numbers": True, # 中文数字转阿拉伯数字
    "add_space_after_numbers": True,   # 数字后添加空格
    "add_space_in_abbreviations": True, # 缩略词中添加空格
    
    # 语速控制
    "slow_down_long_numbers": True,   # 长数字串放慢
    "slow_down_abbreviations": True,  # 缩略词放慢
}

# 资源管理配置
RESOURCE_MANAGEMENT = {
    # GPU优化
    "enable_gpu_optimization": True,   # 启用GPU优化
    "cudnn_benchmark": True,          # 启用cuDNN基准
    "cudnn_deterministic": False,      # 非确定性模式（更快）
    
    # 内存管理
    "clear_gpu_cache_interval": 50,   # 每50个片段清理GPU缓存
    "preload_models": True,            # 预热模型
    
    # 批处理
    "batch_size": 4,                  # 批处理大小
    "max_concurrent": 1,              # 最大并发数
}

# 批量处理配置
BATCH_PROCESSING = {
    # 批量分割
    "enable_batch_processing": True,   # 启用批量处理
    "batch_size_chars": 10000,         # 每个batch的字符数（1万字符）
    "batch_size_tokens": 15000,        # 每个batch的token数（1.5万token）
    "batch_overlap_chars": 200,        # batch之间的重叠字符数
    
    # 分割策略
    "split_at_paragraphs": True,       # 优先在段落处分割batch
    "split_at_chapters": True,         # 优先在章节处分割batch
    "min_batch_size": 5000,            # 最小batch大小
    "max_batch_size": 20000,           # 最大batch大小
    
    # 输出设置
    "batch_output_prefix": "batch_",   # batch文件前缀
    "batch_output_suffix": "_audiobook.wav", # batch文件后缀
    "create_final_merge": True,        # 是否创建最终合并文件
    "final_output_name": "complete_audiobook.wav", # 最终合并文件名
    
    # 优化版批量处理规则
    "optimized_batch_mode": {
        "enabled": True,               # 启用优化版批量处理
        "default_token_size": 15000,  # 默认token大小
        "generate_separate_audio": True, # 每个batch生成单独音频
        "use_tmp_directory": True,    # 使用tmp目录存储临时文件
        "cleanup_after_batch": True,  # 每个batch完成后清理临时文件
        
        # 时间戳目录规则
        "use_timestamped_temp_dir": True,  # 使用时间戳临时目录
        "temp_dir_format": "chunks_%y%m%d_%H%M",  # 格式: chunks_yymmdd_hhmm
        "batch_subdir_format": "batch_%d",  # batch子目录格式: batch_1, batch_2, ...
        
        # 输出文件规则
        "output_to_audio_dir": True,  # 输出到output/audio目录
        "batch_filename_format": "%s_%y%m%d_%03d.mp3",  # pdf文件名_yymmdd_batchnumber.mp3
    }
}

# 输出配置
OUTPUT_CONFIG = {
    # 文件格式
    "audio_format": "mp3",            # 音频格式: "mp3" 或 "wav"
    "sample_rate": 24000,             # 采样率
    "bit_depth": 32,                  # 位深度（仅用于WAV）
    
    # MP3 配置
    "mp3_bitrate": "320k",            # MP3 比特率: "320k", "256k", "192k", "128k"
    "mp3_quality": 0,                 # MP3 质量: 0 (最高) - 9 (最低)
    
    # 文件命名
    "chunk_prefix": "chunk_",         # 片段文件前缀
    "chunk_padding": 4,               # 片段编号填充位数
    
    # 目录结构
    "temp_dir": "tmp",                # 临时目录
    "output_dir": "output",           # 输出目录
    "keep_chunks": False,             # 是否保留片段文件
    
    # 时间戳目录规则
    "timestamped_temp_dir": True,     # 启用时间戳临时目录
    "temp_dir_format": "chunks_%y%m%d_%H%M",  # 临时目录格式: chunks_yymmdd_hhmm
    "temp_dir_example": "chunks_251024_2243",  # 示例: 2025年10月24日22:43
    
    # Batch输出文件命名规则
    "batch_output_format": "%s_%y%m%d_%03d.mp3",  # pdf文件名_yymmdd_batchnumber.mp3
    "batch_output_example": "RiverTown_251025_001.mp3",  # 示例文件名
    
    # 文件名长度限制
    "max_filename_length": 20,  # 最大文件名长度（字符数）
    "filename_truncate_strategy": "separator",  # 截断策略: "separator" 在分隔符处截断, "direct" 直接截断
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",                  # 日志级别
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file": "audiobook.log",          # 日志文件
    "max_size": 10 * 1024 * 1024,    # 最大文件大小 10MB
    "backup_count": 5,                # 备份文件数量
}

# 预设配置（不同场景的预设）
PRESETS = {
    "high_quality": {
        "description": "高质量模式",
        "text_temp": 0.60,
        "coarse_temp": 0.60,
        "waveform_temp": 0.50,
        "top_p": 0.85,
        "top_k": 50,
        "cfg_scale": 2.0,
        "use_small_model": False,
    },
    "fast": {
        "description": "快速模式",
        "text_temp": 0.70,
        "coarse_temp": 0.65,
        "waveform_temp": 0.60,
        "top_p": 0.95,
        "top_k": 100,
        "cfg_scale": 1.5,
        "use_small_model": True,
    },
    "balanced": {
        "description": "平衡模式（默认）",
        "text_temp": 0.65,
        "coarse_temp": 0.62,
        "waveform_temp": 0.55,
        "top_p": 0.90,
        "top_k": 75,
        "cfg_scale": 1.75,
        "use_small_model": False,
    },
    "conservative": {
        "description": "保守模式（低显存）",
        "text_temp": 0.60,
        "coarse_temp": 0.60,
        "waveform_temp": 0.50,
        "top_p": 0.85,
        "top_k": 50,
        "cfg_scale": 2.0,
        "use_small_model": True,
    }
}

# 语言特定配置
LANGUAGE_CONFIGS = {
    "zh": {  # 中文
        "default_voice": "v2/zh_speaker_1",
        "sentence_endings": ["。", "！", "？"],
        "pause_markers": ["，", "；", "、"],
        "rhythm_annotations": True,
    },
    "en": {  # 英文
        "default_voice": "v2/en_speaker_0",
        "sentence_endings": [".", "!", "?"],
        "pause_markers": [",", ";", ":"],
        "rhythm_annotations": True,
    },
    "ja": {  # 日文
        "default_voice": "v2/ja_speaker_1",
        "sentence_endings": ["。", "！", "？"],
        "pause_markers": ["、", "，"],
        "rhythm_annotations": True,
    }
}

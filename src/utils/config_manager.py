# -*- coding: utf-8 -*-
"""
配置管理工具
提供配置的加载、验证和应用功能
"""
import os
import json
import copy

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file="config.py"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                # 动态导入配置文件
                import importlib.util
                spec = importlib.util.spec_from_file_location("config", self.config_file)
                config_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config_module)
                
                # 提取所有配置
                self.config = {
                    "TEXT_SEGMENTATION": getattr(config_module, "TEXT_SEGMENTATION", {}),
                    "BARK_GENERATION": getattr(config_module, "BARK_GENERATION", {}),
                    "AUDIO_POST_PROCESSING": getattr(config_module, "AUDIO_POST_PROCESSING", {}),
                    "RHYTHM_CONTROL": getattr(config_module, "RHYTHM_CONTROL", {}),
                    "RESOURCE_MANAGEMENT": getattr(config_module, "RESOURCE_MANAGEMENT", {}),
                    "BATCH_PROCESSING": getattr(config_module, "BATCH_PROCESSING", {}),
                    "OUTPUT_CONFIG": getattr(config_module, "OUTPUT_CONFIG", {}),
                    "LOGGING_CONFIG": getattr(config_module, "LOGGING_CONFIG", {}),
                    "PRESETS": getattr(config_module, "PRESETS", {}),
                    "LANGUAGE_CONFIGS": getattr(config_module, "LANGUAGE_CONFIGS", {}),
                }
                print("✓ 配置文件加载成功")
            else:
                print("❌ 配置文件不存在: " + self.config_file)
                self._create_default_config()
        except Exception as e:
            print("❌ 配置文件加载失败: " + str(e))
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置"""
        self.config = {
            "TEXT_SEGMENTATION": {
                "min_chars": 600,
                "max_chars": 800,
                "default_chars": 700,
                "split_at_sentences": True,
                "split_at_paragraphs": True,
                "split_at_commas": True,
                "normalize_numbers": True,
                "normalize_punctuation": True,
                "add_rhythm_annotations": True,
            },
            "BARK_GENERATION": {
                "text_temp": 0.65,
                "waveform_temp": 0.55,
                "seed": 1234,
                "use_fixed_seed": True,
                "use_small_model": False,
                "default_voice": "v2/en_speaker_0",
            },
            "AUDIO_POST_PROCESSING": {
                "sample_rate": 24000,
                "segment_silence": 0.3,
                "sentence_silence": 0.08,
                "fade_ms": 6.0,
                "peak_dbfs": -1.0,
                "lufs_target": -18.0,
                "enable_denoise": True,
                "denoise_threshold": 0.01,
                "enable_deesser": True,
                "deesser_freq": 8000,
            },
            "RHYTHM_CONTROL": {
                "add_pause_annotations": True,
                "pause_after_comma": True,
                "pause_after_numbers": True,
                "normalize_chinese_numbers": True,
                "add_space_after_numbers": True,
                "add_space_in_abbreviations": True,
                "slow_down_long_numbers": True,
                "slow_down_abbreviations": True,
            },
            "RESOURCE_MANAGEMENT": {
                "enable_gpu_optimization": True,
                "cudnn_benchmark": True,
                "cudnn_deterministic": False,
                "clear_gpu_cache_interval": 10,
                "preload_models": True,
                "batch_size": 1,
                "max_concurrent": 1,
            },
            "BATCH_PROCESSING": {
                "enable_batch_processing": True,
                "batch_size_chars": 15000,
                "batch_size_tokens": 15000,
                "batch_overlap_chars": 200,
                "split_at_paragraphs": True,
                "split_at_chapters": True,
                "min_batch_size": 5000,
                "max_batch_size": 20000,
                "batch_output_prefix": "batch_",
                "batch_output_suffix": "_audiobook.wav",
                "create_final_merge": True,
                "final_output_name": "complete_audiobook.wav",
                "optimized_batch_mode": {
                    "enabled": True,
                    "default_token_size": 15000,
                    "generate_separate_audio": True,
                    "use_tmp_directory": True,
                    "cleanup_after_batch": True,
                }
            },
            "OUTPUT_CONFIG": {
                "audio_format": "wav",
                "sample_rate": 24000,
                "bit_depth": 32,
                "chunk_prefix": "chunk_",
                "chunk_padding": 4,
                "temp_dir": "tmp",
                "output_dir": "output",
                "keep_chunks": False,
            },
            "LOGGING_CONFIG": {
                "level": "INFO",
                "format": "%(asctime)s - %(levelname)s - %(message)s",
                "file": "audiobook.log",
                "max_size": 10 * 1024 * 1024,
                "backup_count": 5,
            },
            "PRESETS": {},
            "LANGUAGE_CONFIGS": {},
        }
        print("✓ 使用默认配置")
    
    def get(self, section, key=None, default=None):
        """
        获取配置值
        
        Args:
            section: 配置节名称
            key: 配置键名称
            default: 默认值
            
        Returns:
            配置值
        """
        if key is None:
            return self.config.get(section, default)
        else:
            section_config = self.config.get(section, {})
            if isinstance(section_config, dict):
                return section_config.get(key, default)
            else:
                return default
    
    def set(self, section, key, value):
        """
        设置配置值
        
        Args:
            section: 配置节名称
            key: 配置键名称
            value: 配置值
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def apply_preset(self, preset_name):
        """
        应用预设配置
        
        Args:
            preset_name: 预设名称
        """
        preset = self.get("PRESETS", preset_name)
        if preset:
            print("✓ 应用预设: " + preset.get("description", preset_name))
            # 将预设参数应用到BARK_GENERATION
            bark_config = self.get("BARK_GENERATION") or {}
            for key, value in preset.items():
                if key != "description" and key in bark_config:
                    bark_config[key] = value
            self.config["BARK_GENERATION"] = bark_config
        else:
            print("❌ 预设不存在: " + preset_name)
    
    def get_text_config(self):
        """获取文本处理配置"""
        return self.get("TEXT_SEGMENTATION") or {}
    
    def get_bark_config(self):
        """获取Bark生成配置"""
        return self.get("BARK_GENERATION") or {}
    
    def get_audio_config(self):
        """获取音频后处理配置"""
        return self.get("AUDIO_POST_PROCESSING") or {}
    
    def get_rhythm_config(self):
        """获取韵律控制配置"""
        return self.get("RHYTHM_CONTROL") or {}
    
    def get_resource_config(self):
        """获取资源管理配置"""
        return self.get("RESOURCE_MANAGEMENT") or {}
    
    def get_batch_config(self):
        """获取批量处理配置"""
        return self.get("BATCH_PROCESSING") or {}
    
    def get_output_config(self):
        """获取输出配置"""
        return self.get("OUTPUT_CONFIG") or {}
    
    def get_language_config(self, language="zh"):
        """获取语言特定配置"""
        return self.get("LANGUAGE_CONFIGS", {}).get(language, {})
    
    def validate_config(self) :
        """验证配置的有效性"""
        try:
            # 验证文本分段配置
            text_config = self.get_text_config()
            if not (600 <= text_config.get("default_chars", 700) <= 800):
                print("❌ 文本分段字符数超出范围")
                return False
            
            # 验证Bark参数
            bark_config = self.get_bark_config()
            if not (0.5 <= bark_config.get("text_temp", 0.65) <= 1.0):
                print("❌ Bark文本温度超出范围")
                return False
            
            # 验证音频配置
            audio_config = self.get_audio_config()
            if audio_config.get("sample_rate", 24000) != 24000:
                print("❌ 采样率必须为24kHz")
                return False
            
            print("✓ 配置验证通过")
            return True
        except Exception as e:
            print("❌ 配置验证失败: " + str(e))
            return False
    
    def save_config(self, output_file=None):
        """
        保存配置到文件
        
        Args:
            output_file: 输出文件路径
        """
        if output_file is None:
            output_file = self.config_file.replace(".py", "_exported.json")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print("✓ 配置已保存到: " + output_file)
        except Exception as e:
            print("❌ 配置保存失败: " + str(e))
    
    def print_config(self, section=None):
        """
        打印配置信息
        
        Args:
            section: 指定节名称，None则打印所有
        """
        if section:
            config_section = self.get(section)
            if config_section:
                print("\n" + "=" * 50)
                print("配置节: " + section)
                print("=" * 50)
                for key, value in config_section.items():
                    print(key + ": " + str(value))
            else:
                print("❌ 配置节不存在: " + section)
        else:
            print("\n" + "=" * 60)
            print("当前配置")
            print("=" * 60)
            for section_name, section_config in self.config.items():
                print("\n[" + section_name + "]")
                for key, value in section_config.items():
                    print("  " + key + ": " + str(value))
    
    def list_presets(self):
        """列出所有可用预设"""
        presets = self.get("PRESETS", {})
        if presets:
            print("\n可用预设:")
            print("-" * 40)
            for name, preset in presets.items():
                description = preset.get("description", "无描述")
                print(name + ": " + description)
        else:
            print("❌ 没有可用的预设")


def main():
    """测试配置管理器"""
    config_manager = ConfigManager()
    
    print("🧪 配置管理器测试")
    print("=" * 50)
    
    # 验证配置
    config_manager.validate_config()
    
    # 显示配置
    config_manager.print_config("TEXT_SEGMENTATION")
    
    # 列出预设
    config_manager.list_presets()
    
    # 测试预设应用
    config_manager.apply_preset("balanced")
    
    # 保存配置
    config_manager.save_config()


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
批量处理模块 - 将长文档分割成多个batch进行处理
"""
import os
import sys
import re
from typing import List, Tuple

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.config_manager import ConfigManager


class BatchProcessor:
    """批量处理器 - 将长文本分割成多个batch"""
    
    def __init__(self, config_manager=None):
        """
        初始化批量处理器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager or ConfigManager()
        self.batch_config = self.config_manager.get_batch_config()
        
        # 批量处理参数
        self.enable_batch = self.batch_config.get("enable_batch_processing", True)
        self.batch_size_chars = self.batch_config.get("batch_size_chars", 15000)
        self.batch_size_tokens = self.batch_config.get("batch_size_tokens", 15000)
        self.batch_overlap_chars = self.batch_config.get("batch_overlap_chars", 200)
        self.min_batch_size = self.batch_config.get("min_batch_size", 5000)
        self.max_batch_size = self.batch_config.get("max_batch_size", 20000)
        
        # 分割策略
        self.split_at_paragraphs = self.batch_config.get("split_at_paragraphs", True)
        self.split_at_chapters = self.batch_config.get("split_at_chapters", True)
        
        # 输出设置
        self.batch_prefix = self.batch_config.get("batch_output_prefix", "batch_")
        self.batch_suffix = self.batch_config.get("batch_output_suffix", "_audiobook.wav")
        self.create_final_merge = self.batch_config.get("create_final_merge", True)
        self.final_output_name = self.batch_config.get("final_output_name", "complete_audiobook.wav")
    
    def split_into_batches(self, text: str) -> List[str]:
        """
        将文本分割成多个batch
        
        Args:
            text: 完整文本
            
        Returns:
            batch文本列表
        """
        if not self.enable_batch:
            return [text]
        
        print(f"\n📦 开始批量分割，目标batch大小: {self.batch_size_tokens} tokens")
        
        # 首先按段落分割
        paragraphs = self._split_into_paragraphs(text)
        print(f"✓ 文本已分割成 {len(paragraphs)} 个段落")
        
        # 然后组合成batch
        batches = self._combine_into_batches(paragraphs)
        print(f"✓ 文本已分割成 {len(batches)} 个batch")
        
        # 显示batch信息
        for i, batch in enumerate(batches, 1):
            estimated_tokens = self._estimate_tokens(batch)
            print(f"  Batch {i}: {len(batch)} 字符, ~{estimated_tokens} tokens")
        
        return batches
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """将文本分割成段落"""
        # 按双换行符分割段落
        paragraphs = re.split(r'\n\s*\n', text)
        
        # 清理空段落
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def _estimate_tokens(self, text: str) -> int:
        """估算文本的token数量（粗略估算：1个token ≈ 4个字符）"""
        return len(text) // 4
    
    def _combine_into_batches(self, paragraphs: List[str]) -> List[str]:
        """将段落组合成batch（基于token数量）"""
        batches = []
        current_batch = ""
        current_tokens = 0
        
        for paragraph in paragraphs:
            paragraph_tokens = self._estimate_tokens(paragraph)
            paragraph_chars = len(paragraph)
            
            # 如果当前段落太大，需要分割
            if paragraph_chars > self.max_batch_size:
                # 先保存当前batch
                if current_batch.strip():
                    batches.append(current_batch.strip())
                    current_batch = ""
                    current_tokens = 0
                
                # 分割大段落
                sub_batches = self._split_large_paragraph(paragraph)
                batches.extend(sub_batches)
                continue
            
            # 检查添加当前段落是否会超过batch token数量
            if current_tokens + paragraph_tokens > self.batch_size_tokens:
                # 保存当前batch
                if current_batch.strip():
                    batches.append(current_batch.strip())
                
                # 开始新batch
                current_batch = paragraph
                current_tokens = paragraph_tokens
            else:
                # 添加到当前batch
                if current_batch:
                    current_batch += "\n\n" + paragraph
                else:
                    current_batch = paragraph
                current_tokens += paragraph_tokens
        
        # 保存最后一个batch
        if current_batch.strip():
            batches.append(current_batch.strip())
        
        # 过滤太小的batch
        filtered_batches = []
        for batch in batches:
            if len(batch) >= self.min_batch_size:
                filtered_batches.append(batch)
            else:
                # 如果batch太小，尝试与前一个batch合并
                if filtered_batches and len(filtered_batches[-1]) + len(batch) <= self.max_batch_size:
                    filtered_batches[-1] += "\n\n" + batch
                else:
                    # 如果无法合并，仍然保留（避免丢失内容）
                    filtered_batches.append(batch)
        
        return filtered_batches
    
    def _split_large_paragraph(self, paragraph: str) -> List[str]:
        """分割过大的段落"""
        if len(paragraph) <= self.max_batch_size:
            return [paragraph]
        
        # 按句子分割
        sentences = re.split(r'[.!?。！？]\s*', paragraph)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        batches = []
        current_batch = ""
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            if current_size + sentence_size > self.max_batch_size:
                if current_batch.strip():
                    batches.append(current_batch.strip())
                current_batch = sentence
                current_size = sentence_size
            else:
                if current_batch:
                    current_batch += ". " + sentence
                else:
                    current_batch = sentence
                current_size += sentence_size
        
        if current_batch.strip():
            batches.append(current_batch.strip())
        
        return batches
    
    def get_batch_output_path(self, batch_index: int, base_name: str = "") -> str:
        """
        获取batch输出文件路径
        
        Args:
            batch_index: batch索引（从1开始）
            base_name: 基础文件名
            
        Returns:
            batch输出文件路径
        """
        if base_name:
            # 移除扩展名
            base_name = os.path.splitext(base_name)[0]
            filename = f"{self.batch_prefix}{base_name}_{batch_index:03d}{self.batch_suffix}"
        else:
            filename = f"{self.batch_prefix}{batch_index:03d}{self.batch_suffix}"
        
        return filename
    
    def get_final_output_path(self, base_name: str = "") -> str:
        """
        获取最终合并文件路径
        
        Args:
            base_name: 基础文件名
            
        Returns:
            最终输出文件路径
        """
        if base_name:
            base_name = os.path.splitext(base_name)[0]
            return f"{base_name}_{self.final_output_name}"
        else:
            return self.final_output_name


def main():
    """测试批量处理器"""
    processor = BatchProcessor()
    
    # 测试文本
    test_text = """
    这是第一段文本。它包含了一些内容。
    
    这是第二段文本。它比第一段要长一些，包含了更多的内容。
    
    这是第三段文本。它非常长，包含了很多内容，用来测试批量分割功能。
    
    这是第四段文本。
    
    这是第五段文本。
    """ * 100  # 重复100次以增加长度
    
    print("🧪 批量处理器测试")
    print("=" * 50)
    print(f"原始文本长度: {len(test_text)} 字符")
    
    batches = processor.split_into_batches(test_text)
    
    print(f"\n✓ 分割完成，共 {len(batches)} 个batch")
    for i, batch in enumerate(batches, 1):
        print(f"  Batch {i}: {len(batch)} 字符")
        print(f"    输出文件: {processor.get_batch_output_path(i, 'test')}")


if __name__ == "__main__":
    main()


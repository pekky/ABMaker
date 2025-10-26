# -*- coding: utf-8 -*-
"""
文本处理模块 - 将长文本分割成适合Bark处理的片段
"""
import re
import nltk
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.config_manager import ConfigManager


# 确保nltk数据已下载
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("正在下载NLTK数据...")
    nltk.download('punkt', quiet=True)


class TextProcessor:
    """文本处理器 - 智能分割文本"""
    
    def __init__(self, max_chars=None, config_manager=None):
        """
        初始化文本处理器
        
        Args:
            max_chars: 每个音频片段的最大字符数（可选，优先使用配置）
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager or ConfigManager()
        self.text_config = self.config_manager.get_text_config()
        
        # 从配置获取参数
        self.min_chars = self.text_config.get("min_chars", 600)
        self.max_chars = self.text_config.get("max_chars", 800)
        self.default_chars = self.text_config.get("default_chars", 700)
        
        # 如果提供了max_chars参数，则使用它（但限制在范围内）
        if max_chars is not None:
            self.max_chars = min(max(max_chars, self.min_chars), self.max_chars)
        else:
            self.max_chars = self.default_chars
    
    def clean_text(self, text):
        """
        清理和规范化文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除多余的换行
        text = re.sub(r'\n+', '\n', text)
        
        # 数字和单位规范化
        if self.text_config.get("normalize_numbers", True):
            text = self._normalize_numbers(text)
        
        # 标点规范化
        if self.text_config.get("normalize_punctuation", True):
            text = self._normalize_punctuation(text)
        
        # 去除首尾空格
        text = text.strip()
        
        return text
    
    def _normalize_numbers(self, text):
        """规范化数字和单位"""
        # 中文数字转阿拉伯数字
        chinese_numbers = {
            '零': '0', '一': '1', '二': '2', '三': '3', '四': '4',
            '五': '5', '六': '6', '七': '7', '八': '8', '九': '9',
            '十': '10', '百': '100', '千': '1000', '万': '10000'
        }
        
        for chinese, arabic in chinese_numbers.items():
            text = text.replace(chinese, arabic)
        
        # 规范化数字格式
        text = re.sub(r'(\d+)\s*([年月日时分秒])', r'\1\2', text)
        text = re.sub(r'(\d+)\s*([%％])', r'\1%', text)
        
        return text
    
    def _normalize_punctuation(self, text):
        """规范化标点符号"""
        # 确保句子结尾有标点
        text = re.sub(r'([^。！？\.!?])\s*$', r'\1。', text)
        
        # 规范化逗号
        text = re.sub(r'[,，]\s*', '，', text)
        
        # 规范化句号
        text = re.sub(r'[。\.]\s*', '。', text)
        
        # 添加韵律注释
        if self.text_config.get("add_rhythm_annotations", True):
            text = self._add_rhythm_annotations(text)
        
        return text
    
    def _add_rhythm_annotations(self, text):
        """添加韵律注释"""
        rhythm_config = self.config_manager.get_rhythm_config()
        
        # 在关键位置添加停顿提示
        if rhythm_config.get("pause_after_comma", True):
            text = re.sub(r'([，,])\s*', r'\1（停顿）', text)
        
        # 在数字串中添加空格
        if rhythm_config.get("add_space_after_numbers", True):
            text = re.sub(r'(\d+)([年月日时分秒])', r'\1 \2', text)
        
        # 在英文缩略词中添加空格
        if rhythm_config.get("add_space_in_abbreviations", True):
            text = re.sub(r'([A-Z]{2,})', r' \1 ', text)
        
        # 在长数字串中添加停顿
        if rhythm_config.get("pause_after_numbers", True):
            text = re.sub(r'(\d{4,})', r'\1（停顿）', text)
        
        return text
    
    def split_into_sentences(self, text):
        """
        将文本分割成句子，优先在句号或换段处分割
        
        Args:
            text: 输入文本
            
        Returns:
            句子列表
        """
        # 先按段落分割
        paragraphs = re.split(r'\n\s*\n', text)
        sentences = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # 在段落内按句号、问号、感叹号分割
            para_sentences = re.split(r'([。！？\.!?]+)', paragraph)
            
            # 重新组合句子和标点
            for i in range(0, len(para_sentences) - 1, 2):
                if i + 1 < len(para_sentences):
                    sentence = para_sentences[i] + para_sentences[i + 1]
                    sentence = sentence.strip()
                    if sentence:
                        sentences.append(sentence)
            
            # 如果最后一个元素没有标点
            if len(para_sentences) % 2 == 1 and para_sentences[-1].strip():
                sentences.append(para_sentences[-1].strip())
        
        return sentences
    
    def split_into_chunks(self, text):
        """
        将文本智能分割成600-800字符的片段，优先在句号或换段处分割
        
        Args:
            text: 输入文本
            
        Returns:
            文本片段列表
        """
        # 首先清理文本
        text = self.clean_text(text)
        
        # 分割成句子
        sentences = self.split_into_sentences(text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # 如果单个句子就超过最大长度，需要进一步分割
            if len(sentence) > self.max_chars:
                # 先保存当前chunk
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # 分割长句子
                sub_chunks = self._split_long_sentence(sentence)
                chunks.extend(sub_chunks)
            else:
                # 检查加入新句子后是否超过限制
                if len(current_chunk) + len(sentence) <= self.max_chars:
                    current_chunk += sentence
                else:
                    # 保存当前chunk，开始新的chunk
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
        
        # 添加最后一个chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # 确保所有chunk都在合理范围内
        final_chunks = []
        for chunk in chunks:
            if len(chunk) >= self.min_chars or len(chunks) == 1:
                final_chunks.append(chunk)
            else:
                # 如果chunk太短，尝试与下一个合并
                if final_chunks and len(final_chunks[-1]) + len(chunk) <= self.max_chars:
                    final_chunks[-1] += chunk
                else:
                    final_chunks.append(chunk)
        
        print("✓ 文本已分割成 " + str(len(final_chunks)) + " 个片段")
        return final_chunks
    
    def _split_long_sentence(self, sentence):
        """
        分割过长的句子
        
        Args:
            sentence: 长句子
            
        Returns:
            分割后的句子片段
        """
        chunks = []
        # 按逗号、分号等分割
        parts = re.split(r'([，,；;、])', sentence)
        
        current_chunk = ""
        for part in parts:
            if len(current_chunk) + len(part) <= self.max_chars:
                current_chunk += part
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = part
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # 如果还是太长，强制按字符数分割
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= self.max_chars:
                final_chunks.append(chunk)
            else:
                # 强制分割
                for i in range(0, len(chunk), self.max_chars):
                    final_chunks.append(chunk[i:i + self.max_chars])
        
        return final_chunks



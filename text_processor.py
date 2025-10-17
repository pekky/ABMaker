"""
文本处理模块 - 将长文本分割成适合Bark处理的片段
"""
import re
import nltk
from typing import List


# 确保nltk数据已下载
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("正在下载NLTK数据...")
    nltk.download('punkt', quiet=True)


class TextProcessor:
    """文本处理器 - 智能分割文本"""
    
    def __init__(self, max_chars: int = 200):
        """
        初始化文本处理器
        
        Args:
            max_chars: 每个音频片段的最大字符数（Bark适合处理~13秒的音频）
        """
        self.max_chars = max_chars
    
    def clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除多余的换行
        text = re.sub(r'\n+', '\n', text)
        # 去除首尾空格
        text = text.strip()
        
        return text
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        将文本分割成句子
        
        Args:
            text: 输入文本
            
        Returns:
            句子列表
        """
        # 使用正则表达式分割中文和英文句子
        # 中文句号、问号、感叹号
        sentences = re.split(r'([。！？\.!?]+)', text)
        
        # 重新组合句子和标点
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
                sentence = sentence.strip()
                if sentence:
                    result.append(sentence)
        
        # 如果最后一个元素没有标点
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1].strip())
        
        return result
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        将文本智能分割成适合Bark处理的片段
        
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
        
        print(f"✓ 文本已分割成 {len(chunks)} 个片段")
        return chunks
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
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



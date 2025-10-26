# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
智能PDF文本提取模块 - 支持页码和段落识别
"""
import pdfplumber
import re
from typing import List, Tuple, Dict


class SmartPDFExtractor:
    """智能PDF文本提取器 - 支持页码和段落识别"""
    
    def __init__(self, pdf_path: str):
        """
        初始化智能PDF提取器
        
        Args:
            pdf_path: PDF文件路径
        """
        self.pdf_path = pdf_path
        self.pages = []
        self.has_page_numbers = False
        self.page_patterns = [
            r'第\s*(\d+)\s*页',
            r'Page\s*(\d+)',
            r'-\s*(\d+)\s*-',
            r'(\d+)\s*/\s*\d+',
            r'第\s*(\d+)\s*章',
            r'Chapter\s*(\d+)',
        ]
    
    def extract_text_with_structure(self) -> Dict:
        """
        提取PDF文本并识别结构
        
        Returns:
            包含页面和段落信息的字典
        """
        pages_data = []
        total_chars = 0
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                print(f"正在智能提取PDF文件，共 {len(pdf.pages)} 页...")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        # 检测页码
                        page_number = self._detect_page_number(text)
                        
                        # 分割段落
                        paragraphs = self._split_paragraphs(text)
                        
                        page_data = {
                            'page_num': page_num,
                            'page_number': page_number,
                            'text': text,
                            'paragraphs': paragraphs,
                            'char_count': len(text)
                        }
                        
                        pages_data.append(page_data)
                        total_chars += len(text)
                        
                        if page_num % 10 == 0:
                            print(f"已处理 {page_num}/{len(pdf.pages)} 页")
        
        except Exception as e:
            raise Exception(f"PDF提取失败: {str(e)}")
        
        # 检测是否有页码
        pages_with_numbers = [p for p in pages_data if p['page_number'] is not None]
        self.has_page_numbers = len(pages_with_numbers) > len(pages_data) * 0.3  # 30%以上有页码
        
        print(f"✓ PDF智能提取完成")
        print(f"✓ 总字符数: {total_chars:,}")
        print(f"✓ 总页数: {len(pages_data)}")
        print(f"✓ 页码检测: {'有' if self.has_page_numbers else '无'}")
        
        return {
            'pages': pages_data,
            'total_chars': total_chars,
            'has_page_numbers': self.has_page_numbers,
            'total_pages': len(pages_data)
        }
    
    def _detect_page_number(self, text: str) -> int:
        """
        检测页面中的页码
        
        Args:
            text: 页面文本
            
        Returns:
            页码数字，如果没有找到返回None
        """
        # 取文本的前200个字符和后200个字符进行页码检测
        text_sample = text[:200] + text[-200:]
        
        for pattern in self.page_patterns:
            matches = re.findall(pattern, text_sample, re.IGNORECASE)
            if matches:
                try:
                    return int(matches[0])
                except ValueError:
                    continue
        
        return None
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """
        将文本分割成段落
        
        Args:
            text: 页面文本
            
        Returns:
            段落列表
        """
        # 按双换行符分割段落
        paragraphs = re.split(r'\n\s*\n', text)
        
        # 清理段落
        cleaned_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if para and len(para) > 10:  # 过滤太短的段落
                cleaned_paragraphs.append(para)
        
        return cleaned_paragraphs
    
    def create_smart_batches(self, target_chars: int = 40000) -> List[Dict]:
        """
        创建智能批次 - 按4万字符分批，保证完整页面或段落
        
        Args:
            target_chars: 目标批次字符数
            
        Returns:
            批次列表
        """
        structure_data = self.extract_text_with_structure()
        pages = structure_data['pages']
        
        batches = []
        current_batch = {
            'pages': [],
            'paragraphs': [],
            'char_count': 0,
            'start_page': None,
            'end_page': None,
            'start_para': None,
            'end_para': None
        }
        
        print(f"\n开始创建智能批次（目标: {target_chars:,}字符）...")
        
        for page_idx, page_data in enumerate(pages):
            page_text = page_data['text']
            page_chars = len(page_text)
            
            # 如果添加当前页会超过目标字符数
            if current_batch['char_count'] + page_chars > target_chars and current_batch['pages']:
                # 完成当前批次
                current_batch['end_page'] = current_batch['pages'][-1]['page_num']
                batches.append(current_batch.copy())
                
                # 开始新批次
                current_batch = {
                    'pages': [page_data],
                    'paragraphs': page_data['paragraphs'].copy(),
                    'char_count': page_chars,
                    'start_page': page_data['page_num'],
                    'end_page': None,
                    'start_para': 0,
                    'end_para': len(page_data['paragraphs']) - 1
                }
            else:
                # 添加当前页到批次
                if not current_batch['pages']:
                    current_batch['start_page'] = page_data['page_num']
                    current_batch['start_para'] = 0
                
                current_batch['pages'].append(page_data)
                current_batch['paragraphs'].extend(page_data['paragraphs'])
                current_batch['char_count'] += page_chars
                current_batch['end_page'] = page_data['page_num']
                current_batch['end_para'] = len(current_batch['paragraphs']) - 1
        
        # 添加最后一个批次
        if current_batch['pages']:
            batches.append(current_batch)
        
        print(f"✓ 智能批次创建完成，共 {len(batches)} 批")
        
        # 打印批次信息
        for i, batch in enumerate(batches, 1):
            if self.has_page_numbers:
                print(f"批次 {i}: 第{batch['start_page']}-{batch['end_page']}页, "
                      f"{batch['char_count']:,}字符 ({batch['char_count']/10000:.1f}万字)")
            else:
                print(f"批次 {i}: 第{batch['start_page']}-{batch['end_page']}页, "
                      f"{len(batch['paragraphs'])}个段落, "
                      f"{batch['char_count']:,}字符 ({batch['char_count']/10000:.1f}万字)")
        
        return batches
    
    def get_batch_text(self, batch: Dict) -> str:
        """
        获取批次的完整文本
        
        Args:
            batch: 批次数据
            
        Returns:
            批次的完整文本
        """
        if self.has_page_numbers:
            # 有页码：按页面合并
            texts = [page['text'] for page in batch['pages']]
            return '\n\n'.join(texts)
        else:
            # 无页码：按段落合并
            return '\n\n'.join(batch['paragraphs'])
    
    def extract_text_by_pages(self) -> List[str]:
        """
        按页面提取文本（兼容性方法）
        
        Returns:
            页面文本列表
        """
        structure_data = self.extract_text_with_structure()
        return [page['text'] for page in structure_data['pages']]
    
    def extract_text(self) -> str:
        """
        提取所有文本（兼容性方法）
        
        Returns:
            完整文本
        """
        structure_data = self.extract_text_with_structure()
        return '\n\n'.join([page['text'] for page in structure_data['pages']])


# 兼容性类
class PDFExtractor(SmartPDFExtractor):
    """兼容性PDF提取器"""
    pass

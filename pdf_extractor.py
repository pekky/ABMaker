"""
PDF文本提取模块
"""
import pdfplumber
from typing import List


class PDFExtractor:
    """PDF文本提取器"""
    
    def __init__(self, pdf_path: str):
        """
        初始化PDF提取器
        
        Args:
            pdf_path: PDF文件路径
        """
        self.pdf_path = pdf_path
    
    def extract_text(self) -> str:
        """
        从PDF文件中提取所有文本
        
        Returns:
            提取的文本内容
        """
        text_content = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                print(f"正在提取PDF文件，共 {len(pdf.pages)} 页...")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                    
                    if page_num % 10 == 0:
                        print(f"已处理 {page_num}/{len(pdf.pages)} 页")
        
        except Exception as e:
            raise Exception(f"PDF提取失败: {str(e)}")
        
        full_text = "\n\n".join(text_content)
        print(f"✓ PDF文本提取完成，共 {len(full_text)} 个字符")
        
        return full_text
    
    def extract_text_by_pages(self) -> List[str]:
        """
        按页提取PDF文本
        
        Returns:
            每页的文本列表
        """
        pages_text = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages_text.append(text)
        
        except Exception as e:
            raise Exception(f"PDF提取失败: {str(e)}")
        
        return pages_text



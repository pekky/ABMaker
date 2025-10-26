# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
文档选择工具
"""
import os
import glob
from typing import List, Optional


class DocumentSelector:
    """文档选择器"""
    
    def __init__(self, docs_dir: str = "docs"):
        """
        初始化文档选择器
        
        Args:
            docs_dir: 文档目录路径
        """
        self.docs_dir = docs_dir
        self.supported_formats = ['.pdf', '.txt', '.docx', '.doc']
    
    def get_available_documents(self) -> List[dict]:
        """
        获取可用的文档列表
        
        Returns:
            文档信息列表，每个元素包含 {'name': str, 'path': str, 'size': int}
        """
        documents = []
        
        if not os.path.exists(self.docs_dir):
            return documents
        
        for ext in self.supported_formats:
            pattern = os.path.join(self.docs_dir, f"*{ext}")
            files = glob.glob(pattern)
            
            for file_path in files:
                if os.path.isfile(file_path):
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    documents.append({
                        'name': file_name,
                        'path': file_path,
                        'size': file_size,
                        'extension': ext
                    })
        
        # 按文件名排序
        documents.sort(key=lambda x: x['name'])
        return documents
    
    def format_file_size(self, size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes: 文件大小（字节）
            
        Returns:
            格式化后的文件大小字符串
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def display_documents(self) -> None:
        """显示可用文档列表"""
        documents = self.get_available_documents()
        
        if not documents:
            print(f"❌ 在 {self.docs_dir} 目录中未找到支持的文档")
            print(f"支持的格式: {', '.join(self.supported_formats)}")
            return
        
        print(f"\n📚 可用的文档 (共 {len(documents)} 个):")
        print("=" * 80)
        print(f"{'序号':<4} {'文件名':<40} {'大小':<12} {'格式':<6}")
        print("-" * 80)
        
        for i, doc in enumerate(documents, 1):
            size_str = self.format_file_size(doc['size'])
            ext = doc['extension'].upper()
            print(f"{i:<4} {doc['name']:<40} {size_str:<12} {ext:<6}")
        
        print("=" * 80)
    
    def select_document(self) -> Optional[str]:
        """
        交互式选择文档
        
        Returns:
            选中的文档路径，如果取消则返回None
        """
        documents = self.get_available_documents()
        
        if not documents:
            print(f"❌ 在 {self.docs_dir} 目录中未找到支持的文档")
            return None
        
        while True:
            self.display_documents()
            
            try:
                choice = input(f"\n请选择要转录的文档 (1-{len(documents)}, 或输入 'q' 退出): ").strip()
                
                if choice.lower() == 'q':
                    print("已取消选择")
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(documents):
                    selected_doc = documents[choice_num - 1]
                    print(f"\n✅ 已选择: {selected_doc['name']}")
                    return selected_doc['path']
                else:
                    print(f"❌ 请输入 1 到 {len(documents)} 之间的数字")
                    
            except ValueError:
                print("❌ 请输入有效的数字或 'q' 退出")
            except KeyboardInterrupt:
                print("\n\n已取消选择")
                return None
    
    def get_document_by_name(self, name: str) -> Optional[str]:
        """
        根据文件名获取文档路径
        
        Args:
            name: 文件名
            
        Returns:
            文档路径，如果未找到则返回None
        """
        documents = self.get_available_documents()
        
        for doc in documents:
            if doc['name'] == name:
                return doc['path']
        
        return None


def main():
    """测试文档选择器"""
    selector = DocumentSelector()
    selected_path = selector.select_document()
    
    if selected_path:
        print(f"选中的文档路径: {selected_path}")
    else:
        print("未选择任何文档")


if __name__ == "__main__":
    main()


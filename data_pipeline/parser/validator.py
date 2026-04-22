"""文件校验器
功能：校验文件格式和完整性
作者：
创建时间：
"""
import os
import magic
from typing import Optional

from common_lib.logging.logger import get_logger
from common_lib.exceptions.base_exceptions import DocumentParseException

logger = get_logger(__name__)


class Validator:
    """文件校验器"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Validator, cls).__new__(cls)
        return cls._instance
    
    def validate_file(self, file_path: str) -> bool:
        """校验文件
        参数：file_path - 文件路径
        返回：是否有效
        被调用：mineru_parser.validate_and_parse()
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise DocumentParseException(f"文件不存在: {file_path}")
        
        # 检查文件是否可读
        if not os.path.isfile(file_path):
            raise DocumentParseException(f"路径不是文件: {file_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise DocumentParseException("文件为空")
        
        # 检查文件格式
        allowed_extensions = {'.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.md'}
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in allowed_extensions:
            raise DocumentParseException(f"不支持的文件格式: {ext}")
        
        # 检查文件头（简化版）
        try:
            with open(file_path, 'rb') as f:
                header = f.read(12)
                
            # 简单的文件头检查
            if ext == '.pdf' and header[:4] != b'%PDF':
                raise DocumentParseException("PDF文件格式无效")
            elif ext == '.docx' and header[:2] != b'PK':
                raise DocumentParseException("DOCX文件格式无效")
            elif ext == '.xlsx' and header[:2] != b'PK':
                raise DocumentParseException("XLSX文件格式无效")
            elif ext == '.pptx' and header[:2] != b'PK':
                raise DocumentParseException("PPTX文件格式无效")
        except Exception as e:
            logger.error(f"文件头检查失败: {e}")
            raise DocumentParseException(f"文件格式检查失败: {str(e)}")
        
        logger.info(f"文件{file_path}校验通过")
        return True


# 全局校验器实例
validator = Validator()
"""文本工具类
功能：提供文本处理相关的工具方法
作者：
创建时间：
"""
import re


def clean_extra_spaces(text: str) -> str:
    """清洗多余空格和换行
    参数：text - 原始文本
    返回：清洗后的文本
    被调用：mineru_parser.parse_single_file()
    """
    # 替换多个空格为单个空格
    text = re.sub(r'\s+', ' ', text)
    # 替换多个换行为单个换行
    text = re.sub(r'\n+', '\n', text)
    # 移除首尾空白
    text = text.strip()
    return text


def truncate_text(text: str, max_length: int) -> str:
    """截断文本
    参数：text - 原始文本；max_length - 最大长度
    返回：截断后的文本
    被调用：embedding_service.generate_batch()
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'


def split_by_paragraph(text: str) -> list:
    """按段落分割文本
    参数：text - 原始文本
    返回：段落列表
    被调用：fixed_chunker.chunk()
    """
    paragraphs = text.split('\n')
    # 过滤空段落
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    return paragraphs
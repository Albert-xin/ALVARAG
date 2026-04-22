"""Markdown标题分块器
功能：按Markdown标题对文本进行分块
作者：
创建时间：
"""
import re
from typing import List, Dict, Any

from common_lib.logging.logger import get_logger

logger = get_logger(__name__)


class MarkdownChunker:
    """Markdown标题分块器"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarkdownChunker, cls).__new__(cls)
        return cls._instance
    
    def chunk(self, markdown_text: str) -> List[Dict[str, Any]]:
        """Markdown分块
        参数：markdown_text - Markdown文本
        返回：分块列表
        被调用：ingest_service.process_document()
        """
        if not markdown_text:
            return []
        
        # 匹配标题行
        lines = markdown_text.split('\n')
        chunks = []
        current_chunk = []
        current_header = None
        current_level = 0
        
        for line in lines:
            # 匹配标题
            header_match = re.match(r'^(#{1,6})\s+(.*)$', line)
            if header_match:
                # 保存当前块
                if current_chunk:
                    chunks.append({
                        'content': '\n'.join(current_chunk),
                        'header': current_header,
                        'level': current_level
                    })
                    current_chunk = []
                
                # 新标题
                level = len(header_match.group(1))
                header = header_match.group(2)
                current_header = header
                current_level = level
                current_chunk.append(line)
            else:
                # 普通行
                current_chunk.append(line)
        
        # 处理最后一个块
        if current_chunk:
            chunks.append({
                'content': '\n'.join(current_chunk),
                'header': current_header,
                'level': current_level
            })
        
        # 合并短块，拆分长块
        processed_chunks = []
        for chunk in chunks:
            content = chunk['content']
            if len(content) < 100:
                # 短块，尝试合并到前一个块
                if processed_chunks:
                    processed_chunks[-1]['content'] += '\n' + content
                else:
                    processed_chunks.append(chunk)
            else:
                # 长块，拆分
                lines = content.split('\n')
                current_content = []
                for line in lines:
                    if len('\n'.join(current_content)) + len(line) > 1000:
                        processed_chunks.append({
                            'content': '\n'.join(current_content),
                            'header': chunk['header'],
                            'level': chunk['level']
                        })
                        current_content = [line]
                    else:
                        current_content.append(line)
                if current_content:
                    processed_chunks.append({
                        'content': '\n'.join(current_content),
                        'header': chunk['header'],
                        'level': chunk['level']
                    })
        
        logger.info(f"Markdown分块完成，共{len(processed_chunks)}个块")
        return processed_chunks


# 全局Markdown分块器实例
markdown_chunker = MarkdownChunker()
"""固定长度分块器
功能：按固定长度对文本进行分块
作者：
创建时间：
"""
from typing import List, Dict, Any

from common_lib.logging.logger import get_logger
from common_lib.utils.text_utils import split_by_paragraph

logger = get_logger(__name__)


class FixedChunker:
    """固定长度分块器"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FixedChunker, cls).__new__(cls)
        return cls._instance
    
    def chunk(self, text: str, chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
        """分块
        参数：text - 文本；chunk_size - 分块大小；overlap - 重叠大小
        返回：分块列表
        被调用：ingest_service.process_document()
        """
        if not text:
            return []
        
        # 按段落分割
        paragraphs = split_by_paragraph(text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for paragraph in paragraphs:
            paragraph_length = len(paragraph)
            
            # 如果当前段落长度超过分块大小，单独成块
            if paragraph_length > chunk_size:
                # 处理当前积累的块
                if current_chunk:
                    chunks.append({
                        'content': ' '.join(current_chunk),
                        'start_idx': 0,  # 简化处理
                        'end_idx': current_length
                    })
                    current_chunk = []
                    current_length = 0
                
                # 分割长段落
                start = 0
                while start < paragraph_length:
                    end = min(start + chunk_size, paragraph_length)
                    chunks.append({
                        'content': paragraph[start:end],
                        'start_idx': start,
                        'end_idx': end
                    })
                    start = end - overlap
            else:
                # 检查添加当前段落是否会超过分块大小
                if current_length + paragraph_length > chunk_size:
                    # 保存当前块
                    chunks.append({
                        'content': ' '.join(current_chunk),
                        'start_idx': 0,  # 简化处理
                        'end_idx': current_length
                    })
                    # 开始新块，包含重叠部分
                    current_chunk = current_chunk[-overlap//10:] if overlap > 0 else []
                    current_length = sum(len(p) for p in current_chunk)
                
                # 添加当前段落
                current_chunk.append(paragraph)
                current_length += paragraph_length
        
        # 处理最后一个块
        if current_chunk:
            chunks.append({
                'content': ' '.join(current_chunk),
                'start_idx': 0,  # 简化处理
                'end_idx': current_length
            })
        
        logger.info(f"文本分块完成，共{len(chunks)}个块")
        return chunks


# 全局固定分块器实例
fixed_chunker = FixedChunker()
"""语义分块器
功能：基于语义对文本进行分块
作者：
创建时间：
"""
from typing import List, Dict, Any

from model_service.embedding.embedding_service import embedding_service
from common_lib.logging.logger import get_logger
from common_lib.utils.text_utils import split_by_paragraph

logger = get_logger(__name__)


class SemanticChunker:
    """语义分块器"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticChunker, cls).__new__(cls)
        return cls._instance
    
    def chunk(self, text: str) -> List[Dict[str, Any]]:
        """语义分块
        参数：text - 文本
        返回：分块列表
        被调用：ingest_service.process_document()
        """
        if not text:
            return []
        
        # 按句子分割（简化处理，实际应使用NLP工具）
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return []
        
        # 生成句向量
        embeddings = embedding_service.generate_batch(sentences)
        
        # 计算句子间相似度
        similarities = []
        for i in range(len(sentences) - 1):
            # 简化的相似度计算
            sim = sum([a*b for a, b in zip(embeddings[i], embeddings[i+1])])
            similarities.append(sim)
        
        # 找到分割点
        threshold = 0.5  # 相似度阈值
        split_points = [i+1 for i, sim in enumerate(similarities) if sim < threshold]
        
        # 生成分块
        chunks = []
        start = 0
        for split_point in split_points:
            chunk_content = '. '.join(sentences[start:split_point]) + '.'
            chunks.append({
                'content': chunk_content,
                'semantic_label': f'chunk_{len(chunks)}'
            })
            start = split_point
        
        # 处理最后一个块
        if start < len(sentences):
            chunk_content = '. '.join(sentences[start:]) + '.'
            chunks.append({
                'content': chunk_content,
                'semantic_label': f'chunk_{len(chunks)}'
            })
        
        logger.info(f"语义分块完成，共{len(chunks)}个块")
        return chunks


# 全局语义分块器实例
semantic_chunker = SemanticChunker()
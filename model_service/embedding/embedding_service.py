"""向量化服务
功能：提供文本向量化功能
作者：
创建时间：
"""
import numpy as np
from typing import List, Optional

from model_service.common.model_loader import model_loader
from model_service.common.model_config import get_model_config, get_batch_config
from common_lib.logging.logger import get_logger
from common_lib.utils.text_utils import truncate_text

logger = get_logger(__name__)


class EmbeddingService:
    """向量化服务"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance
    
    def init(self, device: Optional[str] = None):
        """初始化向量化服务
        参数：device - 设备
        被调用：rag_service / ingest_service
        """
        config = get_model_config('embedding')
        if device:
            config['device'] = device
        
        self.model = model_loader.load_model('embedding', config['model_path'], config['device'])
        self.max_length = config['max_length']
        self.batch_size = get_batch_config('embedding')['batch_size']
        logger.info("向量化服务初始化完成")
    
    def generate_single(self, text: str) -> List[float]:
        """生成单个文本的向量
        参数：text - 文本
        返回：向量
        被调用：rag_service.chat()
        """
        # 文本预处理
        text = truncate_text(text, self.max_length)
        # 模拟向量生成
        vector = [0.0] * 768  # 假设向量维度为768
        logger.info(f"生成文本向量: {text[:50]}...")
        return vector
    
    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成文本向量
        参数：texts - 文本列表
        返回：向量列表
        被调用：ingest_service.process_document()
        """
        vectors = []
        # 分批处理
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i+self.batch_size]
            # 文本预处理
            batch_texts = [truncate_text(text, self.max_length) for text in batch_texts]
            # 模拟批量向量生成
            batch_vectors = [[0.0] * 768 for _ in batch_texts]
            vectors.extend(batch_vectors)
        logger.info(f"批量生成{len(texts)}个文本向量")
        return vectors


# 全局向量化服务实例
embedding_service = EmbeddingService()
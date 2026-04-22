"""重排序服务
功能：提供文本重排序功能
作者：
创建时间：
"""
from typing import List, Dict, Any

from model_service.common.model_loader import model_loader
from model_service.common.model_config import get_model_config
from common_lib.logging.logger import get_logger

logger = get_logger(__name__)


class RerankService:
    """重排序服务"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RerankService, cls).__new__(cls)
        return cls._instance
    
    def init(self):
        """初始化重排序服务"""
        config = get_model_config('rerank')
        self.model = model_loader.load_model('rerank', config['model_path'], config['device'])
        self.max_length = config['max_length']
        logger.info("重排序服务初始化完成")
    
    def rerank(self, query: str, documents: List[str], top_k: int) -> List[Dict[str, Any]]:
        """重排序文档
        参数：query - 查询文本；documents - 文档列表；top_k - 返回数量
        返回：排序后的文档列表
        被调用：rag_service.retrieve_rerank()
        """
        # 模拟重排序
        results = []
        for i, doc in enumerate(documents):
            # 模拟相关性分数
            score = (len(doc) % 10) / 10.0
            results.append({
                'document': doc,
                'score': score,
                'index': i
            })
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        # 返回前top_k个结果
        logger.info(f"重排序完成，返回前{top_k}个结果")
        return results[:top_k]


# 全局重排序服务实例
rerank_service = RerankService()
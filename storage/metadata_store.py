"""文档元数据存储
功能：存储和管理文档元数据
作者：
创建时间：
"""
import time
from typing import List, Dict, Any, Optional

from common_lib.logging.logger import get_logger

logger = get_logger(__name__)


class MetadataStore:
    """元数据存储"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetadataStore, cls).__new__(cls)
            cls._instance._init_store()
        return cls._instance
    
    def _init_store(self):
        """初始化存储"""
        # 模拟元数据存储
        self.metadata = {}
        logger.info("元数据存储初始化完成")
    
    def save_metadata(self, doc_id: str, file_info: Dict[str, Any], status: str):
        """保存文档元数据
        参数：doc_id - 文档ID；file_info - 文件信息；status - 状态
        被调用：ingest_service.process_document()
        """
        self.metadata[doc_id] = {
            'doc_id': doc_id,
            'file_name': file_info.get('file_name'),
            'file_size': file_info.get('file_size'),
            'page_count': file_info.get('page_count', 0),
            'chunk_count': file_info.get('chunk_count', 0),
            'upload_time': time.time(),
            'status': status,
            'processing_time': file_info.get('processing_time', 0),
            'error_message': file_info.get('error_message', '')
        }
        logger.info(f"保存文档{doc_id}的元数据")
    
    def get_metadata(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """获取文档元数据
        参数：doc_id - 文档ID
        返回：元数据
        被调用：document_service.get_document_detail()
        """
        return self.metadata.get(doc_id)
    
    def list_documents(self, filter: Dict[str, Any], page: int, size: int) -> Dict[str, Any]:
        """列出文档
        参数：filter - 过滤条件；page - 页码；size - 每页大小
        返回：文档列表和总数
        被调用：document_service.list_documents()
        """
        # 过滤文档
        filtered_docs = []
        for doc_id, data in self.metadata.items():
            # 应用过滤条件
            match = True
            if 'status' in filter and data['status'] != filter['status']:
                match = False
            if 'kb_id' in filter:  # 假设每个文档都属于某个知识库
                match = True  # 简化处理
            if match:
                filtered_docs.append(data)
        
        # 排序
        filtered_docs.sort(key=lambda x: x['upload_time'], reverse=True)
        
        # 分页
        total = len(filtered_docs)
        start = (page - 1) * size
        end = start + size
        paginated_docs = filtered_docs[start:end]
        
        logger.info(f"列出文档，共{total}个，第{page}页")
        return {
            'total': total,
            'docs': paginated_docs
        }


# 全局元数据存储实例
metadata_store = MetadataStore()
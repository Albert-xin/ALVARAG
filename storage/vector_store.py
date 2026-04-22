"""向量库存储
功能：提供向量存储和检索功能，基于Milvus向量数据库
作者：
创建时间：
"""
from typing import List, Dict, Any
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

from common_lib.logging.logger import get_logger
from common_lib.exceptions.base_exceptions import VectorStoreException
from common_lib.config.settings import settings

logger = get_logger(__name__)


class VectorStore:
    """向量库存储，基于Milvus"""
    _instance = None
    _collection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            cls._instance._init_store()
        return cls._instance
    
    def _init_store(self):
        """初始化存储"""
        milvus_config = settings.get('milvus', {})
        self.host = milvus_config.get('host', 'localhost')
        self.port = milvus_config.get('port', 19530)
        self.user = milvus_config.get('user', 'root')
        self.password = milvus_config.get('password', 'milvus')
        self.database = milvus_config.get('database', 'default')
        self.collection_name = milvus_config.get('collection', 'document_vectors')
        
        self._connect()
        self._setup_collection()
        logger.info("Milvus向量库存储初始化完成")
    
    def _connect(self):
        """连接到Milvus服务器"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db_name=self.database
            )
            logger.info(f"已连接到Milvus服务器 {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"连接Milvus服务器失败: {e}")
            raise VectorStoreException(f"连接Milvus服务器失败: {e}")
    
    def _setup_collection(self):
        """创建或获取Collection"""
        try:
            if utility.has_collection(self.collection_name):
                self._collection = Collection(self.collection_name)
                self._collection.load()
                logger.info(f"已加载Collection: {self.collection_name}")
            else:
                dim = settings.get('embedding.max_length', 512)
                
                fields = [
                    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=256, is_primary=True, auto_id=True),
                    FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=128),
                    FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=256),
                    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4096),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
                    FieldSchema(name="page", dtype=DataType.INT32)
                ]
                
                schema = CollectionSchema(fields, description="文档向量集合")
                self._collection = Collection(name=self.collection_name, schema=schema)
                
                index_params = {
                    "metric_type": "IP",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128}
                }
                self._collection.create_index(field_name="embedding", index_params=index_params)
                logger.info(f"已创建Collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"设置Collection失败: {e}")
            raise VectorStoreException(f"设置Collection失败: {e}")
    
    def batch_insert(self, chunks: List[str], embeddings: List[List[float]], doc_id: str):
        """批量插入向量
        参数：chunks - 文本分块；embeddings - 向量；doc_id - 文档ID
        被调用：ingest_service.process_document()
        """
        try:
            entities = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                entities.append({
                    "doc_id": doc_id,
                    "chunk_id": f"{doc_id}_chunk{i}",
                    "content": chunk,
                    "embedding": embedding,
                    "page": i % 10 + 1
                })
            
            self._collection.insert(entities)
            self._collection.flush()
            logger.info(f"批量插入{len(chunks)}个向量到Milvus")
        except Exception as e:
            logger.error(f"批量插入向量失败: {e}")
            raise VectorStoreException(str(e))
    
    def search(self, query_embedding: List[float], top_k: int, kb_ids: List[str] = None) -> List[Dict[str, Any]]:
        """向量搜索
        参数：query_embedding - 查询向量；top_k - 返回数量；kb_ids - 知识库ID列表
        返回：搜索结果
        被调用：rag_service.retrieve()
        """
        try:
            search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
            
            expr = None
            if kb_ids:
                kb_list = ",".join([f'"{kb_id}"' for kb_id in kb_ids])
                expr = f'doc_id in [{kb_list}]'
            
            results = self._collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=expr,
                output_fields=["doc_id", "chunk_id", "content", "page"]
            )
            
            search_results = []
            if results and len(results) > 0:
                for hit in results[0]:
                    search_results.append({
                        'score': float(hit.score),
                        'doc_id': hit.entity.get('doc_id'),
                        'chunk_id': hit.entity.get('chunk_id'),
                        'content': hit.entity.get('content'),
                        'page': hit.entity.get('page')
                    })
            
            logger.info(f"Milvus搜索完成，返回前{len(search_results)}个结果")
            return search_results
        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            raise VectorStoreException(str(e))
    
    def delete_by_doc_id(self, doc_id: str):
        """根据文档ID删除向量
        参数：doc_id - 文档ID
        被调用：document_service.delete_document()
        """
        try:
            expr = f'doc_id == "{doc_id}"'
            self._collection.delete(expr)
            self._collection.flush()
            logger.info(f"删除文档{doc_id}的向量")
        except Exception as e:
            logger.error(f"删除向量失败: {e}")
            raise VectorStoreException(str(e))
    
    def close(self):
        """关闭连接"""
        try:
            connections.disconnect("default")
            logger.info("已断开Milvus连接")
        except Exception as e:
            logger.error(f"关闭Milvus连接失败: {e}")


vector_store = VectorStore()

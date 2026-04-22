"""文档入库服务
功能：处理文档解析、分块、向量化和入库
作者：
创建时间：
"""
import time
from typing import List, Dict, Any

from data_pipeline.parser.mineru_parser import mineru_parser
from data_pipeline.chunker.fixed_chunker import fixed_chunker
from data_pipeline.monitor.pipeline_monitor import pipeline_monitor
from model_service.embedding.embedding_service import embedding_service
from storage.vector_store import vector_store
from storage.metadata_store import metadata_store
from common_lib.logging.logger import get_logger
from common_lib.exceptions.base_exceptions import DocumentParseException
from common_lib.utils.file_utils import delete_temp_files

logger = get_logger(__name__)


class IngestService:
    """文档入库服务"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IngestService, cls).__new__(cls)
        return cls._instance
    
    def process_document(self, file_path: str, doc_id: str) -> Dict[str, Any]:
        """处理单个文档
        参数：file_path - 文件路径；doc_id - 文档ID
        返回：处理结果
        被调用：task_executor.run_task()
        """
        start_time = time.time()
        result = {
            'doc_id': doc_id,
            'status': 'success',
            'error': None
        }
        
        try:
            # 1. 解析文档
            pipeline_monitor.start_monitor(doc_id, 'parse')
            parse_result = mineru_parser.validate_and_parse(file_path)
            pipeline_monitor.end_monitor(doc_id, 'parse')
            
            # 2. 分块
            pipeline_monitor.start_monitor(doc_id, 'chunk')
            chunks = fixed_chunker.chunk(parse_result['text'], 512, 128)
            pipeline_monitor.end_monitor(doc_id, 'chunk')
            
            # 3. 向量化
            pipeline_monitor.start_monitor(doc_id, 'embed')
            chunk_texts = [chunk['content'] for chunk in chunks]
            embeddings = embedding_service.generate_batch(chunk_texts)
            pipeline_monitor.end_monitor(doc_id, 'embed')
            
            # 4. 入库
            pipeline_monitor.start_monitor(doc_id, 'store')
            vector_store.batch_insert(chunk_texts, embeddings, doc_id)
            
            # 保存元数据
            file_info = {
                'file_name': parse_result['metadata']['file_name'],
                'file_size': 0,  # 简化处理
                'page_count': parse_result['metadata']['page_count'],
                'chunk_count': len(chunks),
                'processing_time': time.time() - start_time
            }
            metadata_store.save_metadata(doc_id, file_info, 'completed')
            pipeline_monitor.end_monitor(doc_id, 'store')
            
            logger.info(f"文档{doc_id}处理完成")
        except Exception as e:
            error_msg = str(e)
            result['status'] = 'failed'
            result['error'] = error_msg
            
            # 保存失败状态
            file_info = {
                'file_name': file_path,
                'error_message': error_msg
            }
            metadata_store.save_metadata(doc_id, file_info, 'failed')
            
            logger.error(f"文档{doc_id}处理失败: {error_msg}")
        finally:
            # 清理临时文件
            delete_temp_files()
        
        return result
    
    def batch_process(self, file_paths: List[str]) -> Dict[str, Any]:
        """批量处理文档
        参数：file_paths - 文件路径列表
        返回：处理结果
        被调用：task_executor.run_task()
        """
        results = {}
        success_count = 0
        failure_count = 0
        
        for file_path in file_paths:
            # 生成doc_id（简化处理）
            doc_id = f"doc_{int(time.time())}_{len(results)}"
            result = self.process_document(file_path, doc_id)
            results[file_path] = result
            
            if result['status'] == 'success':
                success_count += 1
            else:
                failure_count += 1
        
        logger.info(f"批量处理完成，成功{success_count}个，失败{failure_count}个")
        return {
            'results': results,
            'success_count': success_count,
            'failure_count': failure_count
        }


# 全局入库服务实例
ingest_service = IngestService()
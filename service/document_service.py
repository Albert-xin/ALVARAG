"""文档服务
功能：提供文档管理相关的业务逻辑
作者：
创建时间：
"""
import os
import time
import uuid
from typing import List, Dict, Any

from task_scheduler.store.task_store import task_store
from task_scheduler.executor.task_executor import task_executor
from storage.vector_store import vector_store
from storage.metadata_store import metadata_store
from common_lib.logging.logger import get_logger
from common_lib.exceptions.base_exceptions import BusinessException
from common_lib.utils.file_utils import calculate_file_md5

logger = get_logger(__name__)


class DocumentService:
    """文档服务"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DocumentService, cls).__new__(cls)
        return cls._instance
    
    def upload(self, file_paths: List[str]) -> Dict[str, Any]:
        """上传文档
        参数：file_paths - 文件路径列表
        返回：上传结果
        被调用：document_api.upload_document()
        """
        try:
            tasks = []
            file_list = []
            
            for file_path in file_paths:
                # 生成doc_id
                doc_id = f"doc_{str(uuid.uuid4())[:8]}"
                # 计算文件MD5
                md5 = calculate_file_md5(file_path)
                # 生成task_id
                task_id = f"task_{str(uuid.uuid4())[:8]}"
                
                # 创建任务
                task_info = {
                    'task_id': task_id,
                    'type': 'parse_document',
                    'doc_id': doc_id,
                    'file_path': file_path,
                    'status': 'waiting',
                    'created_at': time.time()
                }
                task_store.save_task(task_id, task_info)
                
                # 提交任务到执行器
                task_executor.run_task(task_id, task_info)
                
                tasks.append(task_id)
                file_list.append({
                    'file_name': os.path.basename(file_path),
                    'doc_id': doc_id,
                    'task_id': task_id,
                    'md5': md5
                })
            
            logger.info(f"上传文档完成，共{len(file_paths)}个文件")
            return {
                'task_ids': tasks,
                'files': file_list
            }
        except Exception as e:
            logger.error(f"上传文档失败: {e}")
            raise BusinessException(f"上传文档失败: {str(e)}")
    
    def list_documents(self, filter: Dict[str, Any], page: int, size: int) -> Dict[str, Any]:
        """列出文档
        参数：filter - 过滤条件；page - 页码；size - 每页大小
        返回：文档列表
        被调用：document_api.list_documents()
        """
        try:
            result = metadata_store.list_documents(filter, page, size)
            logger.info(f"列出文档，共{result['total']}个")
            return result
        except Exception as e:
            logger.error(f"列出文档失败: {e}")
            raise BusinessException(f"列出文档失败: {str(e)}")
    
    def get_document_detail(self, doc_id: str) -> Dict[str, Any]:
        """获取文档详情
        参数：doc_id - 文档ID
        返回：文档详情
        被调用：document_api.get_document_detail()
        """
        try:
            metadata = metadata_store.get_metadata(doc_id)
            if not metadata:
                raise BusinessException(f"文档不存在: {doc_id}")
            logger.info(f"获取文档详情: {doc_id}")
            return metadata
        except Exception as e:
            logger.error(f"获取文档详情失败: {e}")
            raise BusinessException(f"获取文档详情失败: {str(e)}")
    
    def delete_document(self, doc_id: str) -> bool:
        """删除文档
        参数：doc_id - 文档ID
        返回：是否成功
        被调用：document_api.delete_document()
        """
        try:
            # 删除向量
            vector_store.delete_by_doc_id(doc_id)
            # 删除元数据（简化处理，实际应从metadata_store中删除）
            # 这里需要实现metadata_store的删除方法
            logger.info(f"删除文档: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            raise BusinessException(f"删除文档失败: {str(e)}")
    
    def reprocess_document(self, doc_id: str, file_path: str) -> str:
        """重新处理文档
        参数：doc_id - 文档ID；file_path - 文件路径
        返回：任务ID
        被调用：document_api.reprocess_document()
        """
        try:
            # 生成task_id
            task_id = f"task_{str(uuid.uuid4())[:8]}"
            
            # 创建任务
            task_info = {
                'task_id': task_id,
                'type': 'reprocess_document',
                'doc_id': doc_id,
                'file_path': file_path,
                'status': 'waiting',
                'created_at': time.time()
            }
            task_store.save_task(task_id, task_info)
            
            # 提交任务到执行器
            task_executor.run_task(task_id, task_info)
            
            logger.info(f"重新处理文档: {doc_id}")
            return task_id
        except Exception as e:
            logger.error(f"重新处理文档失败: {e}")
            raise BusinessException(f"重新处理文档失败: {str(e)}")


# 全局文档服务实例
document_service = DocumentService()
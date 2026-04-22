"""任务服务
功能：提供任务管理相关的业务逻辑
作者：
创建时间：
"""
import time
import uuid
from typing import Dict, Any, List

from task_scheduler.store.task_store import task_store
from task_scheduler.executor.task_executor import task_executor
from task_scheduler.scheduler import scheduler
from common_lib.logging.logger import get_logger
from common_lib.exceptions.base_exceptions import BusinessException

logger = get_logger(__name__)


class TaskService:
    """任务服务"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskService, cls).__new__(cls)
        return cls._instance
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态
        参数：task_id - 任务ID
        返回：任务状态
        被调用：task_api.get_task_status()
        """
        try:
            task = task_store.get_task(task_id)
            if not task:
                raise BusinessException(f"任务不存在: {task_id}")
            logger.info(f"获取任务状态: {task_id}")
            return task
        except Exception as e:
            logger.error(f"获取任务状态失败: {e}")
            raise BusinessException(f"获取任务状态失败: {str(e)}")
    
    def list_tasks(self, filter: Dict[str, Any], page: int, size: int) -> Dict[str, Any]:
        """列出任务
        参数：filter - 过滤条件；page - 页码；size - 每页大小
        返回：任务列表
        被调用：task_api.list_tasks()
        """
        try:
            tasks = task_store.list_tasks(filter)
            # 分页
            total = len(tasks)
            start = (page - 1) * size
            end = start + size
            paginated_tasks = tasks[start:end]
            
            logger.info(f"列出任务，共{total}个")
            return {
                'total': total,
                'tasks': paginated_tasks,
                'page': page,
                'size': size
            }
        except Exception as e:
            logger.error(f"列出任务失败: {e}")
            raise BusinessException(f"列出任务失败: {str(e)}")
    
    def retry_task(self, task_id: str) -> str:
        """重试任务
        参数：task_id - 任务ID
        返回：新任务ID
        被调用：task_api.retry_task()
        """
        try:
            task = task_store.get_task(task_id)
            if not task:
                raise BusinessException(f"任务不存在: {task_id}")
            
            if task.get('status') != 'failed':
                raise BusinessException("只能重试失败的任务")
            
            # 生成新任务ID
            new_task_id = f"task_{str(uuid.uuid4())[:8]}"
            
            # 创建新任务
            new_task = {
                **task,
                'task_id': new_task_id,
                'status': 'waiting',
                'created_at': time.time(),
                'error': None
            }
            task_store.save_task(new_task_id, new_task)
            
            # 提交任务到执行器
            task_executor.run_task(new_task_id, new_task)
            
            logger.info(f"重试任务: {task_id} -> {new_task_id}")
            return new_task_id
        except Exception as e:
            logger.error(f"重试任务失败: {e}")
            raise BusinessException(f"重试任务失败: {str(e)}")
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务
        参数：task_id - 任务ID
        返回：是否成功
        被调用：task_api.cancel_task()
        """
        try:
            task = task_store.get_task(task_id)
            if not task:
                raise BusinessException(f"任务不存在: {task_id}")
            
            # 更新任务状态为已取消
            task_store.save_task(task_id, {
                **task,
                'status': 'cancelled',
                'end_time': time.time()
            })
            
            logger.info(f"取消任务: {task_id}")
            return True
        except Exception as e:
            logger.error(f"取消任务失败: {e}")
            raise BusinessException(f"取消任务失败: {str(e)}")
    
    def submit_parse_task(self, file_path: str, doc_id: str) -> str:
        """提交解析任务
        参数：file_path - 文件路径；doc_id - 文档ID
        返回：任务ID
        被调用：document_api.upload_document()
        """
        try:
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
            
            logger.info(f"提交解析任务: {task_id}")
            return task_id
        except Exception as e:
            logger.error(f"提交解析任务失败: {e}")
            raise BusinessException(f"提交解析任务失败: {str(e)}")
    
    def submit_reprocess_task(self, doc_id: str, file_path: str) -> str:
        """提交重新处理任务
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
            
            logger.info(f"提交重新处理任务: {task_id}")
            return task_id
        except Exception as e:
            logger.error(f"提交重新处理任务失败: {e}")
            raise BusinessException(f"提交重新处理任务失败: {str(e)}")


# 全局任务服务实例
task_service = TaskService()
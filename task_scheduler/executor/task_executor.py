"""任务执行器
功能：执行各种任务
作者：
创建时间：
"""
import time
from typing import Dict, Any

from task_scheduler.store.task_store import task_store
from ingest.ingest_service import ingest_service
from common_lib.logging.logger import get_logger
from common_lib.exceptions.base_exceptions import TaskExecutionException

logger = get_logger(__name__)


class TaskExecutor:
    """任务执行器"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskExecutor, cls).__new__(cls)
        return cls._instance
    
    def run_task(self, task_id: str, task_params: Dict[str, Any]):
        """执行任务
        参数：task_id - 任务ID；task_params - 任务参数
        被调用：scheduler 定时任务 / 接口提交任务
        """
        # 更新任务状态为运行中
        task_store.save_task(task_id, {
            **task_params,
            'status': 'running',
            'start_time': time.time()
        })
        
        try:
            task_type = task_params.get('type')
            logger.info(f"开始执行任务: {task_id}, 类型: {task_type}")
            
            if task_type == 'parse_document':
                # 解析文档任务
                file_path = task_params.get('file_path')
                doc_id = task_params.get('doc_id')
                result = ingest_service.process_document(file_path, doc_id)
            elif task_type == 'batch_parse':
                # 批量解析任务
                file_paths = task_params.get('file_paths', [])
                result = ingest_service.batch_process(file_paths)
            elif task_type == 'reprocess_document':
                # 重新处理文档任务
                file_path = task_params.get('file_path')
                doc_id = task_params.get('doc_id')
                result = ingest_service.process_document(file_path, doc_id)
            else:
                raise TaskExecutionException(f"未知任务类型: {task_type}")
            
            # 更新任务状态为成功
            task_store.save_task(task_id, {
                **task_params,
                'status': 'success',
                'end_time': time.time(),
                'result': result
            })
            logger.info(f"任务执行成功: {task_id}")
        except Exception as e:
            error_msg = str(e)
            # 更新任务状态为失败
            task_store.save_task(task_id, {
                **task_params,
                'status': 'failed',
                'end_time': time.time(),
                'error': error_msg
            })
            logger.error(f"任务执行失败: {task_id}, 错误: {error_msg}")
            raise


# 全局任务执行器实例
task_executor = TaskExecutor()
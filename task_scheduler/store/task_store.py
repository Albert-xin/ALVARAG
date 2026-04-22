"""任务状态存储
功能：存储和管理任务状态
作者：
创建时间：
"""
import time
from typing import Dict, Any, List

from common_lib.logging.logger import get_logger

logger = get_logger(__name__)


class TaskStore:
    """任务存储"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskStore, cls).__new__(cls)
            cls._instance._init_store()
        return cls._instance
    
    def _init_store(self):
        """初始化存储"""
        # 模拟任务存储
        self.tasks = {}
        logger.info("任务存储初始化完成")
    
    def save_task(self, task_id: str, info: Dict[str, Any]):
        """保存任务
        参数：task_id - 任务ID；info - 任务信息
        被调用：task_service / task_executor
        """
        self.tasks[task_id] = {
            **info,
            'updated_at': time.time()
        }
        logger.info(f"保存任务: {task_id}")
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """获取任务
        参数：task_id - 任务ID
        返回：任务信息
        被调用：task_api.get_task_status()
        """
        return self.tasks.get(task_id)
    
    def list_tasks(self, filter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """列出任务
        参数：filter - 过滤条件
        返回：任务列表
        被调用：task_api.list_tasks()
        """
        filtered_tasks = []
        for task_id, task_info in self.tasks.items():
            # 应用过滤条件
            match = True
            if 'status' in filter and task_info.get('status') != filter['status']:
                match = False
            if 'type' in filter and task_info.get('type') != filter['type']:
                match = False
            if 'doc_id' in filter and task_info.get('doc_id') != filter['doc_id']:
                match = False
            if match:
                filtered_tasks.append(task_info)
        
        # 按创建时间倒序排序
        filtered_tasks.sort(key=lambda x: x.get('created_at', 0), reverse=True)
        
        logger.info(f"列出任务，共{len(filtered_tasks)}个")
        return filtered_tasks


# 全局任务存储实例
task_store = TaskStore()
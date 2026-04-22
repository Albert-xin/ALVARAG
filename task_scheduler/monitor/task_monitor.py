"""任务监控
功能：监控任务执行状态
作者：
创建时间：
"""
import time
from typing import Dict, Any

from task_scheduler.store.task_store import task_store
from common_lib.logging.logger import get_logger

logger = get_logger(__name__)


class TaskMonitor:
    """任务监控"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskMonitor, cls).__new__(cls)
        return cls._instance
    
    def check_running_tasks(self):
        """检查运行中的任务
        被调用：scheduler 定时调度
        """
        tasks = task_store.list_tasks({'status': 'running'})
        current_time = time.time()
        
        for task in tasks:
            task_id = task.get('task_id')
            start_time = task.get('start_time', 0)
            
            # 检查任务是否超时（超过2小时）
            if current_time - start_time > 7200:
                logger.warning(f"任务超时: {task_id}")
                # 更新任务状态为失败
                task_store.save_task(task_id, {
                    **task,
                    'status': 'failed',
                    'error': '任务执行超时'
                })
        
        logger.info(f"检查运行中任务，共{len(tasks)}个")
    
    def statistics_task_result(self) -> Dict[str, Any]:
        """统计任务结果
        被调用：后台监控
        """
        all_tasks = task_store.list_tasks({})
        stats = {
            'total': len(all_tasks),
            'success': 0,
            'failed': 0,
            'running': 0,
            'average_duration': 0
        }
        
        total_duration = 0
        for task in all_tasks:
            status = task.get('status')
            if status == 'success':
                stats['success'] += 1
                # 计算耗时
                start_time = task.get('start_time', 0)
                end_time = task.get('end_time', 0)
                if start_time and end_time:
                    total_duration += end_time - start_time
            elif status == 'failed':
                stats['failed'] += 1
            elif status == 'running':
                stats['running'] += 1
        
        if stats['success'] > 0:
            stats['average_duration'] = total_duration / stats['success']
        
        # 计算成功率
        if stats['total'] > 0:
            stats['success_rate'] = (stats['success'] / stats['total']) * 100
        else:
            stats['success_rate'] = 0
        
        logger.info(f"任务统计: {stats}")
        return stats


# 全局任务监控实例
task_monitor = TaskMonitor()
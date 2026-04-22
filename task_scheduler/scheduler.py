"""定时任务调度器
功能：管理和调度定时任务
作者：
创建时间：
"""
import time
from typing import Dict, Any, Callable

from common_lib.logging.logger import get_logger

logger = get_logger(__name__)


class Scheduler:
    """调度器"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Scheduler, cls).__new__(cls)
            cls._instance._init_scheduler()
        return cls._instance
    
    def _init_scheduler(self):
        """初始化调度器
        被调用：task_scheduler main入口
        """
        # 模拟任务调度器
        self.jobs = {}
        self.running = False
        logger.info("调度器初始化完成")
    
    def start(self):
        """启动调度器
        被调用：服务启动脚本
        """
        self.running = True
        logger.info("调度器启动")
    
    def stop(self):
        """停止调度器
        被调用：服务关闭脚本
        """
        self.running = False
        logger.info("调度器停止")
    
    def add_job(self, job_func: Callable, cron: str, args: list = None):
        """添加定时任务
        参数：job_func - 任务函数；cron - cron表达式；args - 参数
        被调用：任务注册模块
        """
        job_id = f"job_{int(time.time())}"
        self.jobs[job_id] = {
            'func': job_func,
            'cron': cron,
            'args': args or [],
            'next_run': time.time() + 3600  # 模拟1小时后执行
        }
        logger.info(f"添加任务: {job_id}")
        return job_id
    
    def remove_job(self, job_id: str):
        """移除任务
        参数：job_id - 任务ID
        被调用：task_service.cancel_task()
        """
        if job_id in self.jobs:
            del self.jobs[job_id]
            logger.info(f"移除任务: {job_id}")
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """获取任务状态
        参数：job_id - 任务ID
        返回：任务状态
        被调用：task_api、监控面板
        """
        job = self.jobs.get(job_id)
        if not job:
            return {'exists': False}
        return {
            'exists': True,
            'next_run': job['next_run'],
            'cron': job['cron']
        }


# 全局调度器实例
scheduler = Scheduler()
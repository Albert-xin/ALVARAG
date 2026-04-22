"""解析流程监控
功能：监控文档处理流程
作者：
创建时间：
"""
import time
import psutil
from typing import Dict, Any, Optional

from common_lib.logging.logger import get_logger
from common_lib.metrics import record_duration

logger = get_logger(__name__)


class PipelineMonitor:
    """流程监控器"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PipelineMonitor, cls).__new__(cls)
            cls._instance._init_monitor()
        return cls._instance
    
    def _init_monitor(self):
        """初始化监控"""
        self.processing_status = {}
        logger.info("流程监控器初始化完成")
    
    def start_monitor(self, doc_id: str, step: str):
        """开始监控步骤
        参数：doc_id - 文档ID；step - 步骤
        被调用：ingest_service、mineru_parser、chunker
        """
        if doc_id not in self.processing_status:
            self.processing_status[doc_id] = {}
        
        self.processing_status[doc_id][step] = {
            'start_time': time.time(),
            'status': 'running',
            'error': None,
            'duration': 0
        }
        logger.info(f"开始监控文档{doc_id}的{step}步骤")
    
    def end_monitor(self, doc_id: str, step: str, success: bool = True, error: Optional[str] = None):
        """结束监控步骤
        参数：doc_id - 文档ID；step - 步骤；success - 是否成功；error - 错误信息
        被调用：各处理步骤结束时
        """
        if doc_id in self.processing_status and step in self.processing_status[doc_id]:
            end_time = time.time()
            start_time = self.processing_status[doc_id][step]['start_time']
            duration = end_time - start_time
            
            self.processing_status[doc_id][step]['duration'] = duration
            self.processing_status[doc_id][step]['status'] = 'success' if success else 'failed'
            self.processing_status[doc_id][step]['error'] = error
            
            # 记录耗时
            record_duration('pipeline', step, duration)
            logger.info(f"文档{doc_id}的{step}步骤完成，耗时{duration:.2f}秒")
    
    def get_pipeline_status(self, doc_id: str) -> Dict[str, Any]:
        """获取流程状态
        参数：doc_id - 文档ID
        返回：流程状态
        被调用：document_api、task_service
        """
        return self.processing_status.get(doc_id, {})
    
    def record_memory_usage(self, step: str):
        """记录内存使用
        参数：step - 步骤
        被调用：大文件解析、批量向量化
        """
        memory = psutil.virtual_memory()
        memory_used = memory.used / (1024 * 1024 * 1024)
        memory_total = memory.total / (1024 * 1024 * 1024)
        memory_percent = memory.percent
        
        logger.info(f"{step}步骤内存使用：{memory_used:.2f}GB / {memory_total:.2f}GB ({memory_percent:.1f}%)")
        
        # 检查内存使用是否超过阈值
        if memory_percent > 80:
            logger.warning(f"内存使用超过80%，当前使用率：{memory_percent:.1f}%")
    
    def report_failure(self, doc_id: str, step: str, error: str):
        """报告失败
        参数：doc_id - 文档ID；step - 步骤；error - 错误信息
        被调用：异常捕获块
        """
        logger.error(f"文档{doc_id}的{step}步骤失败：{error}")
        # 这里可以添加告警逻辑


# 全局监控器实例
pipeline_monitor = PipelineMonitor()
"""日志工具
功能：提供统一的日志管理
作者：
创建时间：
"""
import logging
import os
import uuid
from threading import local


class TraceLogger:
    """带trace_id的日志器"""
    _local = local()
    
    @classmethod
    def get_logger(cls, name: str, trace_id: str = None) -> logging.Logger:
        """获取日志器
        参数：name - 模块名；trace_id - 追踪ID
        返回：日志器实例
        被调用：全模块通用
        """
        if trace_id:
            cls._local.trace_id = trace_id
        
        logger = logging.getLogger(name)
        if not logger.handlers:
            # 配置日志格式
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(trace_id)s - %(module)s - %(message)s'
            )
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            # 文件处理器
            log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'), encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            logger.setLevel(logging.INFO)
        
        # 注入trace_id
        original_info = logger.info
        original_error = logger.error
        
        def info(msg, *args, **kwargs):
            trace_id = getattr(cls._local, 'trace_id', str(uuid.uuid4()))
            msg = f"[trace_id={trace_id}] {msg}"
            original_info(msg, *args, **kwargs)
        
        def error(msg, *args, **kwargs):
            trace_id = getattr(cls._local, 'trace_id', str(uuid.uuid4()))
            msg = f"[trace_id={trace_id}] {msg}"
            original_error(msg, *args, **kwargs)
        
        logger.info = info
        logger.error = error
        
        return logger
    
    @classmethod
    def set_trace_id(cls, trace_id: str):
        """设置trace_id
        参数：trace_id - 追踪ID
        被调用：api入口层
        """
        cls._local.trace_id = trace_id


def get_logger(name: str, trace_id: str = None) -> logging.Logger:
    """获取日志器
    参数：name - 模块名；trace_id - 追踪ID
    返回：日志器实例
    """
    return TraceLogger.get_logger(name, trace_id)


def set_trace_id(trace_id: str):
    """设置trace_id
    参数：trace_id - 追踪ID
    """
    TraceLogger.set_trace_id(trace_id)
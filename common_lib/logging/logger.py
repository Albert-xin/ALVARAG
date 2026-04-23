"""日志工具
功能：提供统一的日志管理，支持多级别、结构化、轮转等特性
作者：
创建时间：
"""
import logging
import os
import uuid
import json
import time
from threading import local
from multiprocessing import current_process
from logging.handlers import TimedRotatingFileHandler

from common_lib.config.settings import settings


class SizeAndTimeRotatingFileHandler(TimedRotatingFileHandler):
    """时间和大小双重轮转的文件处理器"""
    def __init__(self, filename, max_size=0, when='h', interval=1, backupCount=0, encoding=None, delay=False):
        super().__init__(filename, when, interval, backupCount, encoding, delay)
        self.max_size = max_size
    
    def shouldRollover(self, record):
        """判断是否需要轮转
        优先检查大小，再检查时间"""
        # 检查大小
        if self.max_size > 0:
            self.stream.seek(0, 2)  # 移动到文件末尾
            if self.stream.tell() >= self.max_size:
                return True
        # 检查时间
        return super().shouldRollover(record)


class TraceContext:
    """追踪上下文管理，支持多进程"""
    def __init__(self):
        self._local = local()
        # 进程ID作为进程间隔离的一部分
        self._process_id = current_process().pid
    
    def get_trace_id(self) -> str:
        """获取trace_id"""
        try:
            return getattr(self._local, 'trace_id', None)
        except AttributeError:
            return None
    
    def set_trace_id(self, trace_id: str):
        """设置trace_id"""
        setattr(self._local, 'trace_id', trace_id)
    
    def generate_trace_id(self) -> str:
        """生成新的trace_id"""
        return str(uuid.uuid4())
    
    def get_or_create_trace_id(self) -> str:
        """获取或创建trace_id"""
        trace_id = self.get_trace_id()
        if not trace_id:
            trace_id = self.generate_trace_id()
            self.set_trace_id(trace_id)
        return trace_id


class JsonFormatter(logging.Formatter):
    """JSON格式日志格式化器"""
    def format(self, record):
        log_record = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created)),
            'level': record.levelname,
            'module': record.module,
            'message': record.getMessage(),
            'trace_id': getattr(record, 'trace_id', None),
            'process_id': current_process().pid,
            'thread_id': record.thread,
        }
        # 添加额外的上下文信息
        if hasattr(record, 'context'):
            log_record.update(record.context)
        return json.dumps(log_record, ensure_ascii=False)


class EnhancedLogger:
    """增强型日志器"""
    _instance = None
    _trace_context = TraceContext()
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EnhancedLogger, cls).__new__(cls)
            cls._instance._init_config()
        return cls._instance
    
    def _init_config(self):
        """初始化配置"""
        self.log_config = settings.get('logging', {})
        self.log_level = self._get_log_level()
        self.log_format = self.log_config.get('format', '%(asctime)s - %(levelname)s - %(trace_id)s - %(module)s - %(message)s')
        self.json_format = self.log_config.get('json_format', False)
        self.log_dir = self.log_config.get('log_dir', 'logs')
        self.rotation_config = self.log_config.get('rotation', {})
        
        # 确保日志目录存在
        os.makedirs(self.log_dir, exist_ok=True)
    
    def _get_log_level(self):
        """根据环境获取日志级别"""
        env = os.environ.get('ENVIRONMENT', 'development')
        env_config = self.log_config.get('environments', {}).get(env, {})
        level = env_config.get('level', self.log_config.get('level', 'INFO'))
        return getattr(logging, level.upper(), logging.INFO)
    
    def _create_logger(self, name: str) -> logging.Logger:
        """创建日志器"""
        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)
        
        # 避免重复添加处理器
        if not logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.log_level)
            
            # 文件处理器（带时间和大小轮转）
            log_file = os.path.join(self.log_dir, 'app.log')
            if self.rotation_config.get('enabled', True):
                file_handler = SizeAndTimeRotatingFileHandler(
                    log_file,
                    max_size=self.rotation_config.get('max_size', 10485760),  # 10MB
                    when=self.rotation_config.get('when', 'H'),
                    interval=self.rotation_config.get('interval', 1),
                    backupCount=self.rotation_config.get('backup_count', 7),
                    encoding='utf-8'
                )
            else:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(self.log_level)
            
            # 格式化器
            if self.json_format:
                formatter = JsonFormatter()
            else:
                formatter = logging.Formatter(self.log_format)
            
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            # 添加处理器
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
        
        return logger
    
    def get_logger(self, name: str, trace_id: str = None) -> logging.Logger:
        """获取日志器
        参数：name - 模块名；trace_id - 追踪ID
        返回：日志器实例
        被调用：全模块通用
        """
        if trace_id:
            self._trace_context.set_trace_id(trace_id)
        
        if name not in self._loggers:
            self._loggers[name] = self._create_logger(name)
        
        logger = self._loggers[name]
        
        # 为日志方法添加trace_id注入
        if not hasattr(logger, '_enhanced'):
            self._enhance_logger(logger)
            logger._enhanced = True
        
        return logger
    
    def _enhance_logger(self, logger: logging.Logger):
        """增强日志器，添加trace_id和上下文支持"""
        for level in ['debug', 'info', 'warning', 'error', 'critical']:
            original_method = getattr(logger, level)
            
            def enhanced_method(msg, *args, **kwargs):
                # 获取trace_id
                trace_id = self._trace_context.get_or_create_trace_id()
                
                # 处理上下文信息
                context = kwargs.pop('context', None)
                
                # 创建日志记录
                record = logger.makeRecord(
                    logger.name,
                    getattr(logging, level.upper()),
                    '', 0, msg, args, None, None
                )
                
                # 注入trace_id
                record.trace_id = trace_id
                
                # 注入上下文
                if context:
                    record.context = context
                
                # 处理异常
                try:
                    logger.handle(record)
                except Exception as e:
                    # 日志写入失败时的处理
                    print(f"日志写入失败: {e}")
            
            setattr(logger, level, enhanced_method)
    
    def set_trace_id(self, trace_id: str):
        """设置trace_id
        参数：trace_id - 追踪ID
        被调用：api入口层
        """
        self._trace_context.set_trace_id(trace_id)
    
    def get_trace_id(self) -> str:
        """获取当前trace_id"""
        return self._trace_context.get_or_create_trace_id()


# 全局实例
enhanced_logger = EnhancedLogger()


def get_logger(name: str, trace_id: str = None) -> logging.Logger:
    """获取日志器
    参数：name - 模块名；trace_id - 追踪ID
    返回：日志器实例
    """
    return enhanced_logger.get_logger(name, trace_id)


def set_trace_id(trace_id: str):
    """设置trace_id
    参数：trace_id - 追踪ID
    """
    enhanced_logger.set_trace_id(trace_id)


def get_trace_id() -> str:
    """获取当前trace_id
    返回：trace_id
    """
    return enhanced_logger.get_trace_id()

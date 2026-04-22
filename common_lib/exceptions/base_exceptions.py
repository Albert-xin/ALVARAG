"""全局异常
功能：定义统一的异常类
作者：
创建时间：
"""


class BusinessException(Exception):
    """业务异常基类
    被调用：全业务模块
    """
    def __init__(self, message: str, code: int = 400):
        """初始化异常
        参数：message - 错误信息；code - 错误码
        """
        self.message = message
        self.code = code
        super().__init__(message)


class DocumentParseException(BusinessException):
    """文档解析失败异常
    被调用：mineru_parser
    """
    def __init__(self, message: str):
        """初始化异常
        参数：message - 错误信息
        """
        super().__init__(message, code=400)


class VectorStoreException(BusinessException):
    """向量库异常
    被调用：vector_store
    """
    def __init__(self, message: str):
        """初始化异常
        参数：message - 错误信息
        """
        super().__init__(message, code=500)


class TaskExecutionException(BusinessException):
    """任务执行异常
    被调用：task_executor
    """
    def __init__(self, message: str):
        """初始化异常
        参数：message - 错误信息
        """
        super().__init__(message, code=500)
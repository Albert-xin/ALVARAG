"""定时清理任务
功能：清理临时文件和过期任务
作者：
创建时间：
"""
import os
import time
from common_lib.logging.logger import get_logger

logger = get_logger(__name__)


def run():
    """执行清理任务
    被调用：scheduler 定时调度
    """
    logger.info("开始执行清理任务")
    
    # 清理临时文件
    temp_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'temp')
    if os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                file_mtime = os.path.getmtime(file_path)
                # 删除3天前的文件
                if time.time() - file_mtime > 3 * 24 * 3600:
                    os.remove(file_path)
                    logger.info(f"删除过期临时文件: {file_path}")
            except Exception as e:
                logger.error(f"删除临时文件失败: {file_path}, {e}")
    
    # 清理过期任务日志
    # 这里可以添加清理过期任务日志的逻辑
    
    logger.info("清理任务执行完成")
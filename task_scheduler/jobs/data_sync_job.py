"""目录同步任务
功能：扫描目录并自动更新文档
作者：
创建时间：
"""
import os
from ingest.incremental_update import incremental_update
from common_lib.logging.logger import get_logger

logger = get_logger(__name__)


def run():
    """执行目录同步任务
    被调用：scheduler 定时调度
    """
    logger.info("开始执行目录同步任务")
    
    # 配置的知识库目录
    knowledge_base_dirs = [
        os.path.join(os.path.dirname(__file__), '..', '..', 'knowledge_base')
    ]
    
    for dir_path in knowledge_base_dirs:
        if os.path.exists(dir_path):
            logger.info(f"扫描目录: {dir_path}")
            result = incremental_update.check_and_update(dir_path)
            logger.info(f"目录同步结果: {result}")
        else:
            logger.warning(f"目录不存在: {dir_path}")
    
    logger.info("目录同步任务执行完成")
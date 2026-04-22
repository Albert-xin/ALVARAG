"""增量更新
功能：监控目录变化，自动更新文档
作者：
创建时间：
"""
import os
import time
from typing import Dict, Any

from common_lib.logging.logger import get_logger
from common_lib.utils.file_utils import calculate_file_md5
from ingest.ingest_service import ingest_service

logger = get_logger(__name__)


class IncrementalUpdate:
    """增量更新"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IncrementalUpdate, cls).__new__(cls)
            cls._instance._init_state()
        return cls._instance
    
    def _init_state(self):
        """初始化状态"""
        # 存储文件状态：{file_path: (md5, mtime)}
        self.file_states = {}
        logger.info("增量更新服务初始化完成")
    
    def check_and_update(self, folder_path: str) -> Dict[str, Any]:
        """检查并更新目录
        参数：folder_path - 目录路径
        返回：更新结果
        被调用：data_sync_job.run()
        """
        if not os.path.exists(folder_path):
            logger.error(f"目录不存在: {folder_path}")
            return {'status': 'error', 'message': '目录不存在'}
        
        new_files = []
        modified_files = []
        deleted_files = []
        
        # 扫描目录
        current_files = {}
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # 计算文件MD5和修改时间
                try:
                    md5 = calculate_file_md5(file_path)
                    mtime = os.path.getmtime(file_path)
                    current_files[file_path] = (md5, mtime)
                except Exception as e:
                    logger.error(f"计算文件状态失败: {file_path}, {e}")
        
        # 检查新增和修改的文件
        for file_path, (current_md5, current_mtime) in current_files.items():
            if file_path not in self.file_states:
                # 新增文件
                new_files.append(file_path)
                logger.info(f"发现新增文件: {file_path}")
            else:
                # 检查是否修改
                old_md5, old_mtime = self.file_states[file_path]
                if current_md5 != old_md5:
                    modified_files.append(file_path)
                    logger.info(f"发现修改文件: {file_path}")
        
        # 检查删除的文件
        for file_path in list(self.file_states.keys()):
            if file_path not in current_files:
                deleted_files.append(file_path)
                logger.info(f"发现删除文件: {file_path}")
                del self.file_states[file_path]
        
        # 处理新增和修改的文件
        for file_path in new_files + modified_files:
            # 生成doc_id
            doc_id = f"doc_{int(time.time())}_{hash(file_path)}"
            # 处理文档
            result = ingest_service.process_document(file_path, doc_id)
            if result['status'] == 'success':
                # 更新文件状态
                self.file_states[file_path] = current_files[file_path]
                logger.info(f"文件处理成功: {file_path}")
            else:
                logger.error(f"文件处理失败: {file_path}, {result['error']}")
        
        # 处理删除的文件
        # 这里需要根据文件路径找到对应的doc_id，然后删除
        # 简化处理，实际应从元数据存储中查询
        
        logger.info(f"增量更新完成，新增{len(new_files)}个，修改{len(modified_files)}个，删除{len(deleted_files)}个")
        return {
            'new_files': new_files,
            'modified_files': modified_files,
            'deleted_files': deleted_files
        }


# 全局增量更新实例
incremental_update = IncrementalUpdate()
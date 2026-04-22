"""文档解析器
功能：解析各种格式的文档
作者：
创建时间：
"""
import os
from typing import Dict, Any, List, Optional

from data_pipeline.parser.validator import validator
from data_pipeline.parser.ocr_processor import ocr_processor
from data_pipeline.monitor.pipeline_monitor import pipeline_monitor
from common_lib.logging.logger import get_logger
from common_lib.utils.file_utils import get_file_size, split_file_by_size
from common_lib.utils.text_utils import clean_extra_spaces
from common_lib.exceptions.base_exceptions import DocumentParseException
from model_service.common.device_manager import get_available_device

logger = get_logger(__name__)


class MineruParser:
    """文档解析器"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MineruParser, cls).__new__(cls)
        return cls._instance
    
    def init(self, device: Optional[str] = None, threshold_gb: Optional[float] = None):
        """初始化解析器
        参数：device - 设备；threshold_gb - 大文件阈值
        被调用：ingest_service.process_document()
        """
        self.device = device or get_available_device()
        self.threshold_gb = threshold_gb or 1.0
        logger.info(f"解析器初始化完成，使用设备: {self.device}，大文件阈值: {self.threshold_gb}GB")
    
    def validate_and_parse(self, file_path: str) -> Dict[str, Any]:
        """校验并解析文件
        参数：file_path - 文件路径
        返回：解析结果
        被调用：ingest_service.process_document()
        """
        # 校验文件
        validator.validate_file(file_path)
        
        # 检查文件大小
        file_size = get_file_size(file_path)
        
        # 根据文件大小选择解析方式
        if file_size > self.threshold_gb:
            pipeline_monitor.start_monitor(os.path.basename(file_path), 'parse_large_file')
            try:
                result = self.parse_large_file(file_path)
                pipeline_monitor.end_monitor(os.path.basename(file_path), 'parse_large_file')
            except Exception as e:
                pipeline_monitor.end_monitor(os.path.basename(file_path), 'parse_large_file', False, str(e))
                raise
        else:
            pipeline_monitor.start_monitor(os.path.basename(file_path), 'parse_single_file')
            try:
                result = self.parse_single_file(file_path)
                pipeline_monitor.end_monitor(os.path.basename(file_path), 'parse_single_file')
            except Exception as e:
                pipeline_monitor.end_monitor(os.path.basename(file_path), 'parse_single_file', False, str(e))
                raise
        
        return result
    
    def parse_single_file(self, file_path: str) -> Dict[str, Any]:
        """解析单个文件
        参数：file_path - 文件路径
        返回：解析结果
        被调用：validate_and_parse()
        """
        logger.info(f"解析文件: {file_path}")
        
        # 模拟解析过程
        ext = os.path.splitext(file_path)[1].lower()
        
        # 模拟解析结果
        result = {
            'text': '这是解析后的文本内容',
            'pages': [
                {
                    'page_num': 1,
                    'content': '第1页内容',
                    'tables': []
                },
                {
                    'page_num': 2,
                    'content': '第2页内容',
                    'tables': []
                }
            ],
            'metadata': {
                'file_name': os.path.basename(file_path),
                'page_count': 2
            }
        }
        
        # 清洗文本
        result['text'] = clean_extra_spaces(result['text'])
        
        logger.info(f"文件{file_path}解析完成")
        return result
    
    def parse_large_file(self, file_path: str) -> Dict[str, Any]:
        """解析大文件
        参数：file_path - 文件路径
        返回：解析结果
        被调用：validate_and_parse()
        """
        logger.info(f"解析大文件: {file_path}")
        
        # 分片处理
        chunks = split_file_by_size(file_path, self.threshold_gb)
        logger.info(f"文件分片数: {len(chunks)}")
        
        # 逐个分片解析
        results = []
        for i, chunk in enumerate(chunks):
            logger.info(f"解析分片 {i+1}/{len(chunks)}")
            # 模拟分片解析
            results.append({
                'text': f'分片{i+1}的内容',
                'pages': [{
                    'page_num': i*10 + 1,
                    'content': f'分片{i+1}的第1页'
                }]
            })
        
        # 合并结果
        combined_result = {
            'text': '\n'.join([r['text'] for r in results]),
            'pages': [],
            'metadata': {
                'file_name': os.path.basename(file_path),
                'page_count': len(results) * 10
            }
        }
        
        # 合并页码
        page_num = 1
        for r in results:
            for page in r['pages']:
                page['page_num'] = page_num
                combined_result['pages'].append(page)
                page_num += 1
        
        logger.info(f"大文件{file_path}解析完成")
        return combined_result
    
    def batch_parse(self, file_paths: List[str]) -> Dict[str, Any]:
        """批量解析文件
        参数：file_paths - 文件路径列表
        返回：解析结果
        被调用：ingest_service.batch_process()
        """
        logger.info(f"批量解析{len(file_paths)}个文件")
        
        results = {}
        for file_path in file_paths:
            try:
                result = self.validate_and_parse(file_path)
                results[file_path] = {'success': True, 'data': result}
            except Exception as e:
                results[file_path] = {'success': False, 'error': str(e)}
        
        logger.info("批量解析完成")
        return results


# 全局解析器实例
mineru_parser = MineruParser()
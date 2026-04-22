"""OCR处理器
功能：处理图片型PDF的文字提取
作者：
创建时间：
"""
from typing import Dict, Any

from common_lib.logging.logger import get_logger
from model_service.common.device_manager import get_available_device

logger = get_logger(__name__)


class OCRProcessor:
    """OCR处理器"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCRProcessor, cls).__new__(cls)
            cls._instance._init_processor()
        return cls._instance
    
    def _init_processor(self):
        """初始化OCR处理器"""
        self.device = get_available_device()
        logger.info(f"OCR处理器初始化完成，使用设备: {self.device}")
    
    def ocr_image(self, image_path: str) -> Dict[str, Any]:
        """OCR识别图片
        参数：image_path - 图片路径
        返回：识别结果
        被调用：mineru_parser.parse_single_file()
        """
        # 模拟OCR识别
        logger.info(f"OCR处理图片: {image_path}")
        
        # 模拟识别结果
        result = {
            'text': '这是OCR识别的文本内容',
            'confidence': 0.95,
            'regions': [
                {
                    'text': '识别区域1',
                    'bbox': [0, 0, 100, 100]
                },
                {
                    'text': '识别区域2',
                    'bbox': [100, 100, 200, 200]
                }
            ]
        }
        
        logger.info("OCR处理完成")
        return result


# 全局OCR处理器实例
ocr_processor = OCRProcessor()
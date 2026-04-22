"""模型加载器
功能：加载和管理模型
作者：
创建时间：
"""
import os
import threading
from typing import Dict, Any

from model_service.common.device_manager import get_available_device
from common_lib.logging.logger import get_logger

logger = get_logger(__name__)


class ModelLoader:
    """模型加载器"""
    _instance = None
    _loaded_models: Dict[str, Any] = {}
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    def load_model(self, model_name: str, model_path: str, device: str = None) -> Any:
        """加载模型
        参数：model_name - 模型名称；model_path - 模型路径；device - 设备
        返回：模型实例
        被调用：embedding_service、rerank_service、llm_service
        """
        with self._lock:
            if model_name in self._loaded_models:
                logger.info(f"模型 {model_name} 已加载")
                return self._loaded_models[model_name]
            
            if not device:
                device = get_available_device()
            
            try:
                # 这里根据不同模型类型加载不同的模型
                # 实际实现需要根据具体模型库进行调整
                logger.info(f"加载模型 {model_name} 到 {device}")
                # 模拟模型加载
                model = f"Model {model_name} loaded on {device}"
                self._loaded_models[model_name] = model
                return model
            except Exception as e:
                logger.error(f"加载模型失败: {e}")
                raise
    
    def unload_model(self, model_name: str):
        """卸载模型
        参数：model_name - 模型名称
        被调用：服务重启、模型切换、内存释放
        """
        with self._lock:
            if model_name in self._loaded_models:
                del self._loaded_models[model_name]
                logger.info(f"模型 {model_name} 已卸载")
    
    def reload_model(self, model_name: str, model_path: str, device: str = None):
        """重新加载模型
        参数：model_name - 模型名称；model_path - 模型路径；device - 设备
        被调用：配置更新、热重载
        """
        self.unload_model(model_name)
        return self.load_model(model_name, model_path, device)
    
    def get_loaded_models(self) -> Dict[str, Any]:
        """获取已加载的模型
        返回：已加载模型列表
        被调用：监控、health_api
        """
        return self._loaded_models


# 全局模型加载器实例
model_loader = ModelLoader()
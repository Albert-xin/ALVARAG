"""全局配置类
功能：加载和管理全局配置
作者：
创建时间：
"""
import os
import yaml


class Settings:
    """配置管理类"""
    _instance = None
    _config = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance
    
    def load_config(self):
        """加载配置文件
        被调用：所有服务启动时
        """
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        else:
            # 默认配置
            self._config = {
                'device': 'auto',
                'file_threshold_gb': 1.0,
                'chunk_size': 512,
                'overlap': 128,
                'batch_size': 32,
                'max_concurrency': 4,
                'timeout_seconds': 300,
                'model_paths': {
                    'embedding': 'models/embedding',
                    'rerank': 'models/rerank',
                    'llm': 'models/llm'
                }
            }
    
    def get(self, key: str, default=None):
        """获取配置项
        参数：key - 配置键；default - 默认值
        返回：配置值
        被调用：parser / embedding / scheduler
        """
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


# 全局配置实例
settings = Settings()
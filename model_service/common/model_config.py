"""模型配置管理器
功能：管理模型配置
作者：
创建时间：
"""
from common_lib.config.settings import settings
from model_service.common.device_manager import get_available_device


def get_model_config(model_type: str) -> dict:
    """获取模型配置
    参数：model_type - 模型类型（embedding/rerank/llm）
    返回：配置字典
    被调用：model_loader、embedding/rerank/llm service
    """
    config = {
        'embedding': {
            'model_path': settings.get('model_paths.embedding', 'models/embedding'),
            'device': get_device_config('embedding'),
            'precision': settings.get('embedding.precision', 'fp16'),
            'max_length': settings.get('embedding.max_length', 512)
        },
        'rerank': {
            'model_path': settings.get('model_paths.rerank', 'models/rerank'),
            'device': get_device_config('rerank'),
            'precision': settings.get('rerank.precision', 'fp16'),
            'max_length': settings.get('rerank.max_length', 512)
        },
        'llm': {
            'model_path': settings.get('model_paths.llm', 'models/llm'),
            'device': get_device_config('llm'),
            'precision': settings.get('llm.precision', 'fp16'),
            'max_length': settings.get('llm.max_length', 4096)
        }
    }
    return config.get(model_type, {})


def get_device_config(model_type: str) -> str:
    """获取设备配置
    参数：model_type - 模型类型
    返回：设备字符串
    被调用：所有模型服务
    """
    device = settings.get(f'{model_type}.device')
    if not device:
        device = get_available_device()
    return device


def get_batch_config(model_type: str) -> dict:
    """获取批处理配置
    参数：model_type - 模型类型
    返回：批处理配置
    被调用：embedding、批量生成
    """
    return {
        'batch_size': settings.get(f'{model_type}.batch_size', 32),
        'max_concurrency': settings.get(f'{model_type}.max_concurrency', 4)
    }


def get_model_path(model_type: str) -> str:
    """获取模型路径
    参数：model_type - 模型类型
    返回：模型路径
    被调用：model_loader
    """
    path = settings.get(f'model_paths.{model_type}')
    if not path:
        raise ValueError(f"模型路径未配置: {model_type}")
    return path
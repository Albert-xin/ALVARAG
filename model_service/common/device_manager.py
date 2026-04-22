"""设备管理
功能：管理GPU/CPU设备
作者：
创建时间：
"""
import torch


def get_available_device() -> str:
    """获取可用设备
    返回：'cuda'或'cpu'
    被调用：所有需要GPU/CPU的类初始化
    """
    if torch.cuda.is_available():
        return 'cuda'
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return 'mps'
    else:
        return 'cpu'


def is_gpu_available() -> bool:
    """检查是否有GPU可用
    返回：布尔值
    被调用：parser / embedding / rerank
    """
    return torch.cuda.is_available() or (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available())
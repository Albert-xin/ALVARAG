"""监控指标
功能：提供监控指标收集功能
作者：
创建时间：
"""
import time
import threading
from collections import defaultdict


class Metrics:
    """监控指标收集类"""
    _instance = None
    _request_counts = defaultdict(int)
    _request_success = defaultdict(int)
    _duration_records = defaultdict(list)
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Metrics, cls).__new__(cls)
        return cls._instance
    
    def count_request(self, api_name: str, success: bool = True):
        """统计接口请求
        参数：api_name - 接口名称；success - 是否成功
        被调用：api层所有接口
        """
        with self._lock:
            self._request_counts[api_name] += 1
            if success:
                self._request_success[api_name] += 1
    
    def record_duration(self, module: str, step: str, seconds: float):
        """记录操作耗时
        参数：module - 模块名；step - 步骤名；seconds - 耗时（秒）
        被调用：pipeline各阶段
        """
        with self._lock:
            key = f"{module}_{step}"
            self._duration_records[key].append(seconds)
    
    def gauge_gpu_memory_usage(self):
        """统计GPU内存使用
        被调用：model_service
        """
        try:
            import torch
            if torch.cuda.is_available():
                memory_used = torch.cuda.memory_allocated() / (1024 * 1024 * 1024)
                memory_total = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024 * 1024)
                return {
                    'used': memory_used,
                    'total': memory_total,
                    'percentage': (memory_used / memory_total) * 100
                }
        except ImportError:
            pass
        return None
    
    def get_metrics(self):
        """获取所有指标"""
        with self._lock:
            metrics = {
                'requests': dict(self._request_counts),
                'success': dict(self._request_success),
                'duration': {k: sum(v)/len(v) if v else 0 for k, v in self._duration_records.items()}
            }
        return metrics


# 全局监控实例
metrics = Metrics()


def count_request(api_name: str, success: bool = True):
    """统计接口请求
    参数：api_name - 接口名称；success - 是否成功
    """
    metrics.count_request(api_name, success)


def record_duration(module: str, step: str, seconds: float):
    """记录操作耗时
    参数：module - 模块名；step - 步骤名；seconds - 耗时（秒）
    """
    metrics.record_duration(module, step, seconds)


def gauge_gpu_memory_usage():
    """统计GPU内存使用
    """
    return metrics.gauge_gpu_memory_usage()
"""文件工具类
功能：提供文件操作相关的工具方法
作者：
创建时间：
"""
import os
import hashlib
import tempfile


def get_file_size(file_path: str) -> float:
    """获取文件大小
    参数：file_path - 文件路径
    返回：文件大小（GB）
    被调用：mineru_parser.validate_and_parse()
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024 * 1024)  # 转换为GB


def split_file_by_size(file_path: str, chunk_size_gb: float) -> list:
    """按大小切分文件
    参数：file_path - 文件路径；chunk_size_gb - 切分大小（GB）
    返回：临时文件路径列表
    被调用：mineru_parser.parse_large_file()
    """
    chunk_size_bytes = int(chunk_size_gb * 1024 * 1024 * 1024)
    temp_files = []
    
    with open(file_path, 'rb') as f:
        chunk_index = 0
        while True:
            chunk_data = f.read(chunk_size_bytes)
            if not chunk_data:
                break
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'_chunk{chunk_index}')
            temp_file.write(chunk_data)
            temp_file.close()
            temp_files.append(temp_file.name)
            chunk_index += 1
    
    return temp_files


def calculate_file_md5(file_path: str) -> str:
    """计算文件MD5
    参数：file_path - 文件路径
    返回：MD5哈希值
    被调用：document_service.upload()
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def delete_temp_files():
    """清理临时文件
    被调用：ingest_service.process_document()
    """
    temp_dir = tempfile.gettempdir()
    for filename in os.listdir(temp_dir):
        if filename.endswith('_chunk') or 'mineru_temp' in filename:
            file_path = os.path.join(temp_dir, filename)
            try:
                os.remove(file_path)
            except Exception:
                pass
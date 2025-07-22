"""
文件操作工具
处理CAD文件的导入导出和路径管理
"""

import importlib
import os
import cadquery as cq
from typing import Optional

def get_download_path(object_id: str, extension: str = "step") -> str:
    """
    获取CAD对象的下载文件路径，如果文件不存在则自动生成
    
    Args:
        object_id: 对象ID
        extension: 文件扩展名 (step, stl, obj, etc.)
    
    Returns:
        生成的文件路径
    """
    # Export the CAD object
    cad_file_path = f"data/generated/{object_id}.{extension}"
    if not os.path.exists(cad_file_path):
        spec = importlib.util.spec_from_file_location(
            "obj_module", f"data/generated/{object_id}.py"
        )
        obj_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(obj_module)

        cq.exporters.export(obj_module.obj, cad_file_path)
    return cad_file_path

def ensure_directory_exists(directory_path: str) -> None:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory_path: 目录路径
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def safe_file_read(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
    """
    安全地读取文件内容
    
    Args:
        file_path: 文件路径
        encoding: 文件编码
    
    Returns:
        文件内容，如果读取失败返回None
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except (FileNotFoundError, UnicodeDecodeError, PermissionError) as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def safe_file_write(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    安全地写入文件内容
    
    Args:
        file_path: 文件路径
        content: 要写入的内容
        encoding: 文件编码
    
    Returns:
        写入是否成功
    """
    try:
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory:
            ensure_directory_exists(directory)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except (PermissionError, OSError) as e:
        print(f"Error writing file {file_path}: {e}")
        return False

def get_file_size(file_path: str) -> Optional[int]:
    """
    获取文件大小
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件大小（字节），如果文件不存在返回None
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return None

def clean_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
    
    Returns:
        清理后的安全文件名
    """
    # 移除或替换非法字符
    illegal_chars = '<>:"/\\|?*'
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    
    # 移除首尾空格和点号
    filename = filename.strip(' .')
    
    # 如果文件名为空，使用默认名称
    if not filename:
        filename = 'untitled'
    
    return filename 
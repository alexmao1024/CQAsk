"""
后处理器模块
负责处理生成的CAD对象，如tessellation转换
"""

from .tessellation_processor import tessellate_cad_objects

__all__ = [
    'tessellate_cad_objects'
] 
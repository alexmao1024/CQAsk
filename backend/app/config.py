"""
应用配置管理
集中管理所有路径和配置项
"""

import os
from pathlib import Path

# 获取backend目录的绝对路径
BACKEND_DIR = Path(__file__).parent.parent

# 数据存储路径配置
class StoragePaths:
    """存储路径配置"""
    
    # 新的模块化路径（已迁移）
    DATA_DIR = BACKEND_DIR / "data"
    GENERATED_DIR = DATA_DIR / "generated"
    CONVERSATIONS_DIR = DATA_DIR / "conversations"
    ASSETS_DIR = DATA_DIR / "assets"
    
    @classmethod
    def ensure_directories(cls):
        """确保所有必要的目录存在"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.GENERATED_DIR.mkdir(exist_ok=True)
        cls.CONVERSATIONS_DIR.mkdir(exist_ok=True)
        cls.ASSETS_DIR.mkdir(exist_ok=True)

# 文件路径工具函数
class PathUtils:
    """路径工具函数"""
    
    @staticmethod
    def get_generated_file_path(file_id: str, extension: str = "py") -> str:
        """获取生成文件的路径"""
        return str(StoragePaths.GENERATED_DIR / f"{file_id}.{extension}")
    
    @staticmethod
    def get_conversation_file_path(conversation_id: str) -> str:
        """获取对话文件的路径"""
        return str(StoragePaths.CONVERSATIONS_DIR / f"{conversation_id}.json")
    
    @staticmethod
    def get_svg_file_path(file_id: str) -> str:
        """获取SVG文件的路径"""
        return str(StoragePaths.GENERATED_DIR / f"{file_id}.svg")

# AI模型配置
class AIConfig:
    """AI模型配置"""
    
    # API配置
    SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
    
    # 模型配置
    CODE_GENERATION_MODEL = "Qwen/Qwen2.5-72B-Instruct-128K"
    ERROR_ANALYSIS_MODEL = "deepseek-ai/DeepSeek-V3"
    
    # 重试配置
    MAX_RETRIES = 3
    MAX_SCHEMDRAW_RETRIES = 3

# 应用配置
class AppConfig:
    """应用配置"""
    
    # Flask配置
    HOST = "127.0.0.1"
    PORT = 5001
    DEBUG = True
    
    # CORS配置
    CORS_ORIGINS = ["http://localhost:3000"]

# 初始化配置
def init_config():
    """初始化配置，创建必要的目录"""
    StoragePaths.ensure_directories() 
"""
AI模块
包含所有与人工智能相关的功能
"""

from .llm_client import (
    LLMClient,
    CadQueryLLMClient, 
    SchemdrawLLMClient,
    ErrorAnalysisLLMClient,
    clean_code
)
from .error_analyzer import analyze_errors_with_ai, generate_friendly_error_message

__all__ = [
    'LLMClient',
    'CadQueryLLMClient',
    'SchemdrawLLMClient', 
    'ErrorAnalysisLLMClient',
    'clean_code',
    'analyze_errors_with_ai',
    'generate_friendly_error_message'
] 
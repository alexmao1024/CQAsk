"""
LLM客户端封装
负责与大语言模型的通信
"""

import os
import openai
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

class LLMClient:
    """LLM客户端基类"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.environ["SILICONFLOW_API_KEY"]
        self.base_url = base_url or "https://api.siliconflow.cn/v1"
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat_completion(self, model: str, messages: List[Dict[str, str]], **kwargs) -> str:
        """通用的聊天完成方法"""
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content

class CadQueryLLMClient(LLMClient):
    """CadQuery代码生成专用客户端"""
    
    def __init__(self):
        super().__init__()
        self.model = "Qwen/Qwen2.5-72B-Instruct-128K"
    
    def generate_code(self, user_msg: str, conversation_history: List[Dict[str, str]] = None, error_message: str = None) -> str:
        """生成CadQuery代码"""
        # 这里先保持原有逻辑，稍后从codex.py复制具体实现
        pass

class SchemdrawLLMClient(LLMClient):
    """Schemdraw代码生成专用客户端"""
    
    def __init__(self):
        super().__init__()
        self.model = "Qwen/Qwen2.5-72B-Instruct-128K"
    
    def generate_code(self, user_msg: str, conversation_history: List[Dict[str, str]] = None, error_message: str = None) -> str:
        """生成Schemdraw代码"""
        # 这里先保持原有逻辑，稍后从schemdraw_codegen.py复制具体实现
        pass

class ErrorAnalysisLLMClient(LLMClient):
    """错误分析专用客户端"""
    
    def __init__(self):
        super().__init__()
        self.model = "deepseek-ai/DeepSeek-V3"
    
    def analyze_errors(self, user_query: str, error_attempts: List[Dict[str, Any]]) -> str:
        """分析错误并生成友好的错误消息"""
        # 这里先保持原有逻辑，稍后从codex.py复制具体实现
        pass

# 工具函数
def clean_code(code_text: str) -> str:
    """清理模型生成的代码，移除 Markdown 格式标记"""
    lines = code_text.split('\n')
    clean_lines = []
    for line in lines:
        if line.strip() and not line.startswith('```') and not line.endswith('```'):
            clean_lines.append(line)
    return '\n'.join(clean_lines) 
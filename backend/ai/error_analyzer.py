"""
AI错误分析器
使用DeepSeek-V3分析错误并生成用户友好的错误信息
"""

import os
import openai
from dotenv import load_dotenv
from typing import List, Dict, Any
import traceback

load_dotenv()

# 错误分析客户端（使用DeepSeek-V3）
error_analysis_client = openai.OpenAI(
    api_key=os.environ["SILICONFLOW_API_KEY"],
    base_url="https://api.siliconflow.cn/v1",
)

def analyze_errors_with_ai(user_query: str, error_attempts: List[Dict[str, Any]]) -> str:
    """
    使用DeepSeek-V3分析错误并生成用户友好的错误信息
    
    Args:
        user_query: 用户的原始请求
        error_attempts: 包含每次尝试的错误信息的列表
    
    Returns:
        AI生成的用户友好错误分析
    """
    
    try:
        # 构建错误分析的prompt
        error_analysis_prompt = f"""你是一个CAD建模专家和用户体验专家。请分析以下CAD代码生成过程中遇到的错误，并为用户提供清晰、友好、可操作的建议。

用户请求："{user_query}"

错误尝试历史："""

        for i, attempt in enumerate(error_attempts, 1):
            error_analysis_prompt += f"""

=== 尝试 {i} ===
错误类型：{attempt.get('type', '未知')}
错误信息：{attempt.get('message', '无详细信息')}
"""
            if attempt.get('traceback'):
                error_analysis_prompt += f"详细追踪：{attempt.get('traceback')[:500]}..."

        error_analysis_prompt += """

请根据以上信息：

1. 分析可能的根本原因
2. 用通俗易懂的语言解释问题
3. 提供具体的、可操作的解决建议
4. 如果可能，建议用户如何重新表述需求

回复要求：
- 使用友好、专业的语调
- 避免技术术语，用普通用户能理解的语言
- 提供具体的下一步操作建议
- 如果是2D/3D渲染问题，要明确指出
- 回复长度控制在300字以内，简洁明了

请直接给出分析结果，不要包含多余的格式或标题。"""

        print(f"Sending error analysis request to DeepSeek-V3...")
        print(f"Error attempts count: {len(error_attempts)}")
        
        response = error_analysis_client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {"role": "system", "content": "你是一个专业的CAD软件技术支持专家，擅长将技术问题转化为用户容易理解的解决方案。"},
                {"role": "user", "content": error_analysis_prompt}
            ],
            max_tokens=800,
            temperature=0.3,
        )
        
        ai_analysis = response.choices[0].message.content.strip()
        print(f"AI analysis completed successfully: {ai_analysis[:100]}...")
        return ai_analysis
        
    except Exception as e:
        print(f"AI error analysis failed: {e}")
        traceback.print_exc()
        # 返回一个通用的友好错误消息作为后备
        return generate_friendly_error_message(user_query, error_attempts)

def generate_friendly_error_message(user_query: str, error_attempts: List[Dict[str, Any]]) -> str:
    """
    生成通用的友好错误消息（AI分析失败时的后备方案）
    """
    error_count = len(error_attempts)
    
    # 分析错误类型
    error_types = [attempt.get('type', '未知') for attempt in error_attempts]
    common_error_types = set(error_types)
    
    # 基础错误消息
    base_message = f"抱歉，尝试了{error_count}次都无法完成您的请求 \"{user_query}\"。"
    
    # 根据错误类型提供建议
    if 'TessellationError' in common_error_types:
        suggestion = "这可能是因为生成的是2D内容，建议您尝试切换到'2D渲染'模式，或者在描述中明确指出需要3D立体模型。"
    elif 'SyntaxError' in common_error_types:
        suggestion = "代码语法有问题，建议您简化描述，使用更基础的几何形状术语。"
    elif 'ImportError' in common_error_types or 'ModuleNotFoundError' in common_error_types:
        suggestion = "系统库缺失，请联系管理员检查环境配置。"
    elif 'ValueError' in common_error_types:
        suggestion = "参数设置有问题，建议您提供更具体的尺寸和形状描述。"
    else:
        suggestion = "建议您：1) 简化描述；2) 使用基础几何形状；3) 提供具体的尺寸要求；4) 或联系技术支持。"
    
    return f"{base_message} {suggestion}" 
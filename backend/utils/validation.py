"""
验证工具
提供输入验证和数据校验功能
"""

import re
from typing import Any, Dict, List, Optional, Union

def validate_object_id(object_id: str) -> bool:
    """
    验证对象ID格式是否正确
    
    Args:
        object_id: 对象ID字符串
    
    Returns:
        验证是否通过
    """
    if not object_id or not isinstance(object_id, str):
        return False
    
    # 检查是否符合ISO 8601时间戳格式（去除冒号）
    pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d{6}$'
    return bool(re.match(pattern, object_id))

def validate_conversation_id(conversation_id: str) -> bool:
    """
    验证对话ID格式是否正确
    
    Args:
        conversation_id: 对话ID字符串
    
    Returns:
        验证是否通过
    """
    return validate_object_id(conversation_id)  # 格式相同

def validate_render_mode(render_mode: str) -> bool:
    """
    验证渲染模式是否有效
    
    Args:
        render_mode: 渲染模式字符串
    
    Returns:
        验证是否通过
    """
    valid_modes = {'2d', '3d'}
    return render_mode in valid_modes

def validate_user_query(query: str) -> Dict[str, Any]:
    """
    验证用户查询内容
    
    Args:
        query: 用户查询字符串
    
    Returns:
        验证结果字典，包含是否通过和错误信息
    """
    result = {"valid": True, "errors": []}
    
    if not query or not isinstance(query, str):
        result["valid"] = False
        result["errors"].append("查询内容不能为空")
        return result
    
    # 检查长度
    if len(query.strip()) < 2:
        result["valid"] = False
        result["errors"].append("查询内容过短，请提供更详细的描述")
    
    if len(query) > 1000:
        result["valid"] = False
        result["errors"].append("查询内容过长，请简化描述")
    
    # 检查是否包含潜在的恶意内容
    dangerous_patterns = [
        r'import\s+os',
        r'import\s+subprocess',
        r'exec\s*\(',
        r'eval\s*\(',
        r'__import__',
        r'open\s*\(',
        r'file\s*\(',
        r'input\s*\(',
        r'raw_input\s*\('
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            result["valid"] = False
            result["errors"].append("查询内容包含不安全的代码片段")
            break
    
    return result

def validate_api_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证API请求数据
    
    Args:
        data: 请求数据字典
    
    Returns:
        验证结果字典
    """
    result = {"valid": True, "errors": []}
    
    # 检查必需字段
    if "query" not in data:
        result["valid"] = False
        result["errors"].append("缺少必需的查询字段")
        return result
    
    # 验证查询内容
    query_validation = validate_user_query(data["query"])
    if not query_validation["valid"]:
        result["valid"] = False
        result["errors"].extend(query_validation["errors"])
    
    # 验证可选字段
    if "render_mode" in data:
        if not validate_render_mode(data["render_mode"]):
            result["valid"] = False
            result["errors"].append("无效的渲染模式，必须是 '2d' 或 '3d'")
    
    if "conversation_id" in data and data["conversation_id"]:
        if not validate_conversation_id(data["conversation_id"]):
            result["valid"] = False
            result["errors"].append("无效的对话ID格式")
    
    return result

def sanitize_user_input(user_input: str) -> str:
    """
    清理用户输入，移除潜在的危险内容
    
    Args:
        user_input: 用户输入字符串
    
    Returns:
        清理后的安全字符串
    """
    if not isinstance(user_input, str):
        return ""
    
    # 移除控制字符
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', user_input)
    
    # 限制长度
    if len(cleaned) > 1000:
        cleaned = cleaned[:1000]
    
    # 移除首尾空白
    cleaned = cleaned.strip()
    
    return cleaned

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    验证文件扩展名是否在允许列表中
    
    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名列表
    
    Returns:
        验证是否通过
    """
    if not filename or not isinstance(filename, str):
        return False
    
    # 提取文件扩展名
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    return extension in [ext.lower().lstrip('.') for ext in allowed_extensions]

def is_safe_path(path: str, base_path: str = "") -> bool:
    """
    检查路径是否安全，防止路径遍历攻击
    
    Args:
        path: 要检查的路径
        base_path: 基础路径
    
    Returns:
        路径是否安全
    """
    if not path or not isinstance(path, str):
        return False
    
    # 检查危险的路径模式
    dangerous_patterns = ['../', '..\\', '/..', '\\..']
    for pattern in dangerous_patterns:
        if pattern in path:
            return False
    
    # 检查绝对路径
    if path.startswith('/') or (len(path) > 1 and path[1] == ':'):
        return False
    
    return True 
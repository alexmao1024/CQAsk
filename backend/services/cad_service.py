"""
CAD服务层
封装CAD生成的核心业务逻辑
"""

from typing import Dict, Any, Optional, Tuple, List
import traceback

from generators import generate_cq_obj, generate_schemdraw_code
from processors import tessellate_cad_objects
from ai import analyze_errors_with_ai
from models import ConversationManager
from utils import validate_api_request_data, sanitize_user_input

class CADService:
    """CAD生成服务"""
    
    def __init__(self):
        self.conversation_manager = ConversationManager()
        self.max_retries = 3
    
    def generate_cad(self, query: str, conversation_id: Optional[str] = None, render_mode: str = "3d") -> Dict[str, Any]:
        """
        生成CAD对象的主要业务逻辑
        
        Args:
            query: 用户查询
            conversation_id: 对话ID（可选）
            render_mode: 渲染模式 ('2d' 或 '3d')
        
        Returns:
            生成结果字典
        """
        # 输入验证和清理
        query = sanitize_user_input(query)
        
        # 处理对话历史
        conversation_history = []
        if conversation_id:
            conversation_history = self.conversation_manager.get_conversation_history(conversation_id)
            # 添加用户消息到对话
            self.conversation_manager.add_user_message(conversation_id, query)
        else:
            # 创建新对话
            conversation_id = self.conversation_manager.create_conversation(query)
        
        # 根据渲染模式选择生成策略
        if render_mode == "2d":
            return self._generate_2d_cad(query, conversation_id, conversation_history)
        else:
            return self._generate_3d_cad(query, conversation_id, conversation_history)
    
    def _generate_2d_cad(self, query: str, conversation_id: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """生成2D CAD的业务逻辑"""
        accumulated_errors = []
        
        for attempt in range(self.max_retries):
            try:
                # 获取错误信息（如果是重试）
                error_message = None
                if attempt > 0:
                    last_error = accumulated_errors[-1] if accumulated_errors else None
                    if last_error:
                        error_message = f"{last_error['type']}: {last_error['message']}"

                # 生成schemdraw代码
                result = generate_schemdraw_code(query, conversation_history, error_message)

                if len(result) == 3:
                    object_id, svg_content, error_info = result

                    if error_info:
                        # 代码执行失败
                        print(f"--- 2D Generation Attempt {attempt + 1} Failed ---")
                        print(f"Error Type: {error_info.get('type')}")
                        print(f"Error Message: {error_info.get('message')}")
                        print(f"Traceback: \n{error_info.get('traceback')}")
                        print("--------------------------------------")
                        accumulated_errors.append(error_info)

                        if attempt == self.max_retries - 1:
                            # 最后一次重试失败，使用AI分析错误
                            friendly_error = analyze_errors_with_ai(query, accumulated_errors)
                            self.conversation_manager.add_assistant_message(
                                conversation_id, "", None, friendly_error, "2d"
                            )
                            return {
                                "success": False,
                                "error": friendly_error,
                                "conversation_id": conversation_id,
                                "retry_count": attempt + 1,
                                "generator": "schemdraw"
                            }
                        continue

                    # 生成成功
                    # 读取生成的代码
                    with open(f"data/generated/{object_id}.py", "r", encoding="utf-8") as f:
                        generated_code = f.read()

                    self.conversation_manager.add_assistant_message(
                        conversation_id, generated_code, object_id, None, "2d"
                    )

                    return {
                        "success": True,
                        "id": object_id,
                        "svg": svg_content,
                        "code": generated_code,
                        "render_mode": "2d",
                        "conversation_id": conversation_id,
                        "generator": "schemdraw"
                    }

            except Exception as e:
                # 系统级错误
                system_error = {
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
                print(f"--- 2D Generation Attempt {attempt + 1} System Error ---")
                print(f"Error Type: {system_error.get('type')}")
                print(f"Error Message: {system_error.get('message')}")
                print(f"Traceback: \n{system_error.get('traceback')}")
                print("---------------------------------------------")
                accumulated_errors.append(system_error)

                if attempt == self.max_retries - 1:
                    friendly_error = analyze_errors_with_ai(query, accumulated_errors)
                    return {
                        "success": False,
                        "error": friendly_error,
                        "conversation_id": conversation_id,
                        "retry_count": attempt + 1,
                        "generator": "schemdraw"
                    }
                continue

        # 理论上不应该到达这里
        return {
            "success": False,
            "error": "2D生成过程出现未知错误",
            "conversation_id": conversation_id,
            "generator": "schemdraw"
        }

    def _generate_3d_cad(self, query: str, conversation_id: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """生成3D CAD的业务逻辑"""
        accumulated_errors = []

        for attempt in range(self.max_retries):
            try:
                # 获取错误信息（如果是重试）
                error_message = None
                if attempt > 0:
                    last_error = accumulated_errors[-1] if accumulated_errors else None
                    if last_error:
                        error_message = f"{last_error['type']}: {last_error['message']}"

                # 生成CadQuery代码
                result = generate_cq_obj(query, conversation_history, error_message)

                if len(result) == 3:
                    object_id, obj, error_info = result

                    if error_info:
                        # CadQuery代码执行失败
                        print(f"--- 3D Generation Attempt {attempt + 1} Failed ---")
                        print(f"Error Type: {error_info.get('type')}")
                        print(f"Error Message: {error_info.get('message')}")
                        print(f"Traceback: \n{error_info.get('traceback')}")
                        print("--------------------------------------")
                        accumulated_errors.append(error_info)

                        if attempt == self.max_retries - 1:
                            friendly_error = analyze_errors_with_ai(query, accumulated_errors)
                            self.conversation_manager.add_assistant_message(
                                conversation_id, "", None, friendly_error, "3d"
                            )
                            return {
                                "success": False,
                                "error": friendly_error,
                                "conversation_id": conversation_id,
                                "retry_count": attempt + 1,
                                "generator": "cadquery"
                            }
                        continue

                    # CadQuery生成成功，尝试tessellation
                    try:
                        meshed_instances, shapes, mapping = tessellate_cad_objects(obj)

                        if not shapes or not meshed_instances:
                            # tessellation失败
                            tessellation_error = {
                                "type": "TessellationError",
                                "message": "无法对生成的对象进行三角剖分，可能是2D内容",
                                "traceback": "Generated object cannot be tessellated for 3D rendering"
                            }
                            print(f"--- 3D Tessellation Attempt {attempt + 1} Failed ---")
                            print(f"Error Type: {tessellation_error.get('type')}")
                            print(f"Error Message: {tessellation_error.get('message')}")
                            print("---------------------------------------------")
                            accumulated_errors.append(tessellation_error)

                            if attempt == self.max_retries - 1:
                                friendly_error = analyze_errors_with_ai(query, accumulated_errors)
                                return {
                                    "success": False,
                                    "error": friendly_error,
                                    "suggestion": "try_2d_mode",
                                    "conversation_id": conversation_id,
                                    "retry_count": attempt + 1
                                }
                            continue

                        # 3D生成完全成功
                        # 读取生成的代码
                        with open(f"data/generated/{object_id}.py", "r", encoding="utf-8") as f:
                            generated_code = f.read()

                        self.conversation_manager.add_assistant_message(
                            conversation_id, generated_code, object_id, None, "3d"
                        )

                        return {
                            "success": True,
                            "id": object_id,
                            # 将 shapes 和 meshed_instances 打包成一个数组
                            "shapes": [shapes, meshed_instances],
                            "code": generated_code,
                            "render_mode": "3d",
                            "conversation_id": conversation_id,
                            "generator": "cadquery"
                        }

                    except Exception as tessellation_error:
                        # tessellation系统错误
                        system_error = {
                            "type": type(tessellation_error).__name__,
                            "message": str(tessellation_error),
                            "traceback": traceback.format_exc()
                        }
                        print(f"--- 3D Tessellation Attempt {attempt + 1} System Error ---")
                        print(f"Error Type: {system_error.get('type')}")
                        print(f"Error Message: {system_error.get('message')}")
                        print(f"Traceback: \n{system_error.get('traceback')}")
                        print("-----------------------------------------------------")
                        accumulated_errors.append(system_error)

                        if attempt == self.max_retries - 1:
                            friendly_error = analyze_errors_with_ai(query, accumulated_errors)
                            return {
                                "success": False,
                                "error": friendly_error,
                                "conversation_id": conversation_id,
                                "retry_count": attempt + 1
                            }
                        continue

            except Exception as e:
                # CadQuery生成系统级错误
                system_error = {
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
                print(f"--- 3D Generation Attempt {attempt + 1} System Error ---")
                print(f"Error Type: {system_error.get('type')}")
                print(f"Error Message: {system_error.get('message')}")
                print(f"Traceback: \n{system_error.get('traceback')}")
                print("---------------------------------------------")
                accumulated_errors.append(system_error)

                if attempt == self.max_retries - 1:
                    friendly_error = analyze_errors_with_ai(query, accumulated_errors)
                    return {
                        "success": False,
                        "error": friendly_error,
                        "conversation_id": conversation_id,
                        "retry_count": attempt + 1
                    }
                continue

        # 理论上不应该到达这里
        return {
            "success": False,
            "error": "3D生成过程出现未知错误",
            "conversation_id": conversation_id,
            "generator": "cadquery"
        }
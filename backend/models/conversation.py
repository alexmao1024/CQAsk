"""
多轮对话管理模块
处理对话历史、错误重试等功能
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class ConversationManager:
    def __init__(self, conversations_dir: str = "data/conversations"):
        self.conversations_dir = conversations_dir
        if not os.path.exists(conversations_dir):
            os.makedirs(conversations_dir)

    def _load_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """加载对话数据"""
        if not conversation_id:
            return None
        file_path = os.path.join(self.conversations_dir, f"{conversation_id}.json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _save_conversation(self, conversation_id: str, conversation: Dict[str, Any]):
        """保存对话数据"""
        file_path = os.path.join(self.conversations_dir, f"{conversation_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)

    def create_conversation(self, user_query: str) -> str:
        """创建新对话"""
        conversation_id = datetime.now().isoformat().replace(":", "-")
        conversation = {
            "id": conversation_id,
            "created_at": datetime.now().isoformat(),
            "messages": [
                {
                    "role": "user",
                    "content": user_query,
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "current_code": None,
            "current_object_id": None,
            "render_mode": None,
            "error_history": []
        }
        self._save_conversation(conversation_id, conversation)
        return conversation_id

    def add_user_message(self, conversation_id: str, user_query: str) -> bool:
        """添加用户消息"""
        conversation = self._load_conversation(conversation_id)
        if not conversation:
            return False
        conversation["messages"].append({
            "role": "user",
            "content": user_query,
            "timestamp": datetime.now().isoformat()
        })
        self._save_conversation(conversation_id, conversation)
        return True

    def add_assistant_message(self, conversation_id: str, code: str, object_id: Optional[str], error_message: Optional[str] = None, render_mode: Optional[str] = None):
        """添加助手回复"""
        conversation = self._load_conversation(conversation_id)
        if not conversation: return False

        message = {
            "role": "assistant", "timestamp": datetime.now().isoformat(),
            "code": code, "object_id": object_id, "error": error_message,
            "render_mode": render_mode
        }
        conversation["messages"].append(message)

        if render_mode: conversation["render_mode"] = render_mode
        if error_message:
            conversation["error_history"].append({"timestamp": message["timestamp"], "error": error_message})
        else:
            conversation["current_code"] = code
            conversation["current_object_id"] = object_id

        self._save_conversation(conversation_id, conversation)
        return True

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """获取完整的对话历史用于发送给大模型"""
        conversation = self._load_conversation(conversation_id)
        if not conversation: return []

        history = []
        for msg in conversation["messages"]:
            content = msg.get("code") if msg["role"] == "assistant" else msg.get("content")
            if content:
                 history.append({"role": msg["role"], "content": content})
        return history

    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """获取所有对话的摘要信息"""
        conversations = []
        if not os.path.exists(self.conversations_dir):
            return conversations

        files = os.listdir(self.conversations_dir)
        files.sort(reverse=True)

        for filename in files:
            if filename.endswith('.json'):
                conversation = self._load_conversation(filename[:-5])
                if conversation:
                    first_user_message = next((msg["content"] for msg in conversation["messages"] if msg["role"] == "user"), "")
                    assistant_responses = sum(1 for msg in conversation["messages"] if msg["role"] == "assistant" and msg.get("object_id"))

                    # 只添加有成功结果的对话，以匹配前端逻辑
                    if assistant_responses > 0:
                        conversations.append({
                            "id": conversation["id"],
                            "created_at": conversation["created_at"],
                            "title": first_user_message[:50] + ("..." if len(first_user_message) > 50 else ""),
                            "message_count": len(conversation["messages"]),
                            "assistant_responses": assistant_responses,
                            "current_object_id": conversation.get("current_object_id")
                        })
        return conversations

    def get_conversation_detail(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """获取对话的详细信息，为前端准备格式化的数据"""
        conversation = self._load_conversation(conversation_id)
        if not conversation:
            return None

        processed_messages = []
        for i, msg in enumerate(conversation["messages"]):
            processed_msg = {
                "index": i, "role": msg["role"],
                "content": msg.get("code") or msg.get("content"), # 优先显示code
                "timestamp": msg["timestamp"]
            }
            if msg["role"] == "assistant":
                processed_msg["object_id"] = msg.get("object_id")
                processed_msg["error"] = msg.get("error")
                processed_msg["has_result"] = bool(msg.get("object_id"))
            processed_messages.append(processed_msg)

        return {
            "id": conversation_id,
            "created_at": conversation["created_at"],
            "messages": processed_messages,
            "current_object_id": conversation.get("current_object_id")
        }

    def get_message_result(self, conversation_id: str, message_index: int) -> Optional[Dict[str, Any]]:
        """获取特定消息的渲染结果"""
        conversation = self._load_conversation(conversation_id)
        if not conversation or message_index >= len(conversation["messages"]):
            return None

        message = conversation["messages"][message_index]
        render_mode = message.get("render_mode")
        object_id = message.get("object_id")

        if message["role"] != "assistant" or not object_id:
            return {"error": "This message has no associated CAD object."}

        # 重新生成数据
        try:
            code_file = f"data/generated/{object_id}.py"
            if not os.path.exists(code_file):
                return {"error": "Code file not found"}

            with open(code_file, "r", encoding="utf-8") as f:
                code_content = f.read()

            # --- Logic for 2D results ---
            if render_mode == "2d":
                svg_file = f"data/generated/{object_id}.svg"
                if not os.path.exists(svg_file):
                    return {"error": "SVG file for 2D object not found."}

                with open(svg_file, "r", encoding="utf-8") as f:
                    svg_content = f.read()

                return {
                    "id": object_id,
                    "svg": svg_content,
                    "code": code_content,
                    "render_mode": render_mode,
                    "conversation_id": conversation_id,
                }

            # --- Logic for 3D results ---
            elif render_mode == "3d":
                exec_globals = {}
                exec(code_content, exec_globals)

                if 'obj' not in exec_globals:
                    return {"error": "No 'obj' variable found in the generated code"}

                from processors.tessellation_processor import tessellate_cad_objects
                meshed_instances, shapes, _ = tessellate_cad_objects(exec_globals['obj'])

                return {
                    "id": object_id,
                    "shapes": [shapes, meshed_instances],
                    "conversation_id": conversation_id,
                    "code": code_content,
                    "render_mode": render_mode
                }

            else:
                return {"error": f"Unknown render mode: {render_mode}"}

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"Failed to regenerate result: {str(e)}"}
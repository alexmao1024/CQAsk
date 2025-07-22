"""
多轮对话管理模块
处理对话历史、错误重试等功能
"""

import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

class ConversationManager:
    def __init__(self, conversations_dir: str = "conversations"):
        self.conversations_dir = conversations_dir
        if not os.path.exists(conversations_dir):
            os.makedirs(conversations_dir)
    
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
            "retry_count": 0
        }
        
        self._save_conversation(conversation_id, conversation)
        return conversation_id
    
    def add_user_message(self, conversation_id: str, message: str) -> bool:
        """添加用户消息到现有对话"""
        conversation = self._load_conversation(conversation_id)
        if not conversation:
            return False
        
        conversation["messages"].append({
            "role": "user", 
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # 重置重试计数
        conversation["retry_count"] = 0
        
        self._save_conversation(conversation_id, conversation)
        return True
    
    def add_assistant_message(self, conversation_id: str, code: str, object_id: str = None, error: str = None) -> bool:
        """添加助手回复"""
        conversation = self._load_conversation(conversation_id)
        if not conversation:
            return False
        
        message = {
            "role": "assistant",
            "content": code,
            "timestamp": datetime.now().isoformat()
        }
        
        if error:
            message["error"] = error
        
        if object_id:
            message["object_id"] = object_id
            conversation["current_object_id"] = object_id
        
        conversation["messages"].append(message)
        conversation["current_code"] = code
        
        self._save_conversation(conversation_id, conversation)
        return True
    
    def add_error_retry(self, conversation_id: str, error_message: str) -> bool:
        """记录错误重试"""
        conversation = self._load_conversation(conversation_id)
        if not conversation:
            return False
        
        conversation["retry_count"] = conversation.get("retry_count", 0) + 1
        
        # 添加错误信息到最后一条助手消息
        if conversation["messages"] and conversation["messages"][-1]["role"] == "assistant":
            conversation["messages"][-1]["error"] = error_message
            conversation["messages"][-1]["retry_count"] = conversation["retry_count"]
        
        self._save_conversation(conversation_id, conversation)
        return True
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """获取对话历史用于发送给大模型"""
        conversation = self._load_conversation(conversation_id)
        if not conversation:
            return []
        
        # 转换为大模型需要的格式
        history = []
        for msg in conversation["messages"]:
            if msg["role"] == "user":
                history.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                history.append({"role": "assistant", "content": msg["content"]})
        
        return history
    
    def get_retry_count(self, conversation_id: str) -> int:
        """获取当前重试次数"""
        conversation = self._load_conversation(conversation_id)
        if not conversation:
            return 0
        return conversation.get("retry_count", 0)
    
    def get_current_object_id(self, conversation_id: str) -> Optional[str]:
        """获取当前对象ID"""
        conversation = self._load_conversation(conversation_id)
        if not conversation:
            return None
        return conversation.get("current_object_id")
    
    def _load_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """加载对话数据"""
        file_path = os.path.join(self.conversations_dir, f"{conversation_id}.json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """获取所有对话的摘要信息"""
        conversations = []
        
        if not os.path.exists(self.conversations_dir):
            return conversations
        
        for filename in os.listdir(self.conversations_dir):
            if filename.endswith('.json'):
                conversation_id = filename[:-5]  # 移除.json后缀
                conversation = self._load_conversation(conversation_id)
                
                if conversation:
                    # 提取摘要信息
                    first_user_message = ""
                    assistant_messages_count = 0
                    
                    for msg in conversation["messages"]:
                        if msg["role"] == "user" and not first_user_message:
                            first_user_message = msg["content"]
                        elif msg["role"] == "assistant":
                            assistant_messages_count += 1
                    
                    conversations.append({
                        "id": conversation_id,
                        "created_at": conversation["created_at"],
                        "title": first_user_message[:50] + ("..." if len(first_user_message) > 50 else ""),
                        "message_count": len(conversation["messages"]),
                        "assistant_responses": assistant_messages_count,
                        "current_object_id": conversation.get("current_object_id")
                    })
        
        # 按创建时间倒序排列
        conversations.sort(key=lambda x: x["created_at"], reverse=True)
        return conversations
    
    def get_conversation_detail(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """获取对话的详细信息，包括所有消息"""
        conversation = self._load_conversation(conversation_id)
        if not conversation:
            return None
        
        # 处理消息，为前端准备格式化的数据
        processed_messages = []
        for i, msg in enumerate(conversation["messages"]):
            processed_msg = {
                "index": i,
                "role": msg["role"],
                "content": msg["content"],
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
        
        if message["role"] != "assistant" or not message.get("object_id"):
            return None
        
        object_id = message["object_id"]
        
        # 重新生成tessellation数据
        try:
            # 读取生成的代码文件
            code_file = f"generated/{object_id}.py"
            if not os.path.exists(code_file):
                return {"error": "Code file not found"}
            
            with open(code_file, "r", encoding="utf-8") as f:
                code_content = f.read()
            
            # 重新执行代码获取对象
            exec_globals = {}
            exec(code_content, exec_globals)
            
            if 'obj' not in exec_globals:
                return {"error": "No 'obj' variable found in code"}
            
            obj = exec_globals['obj']
            
            # 重新tessellate
            from utils.tessellate import tessellate_cad_objects
            converted_obj = tessellate_cad_objects([obj])
            (shapes, meshed_instances), mapping = converted_obj
            
            return {
                "id": object_id,
                "shapes": (shapes, meshed_instances),
                "conversation_id": conversation_id,
                "message_index": message_index,
                "code": code_content
            }
            
        except Exception as e:
            return {"error": f"Failed to regenerate result: {str(e)}"}
    
    def _save_conversation(self, conversation_id: str, conversation: Dict[str, Any]):
        """保存对话数据"""
        file_path = os.path.join(self.conversations_dir, f"{conversation_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)

# 全局对话管理器实例
conversation_manager = ConversationManager() 
"""
对话服务层
封装对话管理的业务逻辑
"""
from typing import Dict, Any, List, Optional
from models.conversation import ConversationManager

class ConversationService:
    """对话管理服务"""

    def __init__(self):
        self.conversation_manager = ConversationManager()

    def get_recent_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取最近的对话列表"""
        all_convos = self.conversation_manager.get_all_conversations()
        return all_convos[:limit]

    def get_conversation_detail(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """获取对话详细信息"""
        return self.conversation_manager.get_conversation_detail(conversation_id)

    def get_message_result(self, conversation_id: str, message_index: int) -> Optional[Dict[str, Any]]:
        """获取单个消息的结果"""
        return self.conversation_manager.get_message_result(conversation_id, message_index)

    # 其他方法可以保持原样，因为它们大多是简单的调用
    def search_conversations(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """搜索对话"""
        # 注意：这里的搜索返回的是原始对话，需要包装成摘要
        conversations = self.conversation_manager.search_conversations(query, limit)
        return [self.conversation_manager.get_conversation_summary(conv) for conv in conversations]

    def delete_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """删除对话"""
        success = self.conversation_manager.delete_conversation(conversation_id)
        return {"success": success, "message": "对话删除成功" if success else "对话删除失败"}
"""
对话管理相关的API路由
"""
import json
import traceback

from flask import Blueprint, jsonify, Response
from flask_cors import cross_origin
from services.conversation_service import ConversationService
from utils.json_utils import NumpyEncoder

conversation_bp = Blueprint('conversation', __name__)
conversation_service = ConversationService()

@conversation_bp.route("/conversations", methods=["GET"])
@cross_origin()
def get_conversations():
    """获取所有对话历史摘要"""
    try:
        conversations = conversation_service.get_recent_conversations()
        return jsonify({"conversations": conversations})
    except Exception as e:
        print(f"Error getting conversations: {e}")
        return jsonify({"error": str(e)}), 500

@conversation_bp.route("/conversation/<conversation_id>", methods=["GET"])
@cross_origin()
def get_conversation_detail(conversation_id):
    """获取特定对话的详细信息"""
    try:
        conversation = conversation_service.get_conversation_detail(conversation_id)
        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404
        return jsonify(conversation)
    except Exception as e:
        print(f"Error getting conversation detail: {e}")
        return jsonify({"error": str(e)}), 500

@conversation_bp.route("/conversation/<conversation_id>/message/<int:message_index>", methods=["GET"])
@cross_origin()
def get_message_result(conversation_id, message_index):
    """获取特定消息的结果"""
    try:
        result = conversation_service.get_message_result(conversation_id, message_index)
        if not result:
            return jsonify({"error": "Message or result not found"}), 404

        serialized_data = json.dumps(result, cls=NumpyEncoder)
        return Response(serialized_data, mimetype='application/json')

    except Exception as e:
        print(f"Error getting message result: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
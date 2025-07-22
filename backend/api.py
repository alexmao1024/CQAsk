from flask import Flask, request, send_file
import json
from utils.download import get_donwload_string
from codex import generate_cq_obj
from utils.json import NumpyEncoder
from utils.tessellate import tessellate_cad_objects as tessellate
from flask import jsonify
from flask_cors import CORS, cross_origin
from flask import request
from conversation import conversation_manager

from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


@cross_origin()
@app.route("/cad", methods=["POST"])
def cad():
    data = request.get_json()
    query = data.get("query")
    conversation_id = data.get("conversation_id")
    
    print(f"=== API /cad called ===")
    print(f"Query: '{query}'")
    print(f"Conversation ID: {conversation_id}")
    
    # 确定是新对话还是继续对话
    if conversation_id:
        # 继续现有对话
        success = conversation_manager.add_user_message(conversation_id, query)
        if not success:
            return jsonify({"error": "Invalid conversation ID"}), 400
        
        conversation_history = conversation_manager.get_conversation_history(conversation_id)
    else:
        # 创建新对话
        conversation_id = conversation_manager.create_conversation(query)
        conversation_history = None
    
    # 尝试生成CAD对象，最多重试3次
    max_retries = 3
    
    for attempt in range(max_retries):
        print(f"Attempt {attempt + 1}/{max_retries}")
        
        try:
            # 获取错误信息（如果是重试）
            error_message = None
            if attempt > 0:
                print("This is a retry attempt")
                # 模拟获取上次的错误信息 - 这里应该从对话管理器获取
            
            # 生成代码
            print("Step 1: Calling generate_cq_obj...")
            result = generate_cq_obj(query, conversation_history, error_message)
            
            if len(result) == 3:
                id, obj, error_info = result
                if error_info:
                    # 代码执行失败
                    error_msg = f"{error_info['type']}: {error_info['message']}"
                    print(f"Code execution failed: {error_msg}")
                    
                    # 记录错误重试
                    conversation_manager.add_error_retry(conversation_id, error_msg)
                    
                    if attempt == max_retries - 1:
                        # 最后一次重试也失败了
                        conversation_manager.add_assistant_message(conversation_id, "", None, error_msg)
                        return jsonify({
                            "error": f"Failed to generate valid code after {max_retries} attempts. Last error: {error_msg}",
                            "conversation_id": conversation_id,
                            "retry_count": attempt + 1
                        }), 500
                    
                    # 准备重试
                    error_message = error_msg
                    continue
                
                # 代码执行成功
                print(f"Step 1 completed - ID: {id}, Object type: {type(obj)}")
                
            else:
                # 兼容旧版本返回格式
                id, obj = result
                error_info = None
            
            # 尝试tessellation
            print("Step 2: Calling tessellate...")
            converted_obj = tessellate([obj])
            (shapes, meshed_instances), mapping = converted_obj
            
            # 验证数据是否有效
            if not shapes or not meshed_instances:
                print(f"ERROR: Invalid tessellation result")
                return jsonify({
                    "error": "Tessellation failed", 
                    "conversation_id": conversation_id
                }), 500
            
            print(f"SUCCESS: Tessellation completed")
            print(f"  Shapes keys: {list(shapes.keys()) if isinstance(shapes, dict) else 'Not a dict'}")
            print(f"  Meshed instances length: {len(meshed_instances) if meshed_instances else 0}")
            
            # 保存成功的代码到对话历史
            with open(f"generated/{id}.py", "r", encoding="utf-8") as f:
                generated_code = f.read()
            
            conversation_manager.add_assistant_message(conversation_id, generated_code, id)
            
            # 返回数据给前端
            response_data = {
                "id": id,
                "shapes": (shapes, meshed_instances),
                "conversation_id": conversation_id,
                "success": True
            }
            
            # 使用json.dumps进行序列化
            import json
            from flask import Response
            serialized_data = json.dumps(response_data, cls=NumpyEncoder)
            return Response(serialized_data, mimetype='application/json')
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            
            if attempt == max_retries - 1:
                # 最后一次重试也失败了
                return jsonify({
                    "error": error_msg,
                    "conversation_id": conversation_id,
                    "retry_count": attempt + 1
                }), 500
            
            # 准备重试
            error_message = error_msg
            continue
    
    # 理论上不应该到达这里
    return jsonify({
        "error": "Unexpected error in retry loop",
        "conversation_id": conversation_id
    }), 500


@cross_origin()
@app.route("/conversations", methods=["GET"])
def get_conversations():
    """获取所有对话历史"""
    try:
        conversations = conversation_manager.get_all_conversations()
        return jsonify({"conversations": conversations})
    except Exception as e:
        print(f"Error getting conversations: {e}")
        return jsonify({"error": str(e)}), 500

@cross_origin()
@app.route("/conversation/<conversation_id>", methods=["GET"])
def get_conversation_detail(conversation_id):
    """获取特定对话的详细信息"""
    try:
        conversation = conversation_manager.get_conversation_detail(conversation_id)
        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404
        return jsonify(conversation)
    except Exception as e:
        print(f"Error getting conversation detail: {e}")
        return jsonify({"error": str(e)}), 500

@cross_origin()
@app.route("/conversation/<conversation_id>/message/<int:message_index>", methods=["GET"])
def get_conversation_message(conversation_id, message_index):
    """获取特定对话中的特定消息及其结果"""
    try:
        result = conversation_manager.get_message_result(conversation_id, message_index)
        if not result:
            return jsonify({"error": "Message not found"}), 404
        
        # 使用NumpyEncoder进行序列化
        import json
        from flask import Response
        serialized_data = json.dumps(result, cls=NumpyEncoder)
        return Response(serialized_data, mimetype='application/json')
        
    except Exception as e:
        print(f"Error getting message result: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@cross_origin()
@app.route("/download", methods=["GET"])
def download():
    id = request.args.get("id")
    file_type = request.args.get("file_type")
    file_path = get_donwload_string(id, file_type)
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        print(e)
        return jsonify({"error": f"Something went wrong.{e}"})


if __name__ == "__main__":
    app.run(debug=True, port=5001)

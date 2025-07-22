"""
CAD相关的API路由
处理CAD生成、文件下载等请求
"""

from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin
from services import CADService
from utils import validate_api_request_data, get_download_path

# 创建CAD蓝图
cad_bp = Blueprint('cad', __name__)

# 创建CAD服务实例
cad_service = CADService()

@cad_bp.route("/cad", methods=["POST"])
@cross_origin()
def generate_cad():
    """
    生成CAD对象的API端点
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 验证请求数据
        validation_result = validate_api_request_data(data)
        if not validation_result["valid"]:
            return jsonify({
                "error": "请求数据验证失败",
                "details": validation_result["errors"]
            }), 400
        
        # 提取参数
        query = data.get("query")
        conversation_id = data.get("conversation_id")
        render_mode = data.get("render_mode", "3d")
        
        print(f"=== API /cad called ===")
        print(f"Query: '{query}'")
        print(f"Conversation ID: {conversation_id}")
        print(f"Render Mode: {render_mode}")
        
        # 调用服务层生成CAD
        result = cad_service.generate_cad(
            query=query,
            conversation_id=conversation_id,
            render_mode=render_mode
        )
        
        # 根据结果返回响应
        if result["success"]:
            return jsonify(result)
        else:
            # 错误情况
            status_code = 500
            if "suggestion" in result and result["suggestion"] == "try_2d_mode":
                status_code = 422  # Unprocessable Entity
            
            return jsonify(result), status_code
            
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({
            "error": "服务器内部错误",
            "message": str(e)
        }), 500

@cad_bp.route("/download/<object_id>", methods=["GET"])
@cross_origin()
def download_cad_file(object_id):
    """
    下载CAD文件的API端点
    """
    try:
        # 获取文件格式参数
        file_format = request.args.get("format", "step")
        
        # 检查是2D还是3D对象
        import os
        svg_file = f"data/generated/{object_id}.svg"
        is_2d = os.path.exists(svg_file)
        
        if is_2d:
            # 2D对象只支持SVG格式
            if file_format != "svg":
                return jsonify({
                    "error": "2D电路图只支持SVG格式下载",
                    "supported_formats": ["svg"],
                    "object_type": "2d"
                }), 400
            
            # 直接返回SVG文件
            return send_file(
                svg_file,
                as_attachment=True,
                download_name=f"{object_id}.svg",
                mimetype="image/svg+xml"
            )
        else:
            # 3D对象支持多种CAD格式
            allowed_3d_formats = ["step", "stl", "obj", "3mf"]
            if file_format not in allowed_3d_formats:
                return jsonify({
                    "error": "3D模型不支持该文件格式",
                    "supported_formats": allowed_3d_formats,
                    "object_type": "3d"
                }), 400
            
            # 获取3D文件路径
            file_path = get_download_path(object_id, file_format)
            
            # 发送文件
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f"{object_id}.{file_format}"
            )
        
    except FileNotFoundError:
        return jsonify({
            "error": "文件不存在",
            "object_id": object_id
        }), 404
    except Exception as e:
        print(f"Download Error: {e}")
        return jsonify({
            "error": "文件下载失败",
            "message": str(e)
        }), 500

@cad_bp.route("/cad/<object_id>/info", methods=["GET"])
@cross_origin()
def get_cad_info(object_id):
    """
    获取CAD对象信息的API端点
    """
    try:
        # 检查生成的代码文件是否存在
        import os
        code_file = f"data/generated/{object_id}.py"
        svg_file = f"data/generated/{object_id}.svg"
        
        if not os.path.exists(code_file):
            return jsonify({
                "error": "CAD对象不存在",
                "object_id": object_id
            }), 404
        
        # 读取代码内容
        with open(code_file, 'r', encoding='utf-8') as f:
            code_content = f.read()
        
        # 检查是否有SVG文件（2D对象）
        has_svg = os.path.exists(svg_file)
        svg_content = None
        if has_svg:
            with open(svg_file, 'r', encoding='utf-8') as f:
                svg_content = f.read()
        
        # 获取文件信息
        from utils import get_file_size
        code_size = get_file_size(code_file)
        svg_size = get_file_size(svg_file) if has_svg else None
        
        # 检测渲染类型和支持的下载格式
        render_mode = "2d" if has_svg else "3d"
        supported_formats = ["svg"] if has_svg else ["step", "stl", "obj", "3mf"]
        
        return jsonify({
            "object_id": object_id,
            "render_mode": render_mode,
            "code": code_content,
            "code_size": code_size,
            "has_svg": has_svg,
            "svg": svg_content,
            "svg_size": svg_size,
            "supported_formats": supported_formats,
            "created_at": object_id  # object_id就是时间戳
        })
        
    except Exception as e:
        print(f"Info Error: {e}")
        return jsonify({
            "error": "获取对象信息失败",
            "message": str(e)
        }), 500 
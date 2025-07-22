"""
Flask应用主入口
整合所有模块，创建并配置Flask应用
"""

from flask import Flask
import json as std_json
from flask.json.provider import JSONProvider
from flask_cors import CORS
from dotenv import load_dotenv

from app.config import AppConfig, init_config
from api import cad_bp, conversation_bp
from utils.json_utils import NumpyEncoder

# 加载环境变量
load_dotenv()

class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return std_json.dumps(obj, **kwargs, cls=NumpyEncoder)

    def loads(self, s, **kwargs):
        return std_json.loads(s, **kwargs)

def create_app():
    """
    创建并配置Flask应用
    
    Returns:
        配置好的Flask应用实例
    """
    # 初始化配置
    init_config()
    
    # 创建Flask应用
    app = Flask(__name__)

    app.json = CustomJSONProvider(app)
    
    # 配置CORS
    cors = CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"
    
    # 注册蓝图
    app.register_blueprint(cad_bp)
    app.register_blueprint(conversation_bp)
    
    # 添加健康检查端点
    @app.route("/health", methods=["GET"])
    def health_check():
        return {
            "status": "healthy",
            "service": "CQAsk Backend",
            "version": "2.0.0"
        }
    
    # 添加根路径端点
    @app.route("/", methods=["GET"])
    def root():
        return {
            "message": "CQAsk Backend API",
            "version": "2.0.0",
            "docs": "/health",
            "endpoints": [
                "/cad - CAD生成API",
                "/conversations - 对话管理API",
                "/download/<id> - 文件下载API"
            ]
        }
    
    return app

def run_app():
    """
    运行Flask应用
    """
    app = create_app()
    app.run(
        host=AppConfig.HOST,
        port=AppConfig.PORT,
        debug=AppConfig.DEBUG
    )

if __name__ == "__main__":
    run_app() 
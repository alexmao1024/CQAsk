#!/usr/bin/env python3
"""
CQAsk Backend 启动脚本
"""

import sys
import os

# 添加当前目录到Python路径，确保可以导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import run_app

if __name__ == "__main__":
    print("🚀 Starting CQAsk Backend...")
    print("📁 Working Directory:", os.getcwd())
    run_app() 
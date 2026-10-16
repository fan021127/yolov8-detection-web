"""
生产环境启动脚本（供公网部署使用）
使用 waitress 作为 WSGI 服务器，比 Flask 内置服务器更稳定
"""
from waitress import serve
from app import app
from config import Config

if __name__ == '__main__':
    print('=' * 60)
    print('  YOLOv8 目标检测系统 - 生产模式启动')
    print('=' * 60)
    serve(app, host='0.0.0.0', port=5000, threads=8)

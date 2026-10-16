import os
from flask import Flask
from config import Config
from routes.auth import auth_bp
from routes.detection import detection_bp
from routes.history import history_bp
from routes.export import export_bp


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # 确保目录存在
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.RESULT_FOLDER, exist_ok=True)

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(export_bp)

    return app


app = create_app()


if __name__ == '__main__':
    print('=' * 60)
    print('  YOLOv8 多类别目标检测 Web 系统')
    print('  访问地址: http://127.0.0.1:5000')
    print('=' * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)












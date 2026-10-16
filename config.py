import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'yolov8-detection-secret-key-2024')

    # 上传与结果目录
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    RESULT_FOLDER = os.path.join(BASE_DIR, 'static', 'results')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB

    # MySQL 数据库
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '123456')
    DB_NAME = os.environ.get('DB_NAME', 'yolov8_detection')

    # YOLOv8
    MODEL_PATH = os.path.join(BASE_DIR, 'weights', 'yolov8n.pt')
    DEFAULT_CONF = 0.25
    DEFAULT_IOU = 0.45

    # 视频处理
    VIDEO_FPS = 20

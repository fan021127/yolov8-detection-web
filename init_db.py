"""
数据库初始化脚本
用法: python init_db.py
功能: 创建数据库、建表、插入默认管理员账号
"""
import pymysql
from config import Config
from models.user import User


def init_database():
    # 1. 连接 MySQL（不指定数据库），创建数据库
    conn = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        charset='utf8mb4',
    )
    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME} "
                        f"DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci")
            print(f'[OK] 数据库 {Config.DB_NAME} 已就绪')
        conn.commit()
    finally:
        conn.close()

    # 2. 连接到指定数据库，建表
    conn = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4',
    )
    try:
        with conn.cursor() as cur:
            # 用户表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            INT AUTO_INCREMENT PRIMARY KEY,
                    username      VARCHAR(64)  NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_username (username)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            print('[OK] users 表已就绪')

            # 检测记录表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS detection_records (
                    id             INT AUTO_INCREMENT PRIMARY KEY,
                    user_id        INT          NOT NULL,
                    file_name      VARCHAR(255) NOT NULL,
                    file_type      VARCHAR(16)  NOT NULL,
                    file_path      VARCHAR(512) NOT NULL,
                    result_path    VARCHAR(512),
                    conf_threshold FLOAT        NOT NULL DEFAULT 0.25,
                    detection_json JSON,
                    total_objects  INT          NOT NULL DEFAULT 0,
                    remark         VARCHAR(500),
                    status         VARCHAR(16)  NOT NULL DEFAULT 'completed',
                    created_at     DATETIME     DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_user_id (user_id),
                    INDEX idx_created_at (created_at),
                    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            print('[OK] detection_records 表已就绪')
        conn.commit()
    finally:
        conn.close()

    # 3. 创建默认管理员账号
    if not User.get_by_username('admin'):
        User.create('admin', 'admin123')
        print('[OK] 默认管理员已创建: admin / admin123')
    else:
        print('[INFO] 管理员 admin 已存在，跳过创建')

    print('\n' + '=' * 50)
    print('  数据库初始化完成！')
    print('  默认账号: admin / admin123')
    print('=' * 50)


if __name__ == '__main__':
    init_database()

import pymysql
from pymysql.cursors import DictCursor
from config import Config
def get_connection():
    """获取 MySQL 数据库连接"""
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4',
        cursorclass=DictCursor,
        autocommit=False,
    )
def execute_query(sql, params=None, fetch_one=False):
    """执行查询语句，返回结果列表或单条"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            if fetch_one:
                return cur.fetchone()
            return cur.fetchall()
    finally:
        conn.close()
def execute_update(sql, params=None):
    """执行插入/更新/删除，返回受影响行数和自增ID"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            last_id = cur.lastrowid
            conn.commit()
            return cur.rowcount, last_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

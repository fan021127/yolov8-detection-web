from werkzeug.security import generate_password_hash, check_password_hash
from models.database import execute_query, execute_update


class User:
    @staticmethod
    def create(username, password):
        """创建新用户"""
        password_hash = generate_password_hash(password)
        sql = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
        _, user_id = execute_update(sql, (username, password_hash))
        return user_id

    @staticmethod
    def get_by_username(username):
        """根据用户名查询用户"""
        sql = "SELECT * FROM users WHERE username = %s"
        return execute_query(sql, (username,), fetch_one=True)

    @staticmethod
    def get_by_id(user_id):
        """根据ID查询用户"""
        sql = "SELECT * FROM users WHERE id = %s"
        return execute_query(sql, (user_id,), fetch_one=True)

    @staticmethod
    def verify_password(user, password):
        """校验密码"""
        return check_password_hash(user['password_hash'], password)

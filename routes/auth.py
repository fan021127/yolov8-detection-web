from flask import Blueprint, request, session, jsonify, render_template
from models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """首页：已登录跳检测页，未登录跳登录页"""
    if 'user_id' in session:
        return render_template('index.html', username=session.get('username'))
    return render_template('login.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录"""
    if request.method == 'GET':
        return render_template('login.html')

    data = request.get_json() if request.is_json else request.form
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400

    user = User.get_by_username(username)
    if not user or not User.verify_password(user, password):
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

    session['user_id'] = user['id']
    session['username'] = user['username']
    return jsonify({'success': True, 'message': '登录成功', 'username': user['username']})


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """注册"""
    if request.method == 'GET':
        return render_template('login.html')

    data = request.get_json() if request.is_json else request.form
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    confirm = data.get('confirm_password') or ''

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    if len(username) < 3:
        return jsonify({'success': False, 'message': '用户名至少3个字符'}), 400
    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少6个字符'}), 400
    if password != confirm:
        return jsonify({'success': False, 'message': '两次密码不一致'}), 400

    if User.get_by_username(username):
        return jsonify({'success': False, 'message': '用户名已存在'}), 409

    User.create(username, password)
    return jsonify({'success': True, 'message': '注册成功，请登录'})


@auth_bp.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    return jsonify({'success': True})


@auth_bp.route('/api/user')
def current_user():
    """获取当前登录用户信息"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    return jsonify({'success': True, 'user_id': session['user_id'], 'username': session['username']})

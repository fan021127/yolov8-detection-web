from flask import Blueprint, request, session, jsonify, render_template
from models.detection_record import DetectionRecord

history_bp = Blueprint('history', __name__)


def _login_required():
    if 'user_id' not in session:
        return None, (jsonify({'success': False, 'message': '未登录'}), 401)
    return session['user_id'], None


@history_bp.route('/history')
def history_page():
    """历史记录页面"""
    if 'user_id' not in session:
        return render_template('login.html')
    return render_template('history.html', username=session.get('username'))


@history_bp.route('/api/history')
def list_history():
    """分页查询历史记录"""
    user_id, err = _login_required()
    if err:
        return err

    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))

    records = DetectionRecord.list_by_user(user_id, page, page_size)
    total = DetectionRecord.count_by_user(user_id)

    # 序列化日期
    for r in records:
        if r.get('created_at'):
            r['created_at'] = r['created_at'].strftime('%Y-%m-%d %H:%M:%S')

    return jsonify({
        'success': True,
        'records': records,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': (total + page_size - 1) // page_size,
        },
    })


@history_bp.route('/api/history/<int:record_id>')
def get_record(record_id):
    """查询单条记录详情"""
    user_id, err = _login_required()
    if err:
        return err

    record = DetectionRecord.get_by_id(record_id)
    if not record or record['user_id'] != user_id:
        return jsonify({'success': False, 'message': '记录不存在'}), 404

    if record.get('created_at'):
        record['created_at'] = record['created_at'].strftime('%Y-%m-%d %H:%M:%S')

    return jsonify({'success': True, 'record': record})


@history_bp.route('/api/history/<int:record_id>/remark', methods=['PUT'])
def update_remark(record_id):
    """更新备注"""
    user_id, err = _login_required()
    if err:
        return err

    data = request.get_json()
    remark = (data.get('remark') or '').strip()
    if len(remark) > 500:
        return jsonify({'success': False, 'message': '备注不能超过500字'}), 400

    ok = DetectionRecord.update_remark(record_id, user_id, remark)
    if not ok:
        return jsonify({'success': False, 'message': '记录不存在或更新失败'}), 404
    return jsonify({'success': True, 'message': '备注已更新'})


@history_bp.route('/api/history/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """删除记录"""
    user_id, err = _login_required()
    if err:
        return err

    ok = DetectionRecord.delete(record_id, user_id)
    if not ok:
        return jsonify({'success': False, 'message': '记录不存在或删除失败'}), 404
    return jsonify({'success': True, 'message': '已删除'})

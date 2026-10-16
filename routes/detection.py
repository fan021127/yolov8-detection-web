import os
import uuid
import cv2
from flask import Blueprint, request, session, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from config import Config
from services.detector import detect_image
from services.video_processor import process_video_async, get_task_progress
from models.detection_record import DetectionRecord

detection_bp = Blueprint('detection', __name__)


def _login_required():
    """检查登录状态，返回 (user_id, error_response)"""
    if 'user_id' not in session:
        return None, (jsonify({'success': False, 'message': '未登录'}), 401)
    return session['user_id'], None


def _save_upload(file_storage):
    """保存上传文件，返回 (保存路径, 安全文件名, 原始文件名)"""
    original_name = file_storage.filename or 'upload'
    safe_name = secure_filename(original_name)
    ext = os.path.splitext(safe_name)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(Config.UPLOAD_FOLDER, unique_name)
    file_storage.save(save_path)
    return save_path, unique_name, original_name


@detection_bp.route('/detect')
def detect_page():
    """检测页面"""
    if 'user_id' not in session:
        return render_template('login.html')
    return render_template('index.html', username=session.get('username'))


@detection_bp.route('/api/detect/image', methods=['POST'])
def detect_image_upload():
    """图片检测接口"""
    user_id, err = _login_required()
    if err:
        return err

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '未上传文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '文件名为空'}), 400

    conf_threshold = float(request.form.get('conf_threshold', Config.DEFAULT_CONF))

    try:
        save_path, unique_name, original_name = _save_upload(file)

        # 执行检测
        annotated_img, det_result = detect_image(save_path, conf_threshold=conf_threshold)

        # 保存结果图片
        result_name = f"result_{uuid.uuid4().hex}.jpg"
        result_path = os.path.join(Config.RESULT_FOLDER, result_name)
        cv2.imwrite(result_path, annotated_img)

        # 存入数据库
        record_id = DetectionRecord.create(
            user_id=user_id,
            file_name=original_name,
            file_type='image',
            file_path=f"uploads/{unique_name}",
            result_path=f"results/{result_name}",
            conf_threshold=conf_threshold,
            detection_json=det_result,
            total_objects=det_result['total_objects'],
            status='completed',
        )

        return jsonify({
            'success': True,
            'record_id': record_id,
            'result_url': f"/static/results/{result_name}",
            'original_url': f"/static/uploads/{unique_name}",
            'detection': det_result,
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'检测失败: {str(e)}'}), 500


@detection_bp.route('/api/detect/video', methods=['POST'])
def detect_video_upload():
    """视频检测接口（异步，返回task_id）"""
    user_id, err = _login_required()
    if err:
        return err

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '未上传文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '文件名为空'}), 400

    conf_threshold = float(request.form.get('conf_threshold', Config.DEFAULT_CONF))

    try:
        save_path, unique_name, original_name = _save_upload(file)
        task_id = uuid.uuid4().hex
        result_name = f"result_{task_id}.mp4"
        result_path = os.path.join(Config.RESULT_FOLDER, result_name)

        # 先创建pending记录
        record_id = DetectionRecord.create(
            user_id=user_id,
            file_name=original_name,
            file_type='video',
            file_path=f"uploads/{unique_name}",
            result_path=f"results/{result_name}",
            conf_threshold=conf_threshold,
            detection_json={'detections': [], 'class_counts': {}, 'total_objects': 0},
            total_objects=0,
            status='processing',
        )

        # 启动异步视频处理
        process_video_async(task_id, save_path, result_path, conf_threshold)

        return jsonify({
            'success': True,
            'task_id': task_id,
            'record_id': record_id,
            'message': '视频处理已开始',
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'上传失败: {str(e)}'}), 500


@detection_bp.route('/api/video/progress/<task_id>')
def video_progress(task_id):
    """查询视频处理进度"""
    task = get_task_progress(task_id)
    return jsonify({'success': True, 'task': task})


@detection_bp.route('/api/video/complete/<task_id>/<int:record_id>', methods=['POST'])
def video_complete(task_id, record_id):
    """视频处理完成后更新数据库记录"""
    user_id, err = _login_required()
    if err:
        return err

    task = get_task_progress(task_id)
    if task.get('status') != 'done':
        return jsonify({'success': False, 'message': '视频尚未处理完成'}), 400

    # 更新记录状态和检测结果
    from models.database import execute_update
    import json
    class_counts = task.get('class_counts', {})
    total = sum(class_counts.values())
    det_json = json.dumps({'detections': [], 'class_counts': class_counts, 'total_objects': total}, ensure_ascii=False)
    execute_update(
        "UPDATE detection_records SET status='completed', detection_json=%s, total_objects=%s WHERE id=%s AND user_id=%s",
        (det_json, total, record_id, user_id)
    )

    result_name = os.path.basename(task.get('result_path', ''))
    return jsonify({
        'success': True,
        'result_url': f"/static/results/{result_name}",
        'class_counts': class_counts,
        'total_objects': total,
    })


@detection_bp.route('/api/download/<path:filename>')
def download_result(filename):
    """下载检测结果文件"""
    return send_from_directory(Config.RESULT_FOLDER, filename, as_attachment=True)

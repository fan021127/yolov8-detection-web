from flask import Blueprint, session, jsonify, send_file
from io import BytesIO
from models.detection_record import DetectionRecord
from services.exporter import export_records_to_excel

export_bp = Blueprint('export', __name__)


@export_bp.route('/api/export/excel')
def export_excel():
    """导出当前用户全部检测记录为 Excel"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401

    user_id = session['user_id']
    records = DetectionRecord.list_all_for_export(user_id)

    if not records:
        return jsonify({'success': False, 'message': '暂无检测记录可导出'}), 400

    excel_bytes = export_records_to_excel(records)
    return send_file(
        BytesIO(excel_bytes),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='检测记录导出.xlsx',
    )

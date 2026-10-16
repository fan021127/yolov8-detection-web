import json
from models.database import execute_query, execute_update


class DetectionRecord:
    @staticmethod
    def create(user_id, file_name, file_type, file_path, result_path,
               conf_threshold, detection_json, total_objects, status='completed'):
        """创建检测记录"""
        sql = """INSERT INTO detection_records
                 (user_id, file_name, file_type, file_path, result_path,
                  conf_threshold, detection_json, total_objects, status)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        det_json = json.dumps(detection_json, ensure_ascii=False) if detection_json else None
        _, record_id = execute_update(sql, (
            user_id, file_name, file_type, file_path, result_path,
            conf_threshold, det_json, total_objects, status
        ))
        return record_id

    @staticmethod
    def get_by_id(record_id):
        """根据ID查询记录"""
        sql = "SELECT * FROM detection_records WHERE id = %s"
        row = execute_query(sql, (record_id,), fetch_one=True)
        if row and row.get('detection_json'):
            row['detection_json'] = json.loads(row['detection_json'])
        return row

    @staticmethod
    def list_by_user(user_id, page=1, page_size=10):
        """分页查询用户的检测记录"""
        offset = (page - 1) * page_size
        sql = """SELECT id, file_name, file_type, total_objects, conf_threshold,
                        remark, status, created_at
                 FROM detection_records
                 WHERE user_id = %s
                 ORDER BY created_at DESC
                 LIMIT %s OFFSET %s"""
        records = execute_query(sql, (user_id, page_size, offset))
        return records

    @staticmethod
    def count_by_user(user_id):
        """统计用户记录总数"""
        sql = "SELECT COUNT(*) AS cnt FROM detection_records WHERE user_id = %s"
        result = execute_query(sql, (user_id,), fetch_one=True)
        return result['cnt'] if result else 0

    @staticmethod
    def update_remark(record_id, user_id, remark):
        """更新备注"""
        sql = "UPDATE detection_records SET remark = %s WHERE id = %s AND user_id = %s"
        rowcount, _ = execute_update(sql, (remark, record_id, user_id))
        return rowcount > 0

    @staticmethod
    def delete(record_id, user_id):
        """删除记录"""
        sql = "DELETE FROM detection_records WHERE id = %s AND user_id = %s"
        rowcount, _ = execute_update(sql, (record_id, user_id))
        return rowcount > 0

    @staticmethod
    def list_all_for_export(user_id):
        """查询用户全部记录用于导出"""
        sql = """SELECT id, file_name, file_type, total_objects, conf_threshold,
                        detection_json, remark, status, created_at
                 FROM detection_records
                 WHERE user_id = %s
                 ORDER BY created_at DESC"""
        records = execute_query(sql, (user_id,))
        for r in records:
            if r.get('detection_json'):
                r['detection_json'] = json.loads(r['detection_json'])
        return records

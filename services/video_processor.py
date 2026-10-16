import os
import cv2
import threading
from services.detector import get_model, detect_frame
from config import Config

# 视频处理进度存储: {task_id: {'progress': 0-100, 'status': 'processing'/'done'/'failed', 'result_path': ...}}
video_tasks = {}
_task_lock = threading.Lock()


def get_task_progress(task_id):
    """获取视频处理进度"""
    with _task_lock:
        return video_tasks.get(task_id, {'progress': 0, 'status': 'not_found'})


def process_video_async(task_id, input_path, output_path, conf_threshold=0.25):
    """异步处理视频：逐帧检测并写入输出视频"""
    def _run():
        try:
            model = get_model()
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise RuntimeError('无法打开视频文件')

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or Config.VIDEO_FPS
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            frame_idx = 0
            all_class_counts = {}

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                annotated, counts = detect_frame(frame, model, conf_threshold)
                out.write(annotated)

                for k, v in counts.items():
                    all_class_counts[k] = all_class_counts.get(k, 0) + v

                frame_idx += 1
                if total_frames > 0:
                    progress = int(frame_idx / total_frames * 100)
                else:
                    progress = min(frame_idx, 100)

                with _task_lock:
                    video_tasks[task_id]['progress'] = progress
                    video_tasks[task_id]['class_counts'] = all_class_counts

            cap.release()
            out.release()

            with _task_lock:
                video_tasks[task_id]['status'] = 'done'
                video_tasks[task_id]['progress'] = 100
                video_tasks[task_id]['result_path'] = output_path
        except Exception as e:
            with _task_lock:
                video_tasks[task_id]['status'] = 'failed'
                video_tasks[task_id]['error'] = str(e)

    thread = threading.Thread(target=_run, daemon=True)
    with _task_lock:
        video_tasks[task_id] = {'progress': 0, 'status': 'processing', 'class_counts': {}}
    thread.start()
    return task_id

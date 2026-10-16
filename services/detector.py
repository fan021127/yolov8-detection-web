import os
import cv2
import numpy as np
from ultralytics import YOLO
from config import Config

# 全局模型实例（懒加载，避免每次请求重新加载）
_model = None


def get_model():
    """获取 YOLOv8 模型单例"""
    global _model
    if _model is None:
        if not os.path.exists(Config.MODEL_PATH):
            # 自动下载权重
            _model = YOLO('yolov8n.pt')
            os.makedirs(os.path.dirname(Config.MODEL_PATH), exist_ok=True)
            try:
                _model.save(Config.MODEL_PATH)
            except Exception:
                pass
        else:
            _model = YOLO(Config.MODEL_PATH)
    return _model


# COCO 80 类中文名称映射
COCO_NAMES_CN = {
    0: '人', 1: '自行车', 2: '汽车', 3: '摩托车', 4: '飞机',
    5: '公交车', 6: '火车', 7: '卡车', 8: '船', 9: '红绿灯',
    10: '消防栓', 11: '停车标志', 12: '停车计时器', 13: '长椅', 14: '鸟',
    15: '猫', 16: '狗', 17: '马', 18: '羊', 19: '牛',
    20: '大象', 21: '熊', 22: '斑马', 23: '长颈鹿', 24: '背包',
    25: '雨伞', 26: '手提包', 27: '领带', 28: '行李箱', 29: '飞盘',
    30: '滑雪板', 31: '单板滑雪', 32: '运动球', 33: '风筝', 34: '棒球棒',
    35: '棒球手套', 36: '滑板', 37: '冲浪板', 38: '网球拍', 39: '瓶子',
    40: '酒杯', 41: '杯子', 42: '叉子', 43: '刀', 44: '勺子',
    45: '碗', 46: '香蕉', 47: '苹果', 48: '三明治', 49: '橙子',
    50: '西兰花', 51: '胡萝卜', 52: '热狗', 53: '披萨', 54: '甜甜圈',
    55: '蛋糕', 56: '椅子', 57: '沙发', 58: '盆栽', 59: '床',
    60: '餐桌', 61: '马桶', 62: '电视', 63: '笔记本电脑', 64: '鼠标',
    65: '遥控器', 66: '键盘', 67: '手机', 68: '微波炉', 69: '烤箱',
    70: '烤面包机', 71: '水槽', 72: '冰箱', 73: '书', 74: '时钟',
    75: '花瓶', 76: '剪刀', 77: '泰迪熊', 78: '吹风机', 79: '牙刷',
}

# 为每个类别分配固定颜色（BGR）
np.random.seed(42)
CLASS_COLORS = {i: tuple(int(c) for c in np.random.randint(0, 255, 3)) for i in range(80)}


def detect_image(image_path, conf_threshold=0.25, iou_threshold=0.45):
    """
    对单张图片执行目标检测
    返回: (annotated_image_bgr, detection_result_dict)
    """
    model = get_model()
    results = model.predict(source=image_path, conf=conf_threshold, iou=iou_threshold, verbose=False)
    result = results[0]

    img = result.orig_img.copy()
    detections = []
    class_counts = {}

    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
        cls_name = COCO_NAMES_CN.get(cls_id, model.names[cls_id])

        detections.append({
            'class_id': cls_id,
            'class_name': cls_name,
            'confidence': round(conf, 4),
            'bbox': [x1, y1, x2, y2],
        })
        class_counts[cls_name] = class_counts.get(cls_name, 0) + 1

        # 绘制检测框
        color = CLASS_COLORS.get(cls_id, (0, 255, 0))
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        label = f'{cls_name} {conf:.2f}'
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
        cv2.putText(img, label, (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    detection_result = {
        'detections': detections,
        'class_counts': class_counts,
        'total_objects': len(detections),
    }
    return img, detection_result


def detect_frame(frame, model, conf_threshold=0.25, iou_threshold=0.45):
    """
    对视频单帧执行检测（用于视频处理循环）
    返回: (annotated_frame, class_counts_dict)
    """
    results = model.predict(source=frame, conf=conf_threshold, iou=iou_threshold, verbose=False)
    result = results[0]
    annotated = result.orig_img.copy()
    class_counts = {}

    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
        cls_name = COCO_NAMES_CN.get(cls_id, model.names[cls_id])
        class_counts[cls_name] = class_counts.get(cls_name, 0) + 1

        color = CLASS_COLORS.get(cls_id, (0, 255, 0))
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        label = f'{cls_name} {conf:.2f}'
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(annotated, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
        cv2.putText(annotated, label, (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    return annotated, class_counts

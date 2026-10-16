-- ============================================================
-- YOLOv8 多类别目标检测 Web 系统 数据库建表脚本
-- ============================================================

CREATE DATABASE IF NOT EXISTS yolov8_detection
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE yolov8_detection;

-- ------------------------------------------------------------
-- 用户表
-- ------------------------------------------------------------
DROP TABLE IF EXISTS detection_records;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(64)  NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL        COMMENT '密码哈希',
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ------------------------------------------------------------
-- 检测记录表
-- ------------------------------------------------------------
CREATE TABLE detection_records (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT          NOT NULL COMMENT '所属用户',
    file_name     VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_type     VARCHAR(16)  NOT NULL COMMENT 'image / video',
    file_path     VARCHAR(512) NOT NULL COMMENT '上传文件相对路径',
    result_path   VARCHAR(512)          COMMENT '结果文件相对路径',
    conf_threshold FLOAT       NOT NULL DEFAULT 0.25 COMMENT '置信度阈值',
    detection_json JSON                 COMMENT '检测结果JSON（类别、数量、框坐标）',
    total_objects INT          NOT NULL DEFAULT 0    COMMENT '检测到的物体总数',
    remark        VARCHAR(500)          COMMENT '用户备注',
    status        VARCHAR(16)  NOT NULL DEFAULT 'completed' COMMENT 'pending/processing/completed/failed',
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='检测记录表';

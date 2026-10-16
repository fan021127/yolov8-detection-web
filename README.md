# YOLOv8 多类别目标检测 Web 系统

基于 Flask + YOLOv8 + MySQL + 原生 HTML/CSS/JS 的图像/视频多类别目标检测 Web 平台。

## 功能特性

- 👤 **用户系统**：注册/登录，不同用户数据隔离
- 🖼️ **图片检测**：上传图片，YOLOv8 自动框出物体
- 🎬 **视频检测**：上传视频，逐帧检测，实时进度条
- 🎚️ **置信度调节**：滑块调节置信阈值，过滤低置信结果
- 📊 **统计图表**：自动统计各类物体数量，ECharts 饼图可视化
- 💾 **历史记录**：所有检测结果存入 MySQL，支持分页浏览
- ✏️ **备注功能**：为每条检测记录添加文字备注
- 📥 **结果下载**：下载带检测框的图片/视频
- 📤 **Excel 导出**：一键导出全部检测记录为 Excel 报告

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Flask 3.0 |
| 模型 | YOLOv8 (ultralytics) |
| 前端 | HTML5 + CSS3 + 原生 JavaScript + ECharts |
| 数据库 | MySQL 5.7+ / 8.0 |
| 图像处理 | OpenCV + Pillow |
| Excel导出 | openpyxl |

## 项目结构

```
yolov8-detection-web/
├── app.py                  # Flask 主入口
├── config.py               # 配置文件
├── init_db.py              # 数据库初始化脚本
├── schema.sql              # 数据库建表语句
├── requirements.txt        # Python 依赖
├── README.md               # 说明文档
├── models/                 # 数据模型层
│   ├── database.py         # 数据库连接与操作
│   ├── user.py             # 用户模型
│   └── detection_record.py # 检测记录模型
├── services/               # 业务服务层
│   ├── detector.py         # YOLOv8 检测引擎
│   ├── video_processor.py  # 视频异步处理
│   └── exporter.py         # Excel 导出
├── routes/                 # 路由层
│   ├── auth.py             # 登录/注册路由
│   ├── detection.py        # 检测接口路由
│   ├── history.py          # 历史记录路由
│   └── export.py           # 导出路由
├── templates/              # HTML 模板
│   ├── login.html          # 登录/注册页
│   ├── index.html          # 检测主页
│   └── history.html        # 历史记录页
├── static/                 # 静态资源
│   ├── css/                # 样式文件
│   ├── js/                 # 脚本文件
│   ├── uploads/            # 上传文件存储
│   └── results/            # 检测结果存储
└── weights/                # YOLOv8 模型权重
```

## 环境要求

- Python 3.9 ~ 3.11
- MySQL 5.7+ 或 8.0
- 内存建议 4GB 以上（YOLOv8n 模型约 6MB，推理占用较低）

## 快速开始

### 1. 安装 Python 依赖

```bash
cd yolov8-detection-web
pip install -r requirements.txt
```

> 首次运行会自动下载 `yolov8n.pt` 权重文件（约 6MB），也可手动放入 `weights/` 目录。

### 2. 配置 MySQL

确保 MySQL 服务已启动，然后修改 `config.py` 中的数据库连接信息：

```python
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = '你的密码'
DB_NAME = 'yolov8_detection'
```

### 3. 初始化数据库

```bash
python init_db.py
```

该脚本会自动创建数据库、建表，并创建默认管理员账号：
- 用户名：`admin`
- 密码：`admin123`

### 4. 启动系统

```bash
python app.py
```

启动后访问：**http://127.0.0.1:5000**

## API 接口一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/login` | 用户登录 |
| GET/POST | `/register` | 用户注册 |
| GET | `/logout` | 退出登录 |
| POST | `/api/detect/image` | 图片检测 |
| POST | `/api/detect/video` | 视频检测（异步） |
| GET | `/api/video/progress/<task_id>` | 查询视频处理进度 |
| POST | `/api/video/complete/<task_id>/<record_id>` | 视频处理完成回调 |
| GET | `/api/history` | 分页查询历史记录 |
| GET | `/api/history/<id>` | 查询单条记录详情 |
| PUT | `/api/history/<id>/remark` | 更新备注 |
| DELETE | `/api/history/<id>` | 删除记录 |
| GET | `/api/export/excel` | 导出 Excel 报告 |
| GET | `/api/download/<filename>` | 下载检测结果文件 |

## 支持检测的类别

系统基于 YOLOv8 COCO 预训练模型，支持 80 类常见物体检测，包括：

- **人物/交通**：人、自行车、汽车、摩托车、飞机、公交车、火车、卡车、船
- **日常用品**：瓶子、酒杯、杯子、叉子、刀、勺子、碗、书、时钟、剪刀
- **电子设备**：电视、笔记本电脑、鼠标、遥控器、键盘、手机、微波炉、烤箱、冰箱
- **家具**：椅子、沙发、盆栽、床、餐桌、马桶
- **食物**：香蕉、苹果、三明治、橙子、西兰花、胡萝卜、热狗、披萨、甜甜圈、蛋糕
- **动物**：鸟、猫、狗、马、羊、牛、大象、熊、斑马、长颈鹿
- **运动器材**：飞盘、滑雪板、运动球、风筝、棒球棒、滑板、冲浪板、网球拍
- **其他**：红绿灯、消防栓、停车标志、长椅、背包、雨伞、手提包、领带、行李箱、花瓶、泰迪熊、吹风机、牙刷等

## 常见问题

**Q: 首次运行报错找不到模型权重？**
A: 系统会自动下载 `yolov8n.pt`，如网络问题可手动从 [Ultralytics 官方](https://github.com/ultralytics/ultralytics) 下载后放入 `weights/` 目录。

**Q: 视频检测很慢？**
A: 视频检测是逐帧推理，速度取决于视频长度和硬件。可使用 `yolov8n.pt`（nano版）获得最快速度，或换用 `yolov8s.pt`/`yolov8m.pt` 提升精度。

**Q: 如何更换更大的 YOLOv8 模型？**
A: 修改 `config.py` 中的 `MODEL_PATH` 为对应权重路径（如 `yolov8s.pt`），首次运行会自动下载。

**Q: MySQL 连接失败？**
A: 检查 MySQL 服务是否启动，确认 `config.py` 中的用户名密码正确，且用户有创建数据库的权限。

## License

MIT

@echo off
chcp 65001 >nul
echo ========================================
echo   YOLOv8 目标检测系统 - 启动脚本
echo ========================================
echo.

echo [1/3] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

echo.
echo [2/3] 检查依赖...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包，请稍候...
    pip install -r requirements.txt
) else (
    echo 依赖已安装
)

echo.
echo [3/3] 启动系统...
echo.
echo 系统启动后请访问: http://127.0.0.1:5000
echo 默认账号: admin / admin123
echo 按 Ctrl+C 可停止服务
echo.

python app.py
pause

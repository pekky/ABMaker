@echo off
chcp 65001 >nul
REM PDF小说转有声读物 - Web界面启动脚本 (Windows)

echo ======================================
echo PDF小说转有声读物工具
echo ======================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    echo 请先安装 Python 3.8 或更高版本
    pause
    exit /b 1
)

echo Python版本:
python --version
echo.

REM 检查依赖是否安装
echo 检查依赖...
python -c "import gradio" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

echo ✓ 依赖检查完成
echo.

REM 启动Web界面
echo 正在启动Web界面...
echo 请稍候，首次运行需要下载模型文件...
echo.

python app.py
pause



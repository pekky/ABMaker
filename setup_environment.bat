@echo off
REM ABMaker 环境准备脚本 (Windows版本)
REM 自动安装 miniconda，创建和配置 abmaker310 环境

echo 🚀 ABMaker 环境准备脚本
echo ============================================================

REM 检查 conda 是否已安装
where conda >nul 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] conda 已安装
    goto :check_env
) else (
    echo [WARNING] conda 未安装，开始安装 miniconda...
    goto :install_conda
)

:install_conda
echo [INFO] 正在下载 miniconda...
REM 创建临时目录
set TEMP_DIR=%TEMP%\miniconda_install
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"
cd /d "%TEMP_DIR%"

REM 下载 miniconda 安装包
set MINICONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
set MINICONDA_INSTALLER=Miniconda3-latest-Windows-x86_64.exe

powershell -Command "Invoke-WebRequest -Uri '%MINICONDA_URL%' -OutFile '%MINICONDA_INSTALLER%'"
if %errorlevel% neq 0 (
    echo [ERROR] 下载 miniconda 失败
    exit /b 1
)

echo [INFO] 正在安装 miniconda...
REM 静默安装 miniconda
"%MINICONDA_INSTALLER%" /InstallationType=JustMe /RegisterPython=1 /S /D=%USERPROFILE%\miniconda3

REM 清理临时文件
cd /d "%USERPROFILE%"
rmdir /s /q "%TEMP_DIR%"

echo [SUCCESS] miniconda 安装完成

REM 重新加载环境变量
call "%USERPROFILE%\miniconda3\Scripts\activate.bat"

:check_env
REM 检查 abmaker310 环境是否存在
conda env list | findstr "abmaker310" >nul
if %errorlevel% equ 0 (
    echo [SUCCESS] abmaker310 环境已存在
) else (
    echo [WARNING] abmaker310 环境不存在，开始创建...
    echo [INFO] 正在创建 abmaker310 环境...
    conda create -n abmaker310 python=3.10 -y
    echo [SUCCESS] abmaker310 环境创建完成
)

REM 激活环境
echo [INFO] 正在激活 abmaker310 环境...
call conda activate abmaker310

REM 检查 requirements.txt 是否存在
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt 文件不存在
    exit /b 1
)

echo [INFO] 正在安装依赖包...
REM 升级 pip
python -m pip install --upgrade pip

REM 安装依赖
pip install -r requirements.txt

echo [SUCCESS] 依赖包安装完成

REM 验证环境
echo [INFO] 正在验证环境...
python --version
python -c "import torch; print('PyTorch 版本:', torch.__version__)" 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] PyTorch 已安装
) else (
    echo [WARNING] PyTorch 未安装或有问题
)

python -c "import bark; print('Bark 已安装')" 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Bark 已安装
) else (
    echo [WARNING] Bark 未安装或有问题
)

echo.
echo ============================================================
echo [SUCCESS] 🎉 环境准备完成！
echo.
echo [INFO] 使用方法：
echo   conda activate abmaker310
echo.
echo [INFO] 运行 ABMaker：
echo   conda activate abmaker310 ^&^& python optimized_audiobook_maker.py docs/RiverTown.pdf --batch-mode
echo.
echo [INFO] 或者使用批量处理模式：
echo   conda activate abmaker310 ^&^& python optimized_audiobook_maker.py docs/RiverTown.pdf --batch-mode --batch-size 15000
echo.
echo ============================================================

pause




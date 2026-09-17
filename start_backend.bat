@echo off
chcp 65001 >nul
cd /d %~dp0backend
echo.
echo ================================
echo   Family App - Backend 启动
echo ================================
echo.
call d:\family_app\venv\Scripts\activate.bat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
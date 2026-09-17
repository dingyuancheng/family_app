@echo off
chcp 65001 >nul
cd /d %~dp0mobile_app
echo.
echo ================================
echo   Family App - Frontend 启动
echo ================================
echo.
npm run dev
pause
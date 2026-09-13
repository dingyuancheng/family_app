@echo off
chcp 65001 >nul
echo ============================================
echo   构建前端 + 同步到 Android 工程
echo ============================================
echo.

cd /d "%~dp0"

echo [1/2] 构建前端...
call npm run build
if errorlevel 1 (
    echo.
    echo [错误] 前端构建失败！
    pause
    exit /b 1
)
echo.

echo [2/2] 同步到 Android 工程...
call npx cap sync
if errorlevel 1 (
    echo.
    echo [错误] Capacitor 同步失败！
    pause
    exit /b 1
)

echo.
echo ============================================
echo   完成！可以去 Android Studio 打包 APK 了
echo ============================================
pause
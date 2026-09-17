@echo off
chcp 65001 >nul
echo ============================================
echo   清理 Android 构建缓存
echo ============================================
echo.

cd /d "%~dp0"

if exist "android\.gradle" (
    rmdir /s /q "android\.gradle"
    echo   - 已删除 android\.gradle
) else (
    echo   - 跳过 android\.gradle （不存在）
)
if exist "android\build" (
    rmdir /s /q "android\build"
    echo   - 已删除 android\build
) else (
    echo   - 跳过 android\build （不存在）
)
if exist "android\app\build" (
    rmdir /s /q "android\app\build"
    echo   - 已删除 android\app\build
) else (
    echo   - 跳过 android\app\build （不存在）
)
if exist "android\capacitor-cordova-android-plugins\build" (
    rmdir /s /q "android\capacitor-cordova-android-plugins\build"
    echo   - 已删除 android\capacitor-cordova-android-plugins\build
) else (
    echo   - 跳过 android\capacitor-cordova-android-plugins\build （不存在）
)

echo.
echo ============================================
echo   清理完成！
echo ============================================
pause
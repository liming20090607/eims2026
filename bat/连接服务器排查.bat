@echo off
chcp 65001 >nul
title 连接服务器排查问题
echo ========================================
echo   服务器问题排查 - SSH 连接
echo ========================================
echo.
echo 服务器信息:
echo   IP: 39.106.41.239
echo   用户：admin
echo.
echo 说明:
echo   端口 22 是 SSH 端口，用于远程登录
echo   Web 服务应该使用端口 8000
echo.
echo ========================================
echo.
pause
echo.
echo 正在连接服务器...
ssh admin@39.106.41.239

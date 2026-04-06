@echo off
chcp 65001 >nul
title EIMS 服务器 - SSH 登录
echo ========================================
echo   EIMS 服务器 SSH 登录
echo ========================================
echo.
echo 服务器：39.106.41.239
echo 用户名：root
echo.
echo ========================================
echo.
echo 正在连接服务器...
echo.
ssh root@39.106.41.239

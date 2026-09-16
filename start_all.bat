@echo off
title FinResolve Predict Launcher
echo ============================================================
echo  Starting FinResolve Predict (Backend + Frontend)
echo ============================================================

start "FinResolve Backend" cmd /c "%~dp0run_backend.bat"
timeout /t 3 /nobreak >nul
start "FinResolve Frontend" cmd /c "%~dp0run_frontend.bat"

echo.
echo Both services are launching:
echo   - Backend:  http://127.0.0.1:8000
echo   - Frontend: http://127.0.0.1:5173
echo.
echo Opening browser in 2 seconds...
timeout /t 2 /nobreak >nul
start http://127.0.0.1:5173
exit

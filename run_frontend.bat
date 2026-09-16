@echo off
title FinResolve Predict - Frontend Dashboard (Port 5173)
cd /d "%~dp0\frontend"
echo ============================================================
echo  FinResolve Predict - React Frontend Dashboard
echo  Starting Vite on http://127.0.0.1:5173
echo ============================================================
call npm run dev
pause

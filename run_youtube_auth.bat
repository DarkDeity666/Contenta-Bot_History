@echo off
title Link YouTube Channel
echo =======================================================
echo     CONTENTA HISTORY BOT - YOUTUBE CHANNEL LINK
echo =======================================================
echo.
echo Opening Google sign-in window in your browser...
echo.
.\venv\Scripts\python.exe authenticate_youtube.py
echo.
echo Press any key to close this window.
pause >nul

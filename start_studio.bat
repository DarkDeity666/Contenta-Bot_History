@echo off
title Contenta History Bot Studio
echo =======================================================
echo        CONTENTA 2.5D HISTORY BOT STUDIO
echo =======================================================
echo.
echo Starting Studio Server on isolated port http://localhost:54880 ...
echo Opening your web browser...
start http://localhost:54880
echo.
.\venv\Scripts\python.exe server.py 54880
pause

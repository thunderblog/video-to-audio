@echo off
chcp 65001 >nul
poetry run python mp4tomp3.py %*
pause

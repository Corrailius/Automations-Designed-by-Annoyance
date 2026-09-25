@echo off

cd /d "%~dp0"

if not exist build.log mkdir build.log

if exist build.log\ran.build.md del build.log\ran.build.md
if exist build.log\ran.error.md del build.log\ran.error.md

python main.py >> build.log\ran.build.md 2>> build.log\ran.error.md
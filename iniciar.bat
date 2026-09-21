@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -B app.py
  pause
  exit /b
)
where python >nul 2>&1
if not errorlevel 1 (
  python -B app.py
  pause
  exit /b
)
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
  "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -B app.py
  pause
  exit /b
)
echo Instala Python 3.10 o posterior desde python.org y volve a abrir este archivo.
pause

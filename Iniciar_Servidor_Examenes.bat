@echo off
echo Iniciando servidor local en http://localhost:8000
cd /d %~dp0
start "" http://localhost:8000
python -m http.server 8000

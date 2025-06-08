@echo off
echo Verificando entorno de Python...

:: Intenta ejecutar python --version
python --version >nul 2>&1
if %errorlevel%==0 (
    echo Python detectado.
    start http://localhost:8000
    python -m http.server 8000
    goto fin
)

:: Si no, intenta con py
py --version >nul 2>&1
if %errorlevel%==0 (
    echo Python detectado como 'py'.
    start http://localhost:8000
    py -m http.server 8000
    goto fin
)

:: Si ninguno está disponible
echo ERROR: No se encontró Python en el sistema.
echo Por favor instala Python desde https://www.python.org/ y asegúrate de agregarlo al PATH.
pause

:fin

@echo off
cd /d "%~dp0"
echo Iniciando dashboard a partir do diretorio correto...
echo Diretorio: %CD%
echo.
streamlit run src\dashboard\app.py

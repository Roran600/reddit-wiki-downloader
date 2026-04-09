@echo off
REM run_backup.bat - Windows batch script pre spustenie backup
cd /d "%~dp0"

if not exist venv\Scripts\activate.bat (
    echo [-] Virtuálne prostredie 'venv' neexistuje!
    echo    Spust: python -m venv venv
    echo    Potom: venv\Scripts\activate && pip install -r requirements.txt
    pause
    exit /b 1
)

echo [*] Aktivujem virtualne prostredie...
call venv\Scripts\activate.bat

echo [*] Spustam backup...
python backup.py

echo.
echo [*] Backup dokonceny
pause
@echo off
echo ========================================================
echo   Compilador Automático: The Sims 4 Unlocker Pro GUI
echo ========================================================
echo.
echo Verificando e instalando dependencias (menos de 1 minuto)...
pip install -q pyinstaller customtkinter

echo.
echo Compilando ejecutable en modo "OneFile / Independiente"...
echo El proceso esta optimizado para tardar menos de 2 minutos.
pyinstaller --noconfirm --onefile --windowed --clean --name="Sims4_Unlocker_Updater" ^
    --add-data "setup.bat;." ^
    --add-data "g_The Sims 3.ini;." ^
    --add-data "g_The Sims 4.ini;." ^
    --add-data "ea_app;ea_app" ^
    --add-data "origin;origin" ^
    unlocker_gui.py

echo.
echo ========================================================
echo [EXITO] Compilacion completada. 
echo Tu archivo ejecutable independiente (.exe) se encuentra 
echo en la nueva carpeta llamada "dist".
echo.
echo Puedes mover y ejecutar 'Sims4_Unlocker_Updater.exe'
echo donde quieras. TODOS los archivos del Unlocker estan
echo integrados dentro de el de forma invisible.
echo ========================================================
pause

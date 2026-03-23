@echo off
title 3F - Generador de Instalador
echo ============================================================
echo      GENERADOR DE INSTALADOR WIZARD (INNO SETUP)
echo ============================================================
echo.
echo Para generar el instalador (.exe), sigue estos pasos:
echo.
echo 1. Descarga e instala Inno Setup (gratis):
echo    https://jrsoftware.org/isdl.php
echo.
echo 2. Una vez instalado, puedes:
echo    a) Hacer clic derecho en 'installer\3f_setup.iss' y elegir 'Compile'.
echo    b) O abrir Inno Setup, cargar el archivo y presionar F9.
echo.
echo 3. El instalador se generara en la carpeta: 
echo    c:\xampp\htdocs\3F\dist\3F_FuturoForbes_Setup.exe
echo.
echo ------------------------------------------------------------
echo NOTA: He configurado el instalador para que:
echo - Copie todos los archivos necesarios.
echo - Cree un entorno virtual (.venv) automaticamente.
echo - Instale las dependencias de Python.
echo - Configure la base de datos local SQLite.
echo - Cree accesos directos en Escritorio y Menu Inicio.
echo - Inicie el sistema de forma 'silenciosa' (sin ventana negra).
echo ------------------------------------------------------------
echo.
pause

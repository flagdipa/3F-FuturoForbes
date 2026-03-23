' Script para iniciar FuturoForbes (3F) sin ventana de comando
Set WshShell = CreateObject("WScript.Shell")

' Obtener la ruta del directorio del script
strPath = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))

' Ejecutar el batch en modo oculto (0)
' El comando inicia el sistema y abre el navegador
WshShell.Run """" & strPath & "iniciar_sistema.bat"" /hidden", 0, False

' Esperar 2 segundos para que el servidor inicie
WScript.Sleep 2000

' Abrir el navegador
WshShell.Run "http://localhost:8000"

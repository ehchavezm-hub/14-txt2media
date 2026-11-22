' txt2media_gui.vbs — Abre la GUI sin ninguna ventana DOS
' Doble clic para abrir la interfaz grafica de txt2media
Option Explicit
Dim WShell, py, cmd
Set WShell = CreateObject("WScript.Shell")

' Detectar Python (preferir 3.14/3.13)
py = ""
If py = "" And WShell.Run("py -3.14 --version", 0, True) = 0 Then py = "py -3.14"
If py = "" And WShell.Run("py -3.13 --version", 0, True) = 0 Then py = "py -3.13"
If py = "" And WShell.Run("py -3.12 --version", 0, True) = 0 Then py = "py -3.12"
If py = "" And WShell.Run("py -3.15 --version", 0, True) = 0 Then py = "py -3.15"

If py = "" Then
    MsgBox "Python no encontrado. Ejecuta instalar.bat primero.", vbCritical, "txt2media"
    WScript.Quit 1
End If

' Lanzar GUI — el 0 oculta toda ventana de consola
cmd = py & " -m txt2media.ui.ventana_principal"
WShell.Run cmd, 0, False

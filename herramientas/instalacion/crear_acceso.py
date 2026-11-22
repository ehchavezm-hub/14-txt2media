"""
crear_acceso.py — Crea el acceso directo de txt2media en el Escritorio.
Llamado automáticamente por instalar_universal.bat
"""
import sys
import os
import subprocess


def find_pythonw():
    # Mejor opción: derivar del Python que está corriendo ahora mismo
    exe = sys.executable
    candidate = exe.replace("python.exe", "pythonw.exe")
    if os.path.exists(candidate):
        return candidate

    locs = []
    la = os.environ.get("LOCALAPPDATA", "")
    pf = os.environ.get("PROGRAMFILES", "")
    pf86 = os.environ.get("PROGRAMFILES(X86)", "")

    for base in [la, pf, pf86]:
        for ver in ["314", "313", "312", "311", "310"]:
            locs.append(os.path.join(base, "Programs", "Python", f"Python{ver}", "pythonw.exe"))
            locs.append(os.path.join(base, f"Python{ver}", "pythonw.exe"))

    locs += [
        os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "pyw.exe"),
        os.path.join(la, "Programs", "Python", "Launcher", "pyw.exe"),
    ]

    for loc in locs:
        if loc and os.path.exists(loc):
            return loc

    import shutil
    return shutil.which("pythonw") or shutil.which("pyw")


# Este archivo vive en herramientas/instalacion: la raíz del repositorio está dos niveles arriba
here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
launcher = os.path.join(here, "herramientas", "portable", "lanzar.pyw")
icon = os.path.join(here, "recursos", "icon.ico")
if not os.path.exists(icon):
    icon = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "imageres.dll") + ",11"

desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
shortcut_lnk = os.path.join(desktop, "txt2media.lnk")
pythonw = find_pythonw()

if pythonw:
    # Arguments must be: "C:\path\lanzar.pyw" (with real double-quotes, no backticks)
    # PowerShell single-quoted string preserves literal double-quotes inside it.
    ps = (
        f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{shortcut_lnk}');\n"
        f"$s.TargetPath='{pythonw}';\n"
        "$s.Arguments='\"" + launcher + "\"';\n"
        f"$s.WorkingDirectory='{here}';\n"
        f"$s.IconLocation='{icon}';\n"
        "$s.Description='txt2media v1.0.1';\n"
        "$s.Save()\n"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps],
        capture_output=True, text=True
    )
    if os.path.exists(shortcut_lnk):
        print(f"SHORTCUT_OK: {pythonw}")
    else:
        # Fallback: .vbs que siempre funciona (wscript.exe built-in)
        vbs = os.path.join(desktop, "txt2media.vbs")
        with open(vbs, "w") as f:
            f.write(
                f'Set sh = CreateObject("WScript.Shell")\n'
                f'sh.CurrentDirectory = "{here}"\n'
                f'sh.Run "{pythonw} ""{launcher}""", 0\n'
            )
        print(f"VBS_FALLBACK (ps_error: {result.stderr.strip()})")
else:
    # Sin pythonw: crear .vbs con python normal
    vbs = os.path.join(desktop, "txt2media.vbs")
    with open(vbs, "w") as f:
        f.write(
            f'Set sh = CreateObject("WScript.Shell")\n'
            f'sh.CurrentDirectory = "{here}"\n'
            f'sh.Run "python ""{launcher}""", 0\n'
        )
    print("VBS_FALLBACK_NO_PYTHONW")

"""
bootstrap_installer.py
Compilado con PyInstaller -> txt2media_setup.exe (único archivo, ~15 MB)
El EXE extrae los archivos de txt2media y ejecuta instalar_universal.bat
"""
import sys
import os
import base64
import io
import zipfile
import subprocess
import ctypes
import tempfile

# El ZIP con los archivos de txt2media se inyecta aquí por build_exe.bat / GitHub Actions
_ZIP_B64 = "__ZIP_CONTENT__"


def _is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def _elevate():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable,
        " ".join(f'"{a}"' for a in sys.argv),
        None, 1
    )
    sys.exit(0)


def main():
    if not _is_admin():
        _elevate()
        return

    install_dir = os.path.join(
        os.environ.get("LOCALAPPDATA", os.environ["APPDATA"]),
        "txt2media"
    )
    os.makedirs(install_dir, exist_ok=True)

    # Extraer archivos del ZIP embebido
    raw_b64 = _ZIP_B64.replace("\n", "").replace(" ", "")
    zip_data = base64.b64decode(raw_b64)
    with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
        for name in z.namelist():
            if not name.startswith("txt2media/"):
                continue
            rel = name[len("txt2media/"):]
            if not rel:
                continue
            target = os.path.join(install_dir, rel.replace("/", os.sep))
            if name.endswith("/"):
                os.makedirs(target, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, "wb") as f:
                    f.write(z.read(name))

    # Ejecutar el instalador BAT (el que muestra la ventana verde)
    bat = os.path.join(install_dir, "instalar_universal.bat")
    if not os.path.exists(bat):
        bat = os.path.join(install_dir, "herramientas", "instalacion", "instalar_universal.bat")
    subprocess.call(["cmd", "/c", bat], cwd=install_dir)


if __name__ == "__main__":
    main()

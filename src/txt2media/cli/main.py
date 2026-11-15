"""CLI principal de txt2media v1.0.1."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_VERSION = "1.0.1"

_FORMATOS = {
    "pptx": ".pptx",
    "docx": ".docx",
    "xlsx": ".xlsx",
    "audio": ".mp3",
    "video": ".mp4",
}

_VOCES_ALIAS = {
    "camila": "es-PE-CamilaNeural",
    "alex": "es-PE-AlexNeural",
    "es-pe-camilaneural": "es-PE-CamilaNeural",
    "es-pe-alexneural": "es-PE-AlexNeural",
}


def main() -> None:
    from txt2media.utils.logging_config import configurar_logging
    configurar_logging()

    parser = _construir_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)

    args.func(args)


def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="txt2media",
        description=f"txt2media v{_VERSION} — Convierte documentos a múltiples formatos",
    )
    parser.add_argument("--version", action="version", version=f"txt2media {_VERSION}")

    sub = parser.add_subparsers(dest="comando")

    # ---- convertir -------------------------------------------------- #
    p_conv = sub.add_parser("convertir", help="Convierte un documento")
    p_conv.add_argument("archivo", nargs="+", help="Archivo(s) de entrada")
    p_conv.add_argument(
        "--formato",
        choices=list(_FORMATOS.keys()),
        default="pptx",
        help="Formato de salida (default: pptx)",
    )
    p_conv.add_argument(
        "--salida",
        default=".",
        help="Carpeta de salida (default: directorio actual)",
    )
    p_conv.add_argument(
        "--voz",
        default="camila",
        help="Voz TTS: camila, alex, o nombre completo Azure (default: camila)",
    )
    p_conv.add_argument(
        "--modo",
        choices=["completo", "capitulos"],
        default="completo",
        help="Modo audio: completo (un archivo) o capitulos (uno por sección)",
    )
    p_conv.set_defaults(func=_cmd_convertir)

    # ---- clave ------------------------------------------------------ #
    p_clave = sub.add_parser("clave", help="Gestiona claves API")
    sub_clave = p_clave.add_subparsers(dest="accion_clave")

    p_set = sub_clave.add_parser("guardar", help="Guarda una clave en Credential Manager")
    p_set.add_argument("nombre", help="Nombre de la clave: azure_key, azure_region")
    p_set.add_argument("valor", help="Valor de la clave")
    p_set.set_defaults(func=_cmd_clave_guardar)

    p_check = sub_clave.add_parser("verificar", help="Verifica si una clave está guardada")
    p_check.add_argument("nombre", help="Nombre de la clave")
    p_check.set_defaults(func=_cmd_clave_verificar)

    # ---- info ------------------------------------------------------- #
    p_info = sub.add_parser("info", help="Muestra información del sistema")
    p_info.set_defaults(func=_cmd_info)

    return parser


# ------------------------------------------------------------------ #
# Comandos                                                            #
# ------------------------------------------------------------------ #

def _cmd_convertir(args: argparse.Namespace) -> None:
    from txt2media.core.orquestador import Orquestador

    voz = _resolver_voz(args.voz)
    carpeta_salida = Path(args.salida)
    archivos = [Path(a) for a in args.archivo]

    for archivo in archivos:
        if not archivo.exists():
            print(f"[ERROR] Archivo no encontrado: {archivo}", file=sys.stderr)
            sys.exit(1)

    formato = args.formato
    modo = getattr(args, "modo", "completo")

    if formato == "audio" and modo == "capitulos":
        _convertir_audio_capitulos(archivos, voz, carpeta_salida)
        return

    if formato == "video":
        _convertir_video(archivos, voz, carpeta_salida)
        return

    orq = Orquestador()

    def cb(i: int, total: int, nombre: str) -> None:
        print(f"[{i}/{total}] Procesando: {nombre}")

    resultados = orq.procesar(archivos, formato, carpeta_salida, cb)
    print(f"\nCompletado: {len(resultados)} archivo(s) generado(s) en {carpeta_salida}")
    for r in resultados:
        print(f"  → {r}")


def _convertir_audio_capitulos(archivos: list[Path], voz: str, carpeta_salida: Path) -> None:
    from txt2media.generadores.generador_audio import GeneradorAudio

    for archivo in archivos:
        doc = _leer_documento(archivo)
        sub_carpeta = carpeta_salida / archivo.stem
        gen = GeneradorAudio(voz=voz)
        archivos_gen = gen.generar_capitulos(doc, sub_carpeta)
        print(f"Capítulos generados en {sub_carpeta}:")
        for a in archivos_gen:
            print(f"  → {a.name}")
        if (sub_carpeta / "playlist.m3u").exists():
            print(f"  → playlist.m3u")
        if (sub_carpeta / "cover.jpg").exists():
            print(f"  → cover.jpg")


def _convertir_video(archivos: list[Path], voz: str, carpeta_salida: Path) -> None:
    from txt2media.generadores.generador_video import GeneradorVideo

    carpeta_salida.mkdir(parents=True, exist_ok=True)
    gen = GeneradorVideo(voz=voz)
    for archivo in archivos:
        doc = _leer_documento(archivo)
        salida = carpeta_salida / (archivo.stem + ".mp4")
        gen.generar(doc, salida)
        print(f"  → {salida}")


def _leer_documento(archivo: Path):
    ext = archivo.suffix.lower()
    if ext == ".md":
        from txt2media.lectores.lector_md import LectorMarkdown
        return LectorMarkdown().leer(archivo)
    elif ext == ".docx":
        from txt2media.lectores.lector_docx import LectorDOCX
        return LectorDOCX().leer(archivo)
    elif ext == ".epub":
        from txt2media.lectores.lector_epub import LectorEPUB
        return LectorEPUB().leer(archivo)
    elif ext == ".pdf":
        from txt2media.lectores.lector_pdf import LectorPDF
        return LectorPDF().leer(archivo)
    else:
        raise ValueError(f"Extensión no soportada: {ext}")


def _resolver_voz(voz_arg: str) -> str:
    return _VOCES_ALIAS.get(voz_arg.lower(), voz_arg)


def _cmd_clave_guardar(args: argparse.Namespace) -> None:
    import keyring
    keyring.set_password("txt2media", args.nombre, args.valor)
    print(f"Clave '{args.nombre}' guardada en Windows Credential Manager.")


def _cmd_clave_verificar(args: argparse.Namespace) -> None:
    import keyring
    valor = keyring.get_password("txt2media", args.nombre)
    if valor:
        print(f"Clave '{args.nombre}': configurada ✓")
    else:
        print(f"Clave '{args.nombre}': NO configurada ✗")


def _cmd_info(args: argparse.Namespace) -> None:
    import shutil
    import platform
    from txt2media import __version__
    from txt2media.motores.cadena_voz import CadenaVoz
    from txt2media.utils.rutas import get_datos_dir

    print(f"txt2media v{__version__}")
    print(f"Python {platform.python_version()} en {platform.system()}")
    print(f"Datos: {get_datos_dir()}")

    cadena = CadenaVoz()
    motor = cadena.motor_disponible()
    print(f"Motor TTS disponible: {motor or 'ninguno'}")

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        print(f"ffmpeg: encontrado en {ffmpeg}")
    else:
        print("ffmpeg: NO encontrado  (video deshabilitado)")
        print("        → Instalar: winget install Gyan.FFmpeg")
        print("          o descargar desde https://ffmpeg.org/download.html")

    # Detectar comando Python actual
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    py_cmd = f"py -{py_ver} -m txt2media.cli.main"

    print("\nFormatos soportados:")
    filas = [
        ("pptx",  "PowerPoint",           f"{py_cmd} convertir archivo.pdf --formato pptx"),
        ("docx",  "Word",                 f"{py_cmd} convertir archivo.pdf --formato docx"),
        ("xlsx",  "Excel",                f"{py_cmd} convertir archivo.pdf --formato xlsx"),
        ("audio", "Audio MP3 (completo)", f"{py_cmd} convertir archivo.pdf --formato audio"),
        ("audio", "Audio MP3 (capíts.)",  f"{py_cmd} convertir archivo.pdf --formato audio --modo capitulos"),
        ("video", "Video MP4",            f"{py_cmd} convertir archivo.pdf --formato video"),
    ]
    print(f"  {'Formato':<8} {'Descripción':<24} Ejemplo de comando")
    print("  " + "-" * 80)
    for fmt, desc, cmd in filas:
        print(f"  {fmt:<8} {desc:<24} {cmd}")


if __name__ == "__main__":
    main()

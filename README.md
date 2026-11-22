# txt2media v1.0.1

Convierte documentos EPUB, PDF, DOCX y Markdown a múltiples formatos de salida:
PowerPoint, Word, Excel, Audio MP3 (completo o por capítulos) y Video MP4.

## Instalación

```bash
cd "C:\09\00 txt2media"
py -3.13 -m pip install -e .

# Opcional: OCR para PDFs escaneados (requiere Tesseract instalado)
py -3.13 -m pip install -e .[ocr]
```

## Uso desde la terminal (recomendado)

`txt2media.cmd` trae la última versión desde GitHub (`git pull`) antes de cada
uso, instala las dependencias si hace falta y luego ejecuta lo que pidas.
Funciona en CMD y en PowerShell.

Primera vez (requiere Git y Python 3.13):

```bash
git clone https://github.com/ehchavezm-hub/14-txt2media "C:\09\00 txt2media"
cd "C:\09\00 txt2media"
```

Después, siempre desde esa carpeta:

| Comando | Qué hace |
|---|---|
| `.\txt2media` | Actualiza y abre la ventana |
| `.\txt2media convertir "libro.pdf" --formato audio` | Actualiza y convierte |
| `.\txt2media convertir "libro.pdf" --formato audio --modo capitulos --salida D:\Audiolibros` | Audio por capítulos |
| `.\txt2media info` | Estado del sistema (ffmpeg, voces, claves) |
| `.\txt2media actualizar` | Solo `git pull` y dependencias |
| `.\txt2media ayuda` | Todos los comandos y opciones |

Para no actualizar en una ejecución: `set TXT2MEDIA_SIN_PULL=1` (CMD) o
`$env:TXT2MEDIA_SIN_PULL=1` (PowerShell).

## Uso rápido (CLI)

| Formato       | Comando                                                                                      |
|---------------|----------------------------------------------------------------------------------------------|
| PowerPoint    | `py -3.13 -m txt2media.cli.main convertir "libro.pdf" --formato pptx`                      |
| Word          | `py -3.13 -m txt2media.cli.main convertir "libro.pdf" --formato docx`                      |
| Excel         | `py -3.13 -m txt2media.cli.main convertir "libro.pdf" --formato xlsx`                      |
| Audio completo| `py -3.13 -m txt2media.cli.main convertir "libro.pdf" --formato audio`                     |
| Audio caps.   | `py -3.13 -m txt2media.cli.main convertir "libro.pdf" --formato audio --modo capitulos`    |
| Video         | `py -3.13 -m txt2media.cli.main convertir "libro.pdf" --formato video`                     |

### Opciones de voz

```bash
# Usar voz Camila (predeterminada)
py -3.13 -m txt2media.cli.main convertir "libro.pdf" --formato audio --voz camila

# Usar voz Alex
py -3.13 -m txt2media.cli.main convertir "libro.pdf" --formato audio --voz alex
```

### Capítulos para BookPlayer (iOS)

```bash
py -3.13 -m txt2media.cli.main convertir "libro.pdf" --formato audio --modo capitulos --salida "D:\Audiolibros"
```

Genera en la carpeta de salida:
- `01_introduccion.mp3`, `02_capitulo_uno.mp3`, ...
- `cover.jpg` (portada 400×600)
- `playlist.m3u` (compatible con BookPlayer iOS)

## Configurar voz Azure (opcional)

```bash
# Guardar clave Azure en Windows Credential Manager
py -3.13 -m txt2media.cli.main clave guardar azure_key TU_CLAVE_AQUI
py -3.13 -m txt2media.cli.main clave guardar azure_region eastus

# Verificar
py -3.13 -m txt2media.cli.main clave verificar azure_key
```

Sin clave Azure, el sistema usa **edge-tts** (gratuito, requiere Internet)
o **SAPI5** (local, solo Windows).

## Interfaz gráfica

```bash
py -3.13 -c "from txt2media.ui.ventana_principal import lanzar_app; lanzar_app()"
```

## Desarrollo

```bash
# Activar modo desarrollo (datos en ./datos_dev/)
set CONVDOC_DEV=1

# Ejecutar tests
py -3.13 -m pytest tests/ -v
```

## Requisitos del sistema

- Windows 10/11 (64-bit)
- Python 3.12 o 3.13
- ffmpeg (para formato video) — agregar al PATH
- Internet (para edge-tts / Azure TTS) — opcional

## Estructura del proyecto

En la raíz solo queda lo necesario. **El único archivo para ejecutar es `txt2media.cmd`.**

```
txt2media/
├── txt2media.cmd        ← EJECUTAR ESTE (git pull + abre la app o la CLI)
├── README.md            Guía de uso
├── CLAUDE.md            Instrucciones para Claude
├── pyproject.toml       Dependencias y metadatos de Python
├── src/txt2media/       Código de la aplicación
│   ├── core/            Modelo, configuración, tema
│   ├── lectores/        EPUB, PDF, DOCX, Markdown
│   ├── generadores/     PPTX, DOCX, XLSX, MD, HTML, Audio, Video
│   ├── motores/         Voz: Azure, edge-tts, SAPI
│   ├── ui/              Ventana (PySide6)
│   ├── cli/             Línea de comandos
│   └── utils/           Rutas, seguridad, logging
├── tests/               Pruebas automáticas (pytest)
├── recursos/            Fuentes, tema e icono
├── docs/                Historial de cambios, licencias, alcance e investigación
└── herramientas/        Scripts secundarios (no hace falta usarlos a diario)
    ├── portable/        ejecutar.bat, lanzar.pyw (van dentro del ZIP portable)
    ├── compilar/        build_exe.bat, construir_portable.bat, main_exe.py, *.spec
    ├── instalacion/     instalar.bat, instalar_universal.bat, crear_acceso.py
    ├── ventana/         Lanzadores antiguos de la ventana y diagnóstico
    └── mantenimiento/   guardar.bat, auto_guardar.ps1, verificar.bat, test_video.bat
```

Detalle de cada script en [`herramientas/README.md`](herramientas/README.md).

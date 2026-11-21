# txt2media v1.0.1

Convierte documentos EPUB, PDF, DOCX y Markdown a múltiples formatos de salida:
PowerPoint, Word, Excel, Audio MP3 (completo o por capítulos) y Video MP4.

## Instalación

```bash
cd D:\PST\txt2media
py -3.13 -m pip install -e .

# Opcional: OCR para PDFs escaneados (requiere Tesseract instalado)
py -3.13 -m pip install -e .[ocr]
```

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

```
txt2media/
├── src/txt2media/
│   ├── core/          # Modelo, configuración, cadena de voz
│   ├── lectores/      # EPUB, PDF, DOCX, Markdown
│   ├── generadores/   # PPTX, DOCX, XLSX, Audio, Video
│   ├── motores/       # Azure, edge-tts, SAPI
│   ├── ui/            # PySide6 GUI
│   ├── cli/           # Interfaz de línea de comandos
│   └── utils/         # Rutas, logging
├── tests/
├── recursos/
├── pyproject.toml
└── verificar.bat
```

# Changelog — txt2media

## [Sin publicar]

### Cambios
- Eliminada la dependencia `moviepy`: no se usaba (el video se genera con ffmpeg)
- `pytesseract` declarado como dependencia opcional: `pip install -e .[ocr]`
- `LICENCIAS.md`: añadidas dependencias opcionales y programas externos (ffmpeg, Tesseract)
- README: instalación unificada con Python 3.13


## [1.0.1] — 2026-11-15

### Nuevas características
- **Audio por capítulos**: `--modo capitulos` genera un MP3 por sección
- **Voces es-PE**: Camila (`es-PE-CamilaNeural`) y Alex (`es-PE-AlexNeural`)
- **cover.jpg**: portada 400×600 generada automáticamente con Pillow
- **playlist.m3u**: playlist `#EXTM3U` compatible con BookPlayer (iOS)
- **CLI `--voz`**: alias `camila` / `alex` para la voz TTS
- **CLI `--modo`**: `completo` (un MP3) o `capitulos` (uno por sección)

### Cambios
- Voz predeterminada: `es-PE-CamilaNeural` (antes `es-ES-AlvaroNeural`)
- Formato de audio: `.mp3` (antes `.wav`)
- Todas las dependencias usan `>=` para compatibilidad con Python 3.14

### Correcciones
- Escritura atómica en todos los generadores (tempfile + os.replace)
- ModoLocalEstricto anidable y thread-safe

---

## [1.0.0] — 2026-10-01

### Primera versión
- Lectura: EPUB, PDF, DOCX, Markdown
- Exportación: PPTX, DOCX, XLSX, Audio (un archivo), Video
- Cadena de voces: Azure → edge-tts → SAPI
- Tema Tableau 10 + Figtree
- Secretos en Windows Credential Manager (keyring)
- Modo Local Estricto (sin red)
- UI PySide6 con arrastrar y soltar
- Datos en `%APPDATA%\txt2media`
- `CONVDOC_DEV=1` → `./datos_dev/`

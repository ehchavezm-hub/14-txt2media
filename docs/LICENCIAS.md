# Licencias de dependencias — txt2media v1.0.1

Todas las dependencias incluidas son **LGPL, MIT, BSD, Apache, MPL, PSF o HPND**.
No se incluye ninguna dependencia bajo licencia AGPL o GPL.

| Paquete          | Versión mínima | Licencia   | Uso                             |
|------------------|---------------|------------|---------------------------------|
| PySide6          | 6.10.0        | LGPL-3.0   | Interfaz gráfica Qt             |
| pdfplumber       | 0.11.4        | MIT        | Lectura de PDF                  |
| pypdfium2        | 5.15.2        | Apache-2.0 | Renderizado de PDF              |
| python-docx      | 1.2.0         | MIT        | Lectura/escritura DOCX          |
| python-pptx      | 1.0.2         | MIT        | Generación PPTX                 |
| openpyxl         | 3.1.5         | MIT        | Generación XLSX                 |
| markdown-it-py   | 3.0.0         | MIT        | Parser Markdown                 |
| Pillow           | 11.0.0        | HPND       | Imágenes, cover.jpg             |
| httpx            | 0.27.0        | BSD-3      | Llamadas Azure TTS REST         |
| edge-tts         | 6.1.12        | MIT        | TTS gratuito (edge-tts)         |
| pyttsx3          | 2.90          | MIT        | SAPI5 fallback local            |
| keyring          | 25.4.0        | MIT        | Credential Manager Windows      |
| langdetect       | 1.0.9         | Apache-2.0 | Detección de idioma             |
| jsonschema       | 4.23.0        | MIT        | Validación JSON                 |
| defusedxml       | 0.7.1         | PSF-2.0    | XML seguro para EPUB            |
| beautifulsoup4   | 4.12.3        | MIT        | HTML parsing (EPUB)             |
| lxml             | 5.3.0         | BSD-3      | Backend bs4 para EPUB           |

### Dependencias opcionales

| Paquete          | Versión mínima | Licencia   | Uso                                         |
|------------------|---------------|------------|---------------------------------------------|
| pytesseract      | 0.3.10        | Apache-2.0 | OCR de páginas escaneadas en PDF (`pip install -e .[ocr]`) |

### Programas externos (no se redistribuyen)

| Programa  | Licencia   | Uso                                                        |
|-----------|------------|------------------------------------------------------------|
| ffmpeg    | LGPL-2.1+ (según compilación) | Generación de video MP4 (proceso externo) |
| Tesseract | Apache-2.0 | Motor OCR usado por pytesseract; opcional                  |

**Nota:** el video se genera llamando a `ffmpeg` como proceso externo, por lo que
`ffmpeg` debe instalarse por separado. Si `pytesseract` o Tesseract no están
instalados, las páginas escaneadas simplemente se omiten sin error.

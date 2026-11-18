# Notas de sesión — 17/18-11-2026

Traspaso para continuar el trabajo desde otra cuenta. **No se modificó código**: solo documentación en `docs/`.

## Qué se hizo

1. **Documento de alcance de txt2media v1.0.1** → `docs/alcance/txt2media_Alcance.html`
   Alcance completo de la app tal como está hoy en el repositorio: entradas, modelo de documento,
   7 formatos de salida, cadena de voz, interfaces, seguridad, arquitectura y pendientes.
   Es el documento principal de esta sesión.

2. **Consultas sobre librerías de OCR y PDF** (solo investigación, no es parte del alcance actual) → `docs/investigacion-ocr/`
   - `OCR_PDF_Ranking_Librerias_original.html`: ranking de 28 librerías que trajo el usuario.
   - `OCR_PDF_Ranking_Librerias.html`: el mismo ranking con columna de ventajas y desventajas.
   - `Motor_OCR_Inteligente_Alcance.html`: propuesta de un motor OCR que elige el mejor motor por página.
   - `whiteboard_motor_ocr.json`: datos del whiteboard del motor OCR.
     Versión editable en claude.ai (privada, de la cuenta original):
     https://claude.ai/artifact/2MGjCVTvrb8hD6q5Yz6Xh1

## Pendientes detectados en txt2media (sección 10 del alcance)

- `pytesseract` se usa como OCR opcional en `lectores/lector_pdf.py`, pero no está en `LICENCIAS.md`.
- `moviepy` está declarado en `pyproject.toml` y no se usa (el video se hace con ffmpeg).
- `core/resumen_local.py` (resumen extractivo sin red) existe pero ninguna interfaz lo usa.
- El README instala con `py -3.14` y ejecuta con `py -3.13`: unificar en 3.13.

## Conclusiones de la consulta de OCR (por si se retoma)

- Prohibidas por la regla de licencias: PyMuPDF, pymupdf4llm, borb (AGPL); Surya, marker, nougat (GPL / CC-BY-NC).
- Candidatas compatibles: docling (MIT), PaddleOCR / RapidOCR (Apache 2.0), Tesseract (Apache 2.0),
  TrOCR (MIT), pix2tex (MIT), Azure Document Intelligence (nube, de pago).
- OCRmyPDF depende de Ghostscript (AGPL): para PDF buscable usar pikepdf o pypdfium2.
- Decisiones abiertas si se retoma: ¿nube permitida?, ¿GPU en las PCs?, ¿tamaño del instalador?, ¿imágenes como entrada?

## Instrucción del usuario vigente

"Aún no desarrolles nada": no se debe cambiar código hasta que el usuario lo pida.

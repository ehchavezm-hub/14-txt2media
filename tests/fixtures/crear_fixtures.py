"""Script para crear documentos de prueba sintéticos.

Ejecutar una vez: python tests/fixtures/crear_fixtures.py
Los fixtures se guardan en tests/fixtures/
"""

from pathlib import Path

FIXTURES_DIR = Path(__file__).parent


def crear_fixture_md() -> None:
    """Crea un archivo Markdown sintético con estructura completa."""
    contenido = """# Informe Técnico de Obra

## 1. Introducción

Este documento describe el avance de la obra correspondiente al período enero-marzo 2026.
El proyecto contempla la construcción de 2,500 m² de área techada con un presupuesto
de S/ 4,500,000.00.

## 2. Avance de Obra

### 2.1 Estructuras

Los trabajos de estructuras han alcanzado un avance del 75%, superando la meta
programada de 70%.

La resistencia del concreto alcanzó 350 kg/cm² en todas las muestras analizadas.

### 2.2 Acabados

- Pintura interior: 60% completado
- Pintura exterior: 45% completado
- Instalaciones eléctricas: 80% completado

## 3. Tabla de Partidas

| Partida | Unidad | Metrado | Avance |
|---------|--------|---------|--------|
| Concreto f'c=350 kg/cm² | m³ | 450.00 | 75% |
| Acero fy=4200 kg/cm² | kg | 15,000 | 80% |
| Encofrado | m² | 1,200 | 70% |

## 4. Conclusiones

El proyecto se encuentra dentro del cronograma establecido. Se proyecta la
finalización para el 30 de junio de 2026.

> **Nota**: Los datos presentados corresponden al corte del 31 de marzo de 2026.
"""
    ruta = FIXTURES_DIR / "informe_obra.md"
    ruta.write_text(contenido, encoding="utf-8")
    print(f"✓ Creado: {ruta}")


def crear_fixture_md_simple() -> None:
    """Crea un Markdown simple con tildes, ñ y emojis."""
    contenido = """# Análisis Técnico 🏗️

Documento de análisis con caracteres especiales: ñ, á, é, í, ó, ú, ü.

## Sección Principal

Contenido con «comillas tipográficas» y —guiones largos—.

### Subsección

Texto de prueba con emoji 📊 y más contenido.
"""
    ruta = FIXTURES_DIR / "caracteres_especiales.md"
    ruta.write_text(contenido, encoding="utf-8")
    print(f"✓ Creado: {ruta}")


def crear_fixture_docx() -> None:
    """Crea un archivo DOCX sintético."""
    try:
        from docx import Document
        from docx.shared import Pt
    except ImportError:
        print("⚠ python-docx no instalado, saltando fixture DOCX")
        return

    doc = Document()
    doc.add_heading("Informe de Gestión", level=1)
    doc.add_paragraph("Este informe presenta los resultados del período Q1 2026.")

    doc.add_heading("1. Resumen Ejecutivo", level=2)
    doc.add_paragraph(
        "El proyecto reporta un avance del 78% con un presupuesto ejecutado "
        "de S/ 3,510,000.00 sobre un total de S/ 4,500,000.00."
    )

    doc.add_heading("2. Indicadores Clave", level=2)
    doc.add_paragraph("Los siguientes indicadores fueron medidos durante el período:")

    # Tabla
    tabla = doc.add_table(rows=4, cols=3)
    tabla.style = "Table Grid"
    encabezados = ["Indicador", "Meta", "Resultado"]
    for i, enc in enumerate(encabezados):
        tabla.rows[0].cells[i].text = enc
    datos = [
        ["Avance físico", "75%", "78%"],
        ["Costo por m²", "S/ 1,800", "S/ 1,752"],
        ["Días de obra", "90", "87"],
    ]
    for j, fila in enumerate(datos, start=1):
        for k, celda in enumerate(fila):
            tabla.rows[j].cells[k].text = celda

    doc.add_heading("3. Conclusiones", level=2)
    doc.add_paragraph(
        "El proyecto supera las metas establecidas. La eficiencia en el uso "
        "de recursos es un 2.7% mejor que lo planificado."
    )

    ruta = FIXTURES_DIR / "informe_gestion.docx"
    doc.save(str(ruta))
    print(f"✓ Creado: {ruta}")


def crear_fixture_epub() -> None:
    """Crea un archivo EPUB sintético mínimo."""
    import zipfile

    ruta = FIXTURES_DIR / "libro_tecnico.epub"

    opf_contenido = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Manual Técnico de Construcción</dc:title>
    <dc:creator>COSAPI S.A.</dc:creator>
    <dc:language>es</dc:language>
    <dc:identifier id="uid">urn:uuid:test-epub-123</dc:identifier>
  </metadata>
  <manifest>
    <item id="cap1" href="cap1.xhtml" media-type="application/xhtml+xml"/>
    <item id="cap2" href="cap2.xhtml" media-type="application/xhtml+xml"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine toc="ncx">
    <itemref idref="cap1"/>
    <itemref idref="cap2"/>
  </spine>
</package>"""

    cap1 = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Capítulo 1</title></head>
<body>
  <h1>Capítulo 1: Fundamentos</h1>
  <p>Este capítulo presenta los fundamentos técnicos del proyecto de construcción.</p>
  <h2>1.1 Materiales</h2>
  <p>Los materiales utilizados cumplen con la norma técnica peruana NTP 339.034.</p>
  <ul>
    <li>Cemento Portland Tipo I</li>
    <li>Agregado fino conforme NTP 400.037</li>
    <li>Agua potable</li>
  </ul>
  <table>
    <tr><th>Material</th><th>Norma</th><th>Resistencia</th></tr>
    <tr><td>Concreto</td><td>NTP 339.034</td><td>350 kg/cm²</td></tr>
    <tr><td>Acero</td><td>ASTM A615</td><td>4200 kg/cm²</td></tr>
  </table>
</body>
</html>"""

    cap2 = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Capítulo 2</title></head>
<body>
  <h1>Capítulo 2: Proceso Constructivo</h1>
  <p>El proceso constructivo sigue la secuencia estándar definida en el expediente técnico.</p>
  <h2>2.1 Etapas</h2>
  <p>Las etapas del proceso se ejecutan en estricto orden cronológico.</p>
  <ol>
    <li>Trazo y replanteo</li>
    <li>Movimiento de tierras</li>
    <li>Cimentación</li>
    <li>Estructura</li>
    <li>Acabados</li>
  </ol>
</body>
</html>"""

    toc = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
  "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content="urn:uuid:test-epub-123"/></head>
  <docTitle><text>Manual Técnico</text></docTitle>
  <navMap>
    <navPoint id="nav1" playOrder="1">
      <navLabel><text>Capítulo 1</text></navLabel>
      <content src="cap1.xhtml"/>
    </navPoint>
    <navPoint id="nav2" playOrder="2">
      <navLabel><text>Capítulo 2</text></navLabel>
      <content src="cap2.xhtml"/>
    </navPoint>
  </navMap>
</ncx>"""

    with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/epub+zip")
        zf.writestr("META-INF/container.xml",
            '<?xml version="1.0"?>'
            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            '<rootfiles><rootfile full-path="OEBPS/content.opf" '
            'media-type="application/oebps-package+xml"/></rootfiles></container>'
        )
        zf.writestr("OEBPS/content.opf", opf_contenido)
        zf.writestr("OEBPS/cap1.xhtml", cap1)
        zf.writestr("OEBPS/cap2.xhtml", cap2)
        zf.writestr("OEBPS/toc.ncx", toc)

    print(f"✓ Creado: {ruta}")


def crear_fixture_zip_malicioso() -> None:
    """Crea un ZIP malicioso para pruebas de seguridad."""
    import zipfile

    ruta = FIXTURES_DIR / "zip_malicioso.zip"
    with zipfile.ZipFile(ruta, "w") as zf:
        zf.writestr("../../../evil.py", "print('pwned')")
    print(f"✓ Creado: {ruta}")


if __name__ == "__main__":
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    crear_fixture_md()
    crear_fixture_md_simple()
    crear_fixture_docx()
    crear_fixture_epub()
    crear_fixture_zip_malicioso()
    print("\n✓ Todos los fixtures creados en", FIXTURES_DIR)

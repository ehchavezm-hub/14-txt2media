"""Generador DOCX con diseño editorial: portada, índice, capítulos con color y tablas estilizadas."""

from __future__ import annotations

import os
import re
import tempfile
from datetime import date
from pathlib import Path

from txt2media.core.modelo import Bloque, Documento, TipoBloque
from txt2media.generadores.estilo import (
    PALETA, color_capitulo, formato_miles, minutos_lectura, nivel_relativo, numeracion, palabras_de,
)

_F_TITULO = "Segoe UI"
_F_TEXTO = "Georgia"
_F_MONO = "Consolas"
_RE_NUM_TITULO = re.compile(r"^\s*(\d+(?:\.\d+)*)[.)]?\s+(\S.*)$")


def _hex(c: str) -> str:
    return c.lstrip("#").upper()


def _mezclar(color: str, base: str, proporcion: float) -> str:
    """Mezcla `proporcion` de `color` con `base` (p. ej. 14 % de azul sobre blanco)."""
    a = [int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(base.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x * proporcion + y * (1 - proporcion)):02X}" for x, y in zip(a, b))


class GeneradorDOCX:
    def generar(self, doc: Documento, salida: Path, opciones: dict | None = None) -> Path:
        from docx import Document

        salida = Path(salida)
        d = Document()
        self._preparar(d, doc)
        self._portada(d, doc)
        self._indice(d, doc)
        self._contenido(d, doc)

        salida.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(suffix=".docx", dir=salida.parent)
        os.close(fd)
        try:
            d.save(tmp)
            os.chmod(tmp, 0o644)  # mkstemp crea el archivo solo para el dueño
            os.replace(tmp, salida)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
        return salida

    # ------------------------------------------------------------------ #
    def _preparar(self, d, doc: Documento) -> None:
        from docx.enum.text import WD_LINE_SPACING
        from docx.shared import Cm, Pt, RGBColor

        sec = d.sections[0]
        sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
        sec.left_margin = sec.right_margin = Cm(2.5)
        sec.top_margin, sec.bottom_margin = Cm(2.4), Cm(2.2)
        sec.different_first_page_header_footer = True

        st = d.styles
        normal = st["Normal"]
        normal.font.name = _F_TEXTO
        normal.font.size = Pt(11)
        normal.font.color.rgb = RGBColor.from_string(_hex(PALETA.tinta))
        self._fuente_este(normal, _F_TEXTO)
        pf = normal.paragraph_format
        pf.space_after = Pt(8)
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        pf.line_spacing = 1.3

        for nombre, tam in (("Heading 1", 22), ("Heading 2", 16), ("Heading 3", 13)):
            h = st[nombre]
            h.font.name = _F_TITULO
            h.font.size = Pt(tam)
            h.font.bold = True
            h.font.color.rgb = RGBColor.from_string(_hex(PALETA.tinta))
            self._fuente_este(h, _F_TITULO)
            h.paragraph_format.space_before = Pt(18 if nombre != "Heading 1" else 0)
            h.paragraph_format.space_after = Pt(10)
            h.paragraph_format.keep_with_next = True

        for nombre in ("List Bullet", "Caption"):
            if nombre in [s.name for s in st]:
                st[nombre].font.name = _F_TEXTO if nombre == "List Bullet" else _F_TITULO

        # Encabezado y pie (desde la página 2): título del documento y "Página X de Y"
        cab = sec.header.paragraphs[0]
        cab.text = ""
        r = cab.add_run(doc.titulo or "")
        self._run(r, _F_TITULO, 8.5, PALETA.tinta_3)
        cab.alignment = 2  # derecha
        self._borde_parrafo(cab, "bottom", PALETA.linea, 6)

        pie = sec.footer.paragraphs[0]
        pie.alignment = 1  # centro
        for texto, campo in (("Página ", None), (None, "PAGE"), (" de ", None), (None, "NUMPAGES")):
            if campo:
                self._campo(pie, campo, "1")
            else:
                self._run(pie.add_run(texto), _F_TITULO, 8.5, PALETA.tinta_3)
        for run in pie.runs:
            self._run(run, _F_TITULO, 8.5, PALETA.tinta_3)

        core = d.core_properties
        core.title = doc.titulo or ""
        core.author = doc.autor or ""
        core.comments = "Generado con txt2media"

        # Word actualiza el índice al abrir el documento
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        upd = OxmlElement("w:updateFields")
        upd.set(qn("w:val"), "true")
        d.settings.element.append(upd)

    def _portada(self, d, doc: Documento) -> None:
        from docx.enum.text import WD_BREAK
        from docx.shared import Cm, Pt

        palabras = palabras_de(doc)
        tabla = d.add_table(rows=1, cols=1)
        tabla.autofit = False
        celda = tabla.cell(0, 0)
        celda.width = Cm(16)
        self._sombrear(celda, PALETA.acento_suave)
        self._borde_celda_izq(celda, PALETA.acento, 48)
        self._margenes_celda(celda, 900)
        self._alto_fila(tabla.rows[0], Cm(14))

        p = celda.paragraphs[0]
        self._run(p.add_run("DOCUMENTO"), _F_TITULO, 10, PALETA.acento, negrita=True, espaciado=40)
        p.paragraph_format.space_after = Pt(18)
        p = celda.add_paragraph()
        self._run(p.add_run(doc.titulo or "Documento"), _F_TITULO, 34, PALETA.tinta, negrita=True)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(14)
        if doc.autor:
            p = celda.add_paragraph()
            self._run(p.add_run(doc.autor), _F_TITULO, 15, PALETA.tinta_2)
            p.paragraph_format.space_after = Pt(36)
        p = celda.add_paragraph()
        datos = [f"{len(doc.secciones)} secciones", f"{formato_miles(palabras)} palabras",
                 f"{minutos_lectura(palabras)} min de lectura"]
        self._run(p.add_run("   ·   ".join(datos)), _F_TITULO, 10.5, PALETA.acento, negrita=True)

        p = d.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        self._run(p.add_run(f"Generado con txt2media · {date.today().strftime('%d/%m/%Y')}"),
                  _F_TITULO, 9, PALETA.tinta_3)
        p.add_run().add_break(WD_BREAK.PAGE)

    def _indice(self, d, doc: Documento) -> None:
        """Índice automático de Word. Trae escritos los capítulos para que se vea aunque
        no se actualice; Word lo regenera con números de página al abrir el documento."""
        from docx.enum.text import WD_BREAK
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Cm, Pt

        p = d.add_paragraph()
        self._run(p.add_run("Contenido"), _F_TITULO, 24, PALETA.tinta, negrita=True)
        p.paragraph_format.space_after = Pt(16)
        self._borde_parrafo(p, "bottom", PALETA.acento, 12)

        def fld(run, tipo):
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), tipo)
            if tipo == "begin":
                e.set(qn("w:dirty"), "true")
            run._element.append(e)

        secciones = doc.secciones
        numeros = numeracion(secciones)
        entradas = []
        for i, sec in enumerate(secciones):
            nivel = nivel_relativo(secciones, sec)
            if nivel > 3:
                continue
            nombre = sec.titulo or f"Sección {numeros[i]}"
            numero = numeros[i]
            m = _RE_NUM_TITULO.match(nombre)
            if m:
                numero, nombre = m.group(1), m.group(2)
            entradas.append((nivel, numero, nombre, color_capitulo(i)))
        if not entradas:
            entradas = [(1, "", "Haz clic derecho y elige «Actualizar campo».", PALETA.tinta_3)]

        for k, (nivel, numero, nombre, color) in enumerate(entradas):
            q = d.add_paragraph()
            q.paragraph_format.left_indent = Cm(0.7 * (nivel - 1))
            q.paragraph_format.space_after = Pt(4 if nivel > 1 else 7)
            if k == 0:
                fld(q.add_run(), "begin")
                it = OxmlElement("w:instrText")
                it.set(qn("xml:space"), "preserve")
                it.text = ' TOC \\o "1-3" \\h \\z \\u '
                q.add_run()._element.append(it)
                fld(q.add_run(), "separate")
            if numero:
                self._run(q.add_run(f"{numero}   "), _F_TITULO, 10.5 if nivel == 1 else 9.5, color, negrita=True)
            self._run(q.add_run(nombre), _F_TITULO, 10.5 if nivel == 1 else 9.5,
                      PALETA.tinta if nivel == 1 else PALETA.tinta_2, negrita=nivel == 1)
            if k == len(entradas) - 1:
                fld(q.add_run(), "end")
        d.paragraphs[-1].add_run().add_break(WD_BREAK.PAGE)

    def _contenido(self, d, doc: Documento) -> None:
        from docx.shared import Pt

        secciones = doc.secciones
        numeros = numeracion(secciones)
        n_cap = sum(1 for s in secciones if nivel_relativo(secciones, s) == 1)
        saltar = n_cap > 1 and palabras_de(doc) / max(1, len(secciones)) > 120
        primero = True
        for i, sec in enumerate(secciones):
            nivel = nivel_relativo(secciones, sec)
            color = color_capitulo(i)
            nombre = sec.titulo or f"Sección {numeros[i]}"
            m = _RE_NUM_TITULO.match(nombre)
            numero = numeros[i]
            if m:
                numero, nombre = m.group(1), m.group(2)

            h = d.add_heading(level=min(nivel, 3))
            if nivel == 1 and saltar and not primero:
                h.paragraph_format.page_break_before = True
            primero = False
            self._run(h.add_run(f"{numero}   "), _F_TITULO, None, color, negrita=True)
            h.add_run(nombre)
            if nivel == 1:
                self._borde_parrafo(h, "bottom", color, 12)
                h.paragraph_format.space_after = Pt(14)

            notas: list[str] = []
            for b in sec.bloques:
                if b.tipo == TipoBloque.NOTA_PIE and b.contenido.strip():
                    notas.append(b.contenido.strip())
                else:
                    self._bloque(d, b, color)
            if notas:
                p = d.add_paragraph()
                p.paragraph_format.space_before = Pt(10)
                self._borde_parrafo(p, "top", PALETA.linea, 6)
                self._run(p.add_run("NOTAS"), _F_TITULO, 8, PALETA.tinta_3, negrita=True, espaciado=20)
                for n in notas:
                    q = d.add_paragraph()
                    q.paragraph_format.space_after = Pt(2)
                    self._run(q.add_run(n), _F_TITULO, 8.5, PALETA.tinta_2)

    def _bloque(self, d, b: Bloque, color: str) -> None:
        from docx.shared import Cm, Pt

        t = b.tipo
        if t == TipoBloque.PARRAFO and b.contenido.strip():
            p = d.add_paragraph()
            r = p.add_run(b.contenido.strip())
            r.bold = b.negrita or None
            r.italic = b.cursiva or None
        elif t == TipoBloque.TITULO and b.contenido.strip():
            d.add_heading(b.contenido.strip(), level=3)
        elif t == TipoBloque.LISTA and b.items_lista:
            for item in b.items_lista:
                p = d.add_paragraph(style="List Bullet")
                p.add_run(item)
                p.paragraph_format.space_after = Pt(3)
        elif t == TipoBloque.CITA and b.contenido.strip():
            p = d.add_paragraph()
            r = p.add_run(b.contenido.strip())
            self._run(r, _F_TEXTO, 12, PALETA.tinta_2, cursiva=True)
            p.paragraph_format.left_indent = Cm(0.6)
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(12)
            self._borde_parrafo(p, "left", color, 24, espacio=12)
            self._sombrear_parrafo(p, PALETA.papel)
        elif t == TipoBloque.CODIGO and b.contenido:
            tabla = d.add_table(rows=1, cols=1)
            celda = tabla.cell(0, 0)
            self._sombrear(celda, "#F4F6FA")
            self._margenes_celda(celda, 220)
            lineas = b.contenido.splitlines() or [""]
            p = celda.paragraphs[0]
            for k, linea in enumerate(lineas):
                if k:
                    p = celda.add_paragraph()
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                self._run(p.add_run(linea or " "), _F_MONO, 9.5, "#1E293B")
            d.add_paragraph().paragraph_format.space_after = Pt(2)
        elif t == TipoBloque.TABLA and b.tabla:
            self._tabla(d, b, color)
        elif t == TipoBloque.IMAGEN and b.imagen:
            self._imagen(d, b)
        elif t == TipoBloque.CAPTION and b.contenido.strip():
            p = d.add_paragraph()
            self._run(p.add_run(b.contenido.strip()), _F_TITULO, 9, PALETA.tinta_3, cursiva=True)
        elif t == TipoBloque.SEPARADOR:
            p = d.add_paragraph()
            p.alignment = 1
            self._run(p.add_run("◆   ◆   ◆"), _F_TITULO, 9, color)

    def _tabla(self, d, b: Bloque, color: str) -> None:
        from docx.shared import Pt

        t = b.tabla
        filas = [f.celdas for f in t.filas]
        cab = list(t.encabezados)
        if not cab:
            con_cab = [f for f in t.filas if f.es_encabezado]
            if con_cab:
                cab = con_cab[0].celdas
                filas = [f.celdas for f in t.filas if f is not con_cab[0]]
        n = max([len(cab)] + [len(f) for f in filas] + [0])
        if n == 0:
            return
        tabla = d.add_table(rows=0, cols=n)
        tabla.style = "Table Grid"
        self._bordes_tabla(tabla, PALETA.linea)
        if cab:
            fila = tabla.add_row()
            self._repetir_encabezado(fila)
            for k in range(n):
                c = fila.cells[k]
                self._sombrear(c, _mezclar(color, PALETA.fondo, 0.14))
                p = c.paragraphs[0]
                self._run(p.add_run(cab[k] if k < len(cab) else ""), _F_TITULO, 9.5, _mezclar(color, PALETA.tinta, 0.8), negrita=True)
                p.paragraph_format.space_after = Pt(0)
        for j, celdas in enumerate(filas):
            fila = tabla.add_row()
            for k in range(n):
                c = fila.cells[k]
                if j % 2 == 1:
                    self._sombrear(c, PALETA.papel)
                p = c.paragraphs[0]
                self._run(p.add_run(celdas[k] if k < len(celdas) else ""), _F_TITULO, 9.5, PALETA.tinta)
                p.paragraph_format.space_after = Pt(0)
        for fila in tabla.rows:
            for c in fila.cells:
                self._margenes_celda(c, 110)
        d.add_paragraph().paragraph_format.space_after = Pt(2)

    def _imagen(self, d, b: Bloque) -> None:
        import io
        from docx.shared import Cm

        img = b.imagen
        datos = img.datos
        if datos is None and img.ruta and Path(img.ruta).exists():
            datos = Path(img.ruta).read_bytes()
        if not datos:
            return
        try:
            d.add_picture(io.BytesIO(datos), width=Cm(15))
            d.paragraphs[-1].alignment = 1
        except Exception:
            return

    # ---- utilidades de formato (XML de Word) ---------------------------- #
    @staticmethod
    def _fuente_este(estilo, fuente: str) -> None:
        from docx.oxml.ns import qn
        rpr = estilo.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            from docx.oxml import OxmlElement
            rfonts = OxmlElement("w:rFonts")
            rpr.append(rfonts)
        for att in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rfonts.set(qn(att), fuente)

    @staticmethod
    def _run(r, fuente: str, tam, color: str, negrita: bool = False, cursiva: bool = False,
             espaciado: int | None = None) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Pt, RGBColor
        r.font.name = fuente
        rpr = r._element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.insert(0, rfonts)
        rfonts.set(qn("w:eastAsia"), fuente)
        if tam:
            r.font.size = Pt(tam)
        r.font.color.rgb = RGBColor.from_string(_hex(color))
        if negrita:
            r.bold = True
        if cursiva:
            r.italic = True
        if espaciado:
            sp = OxmlElement("w:spacing")
            sp.set(qn("w:val"), str(espaciado))
            rpr.append(sp)

    @staticmethod
    def _campo(p, instruccion: str, marcador: str) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        def fld(tipo):
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), tipo)
            if tipo == "begin":
                e.set(qn("w:dirty"), "true")
            return e

        r1 = p.add_run()
        r1._element.append(fld("begin"))
        r2 = p.add_run()
        it = OxmlElement("w:instrText")
        it.set(qn("xml:space"), "preserve")
        it.text = f" {instruccion} "
        r2._element.append(it)
        r3 = p.add_run()
        r3._element.append(fld("separate"))
        p.add_run(marcador)
        r5 = p.add_run()
        r5._element.append(fld("end"))

    @staticmethod
    def _sombrear(celda, color: str) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        tcpr = celda._element.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), _hex(color))
        tcpr.append(shd)

    @staticmethod
    def _sombrear_parrafo(p, color: str) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        ppr = p._element.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), _hex(color))
        ppr.append(shd)

    @staticmethod
    def _borde_parrafo(p, lado: str, color: str, grosor: int, espacio: int = 4) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        ppr = p._element.get_or_add_pPr()
        bdr = ppr.find(qn("w:pBdr"))
        if bdr is None:
            bdr = OxmlElement("w:pBdr")
            ppr.append(bdr)
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), str(grosor))
        e.set(qn("w:space"), str(espacio))
        e.set(qn("w:color"), _hex(color))
        bdr.append(e)

    @staticmethod
    def _borde_celda_izq(celda, color: str, grosor: int) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        tcpr = celda._element.get_or_add_tcPr()
        bordes = OxmlElement("w:tcBorders")
        for lado in ("top", "left", "bottom", "right"):
            e = OxmlElement(f"w:{lado}")
            if lado == "left":
                e.set(qn("w:val"), "single")
                e.set(qn("w:sz"), str(grosor))
                e.set(qn("w:color"), _hex(color))
            else:
                e.set(qn("w:val"), "nil")
            bordes.append(e)
        tcpr.append(bordes)

    @staticmethod
    def _margenes_celda(celda, twips: int) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        tcpr = celda._element.get_or_add_tcPr()
        mar = OxmlElement("w:tcMar")
        for lado in ("top", "left", "bottom", "right"):
            e = OxmlElement(f"w:{lado}")
            e.set(qn("w:w"), str(twips))
            e.set(qn("w:type"), "dxa")
            mar.append(e)
        tcpr.append(mar)

    @staticmethod
    def _alto_fila(fila, alto) -> None:
        from docx.enum.table import WD_ROW_HEIGHT_RULE
        fila.height = alto
        fila.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST

    @staticmethod
    def _repetir_encabezado(fila) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        trpr = fila._tr.get_or_add_trPr()
        e = OxmlElement("w:tblHeader")
        e.set(qn("w:val"), "true")
        trpr.append(e)

    @staticmethod
    def _bordes_tabla(tabla, color: str) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        tblpr = tabla._tbl.tblPr
        bordes = OxmlElement("w:tblBorders")
        for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = OxmlElement(f"w:{lado}")
            e.set(qn("w:val"), "single")
            e.set(qn("w:sz"), "4")
            e.set(qn("w:color"), _hex(color))
            bordes.append(e)
        tblpr.append(bordes)

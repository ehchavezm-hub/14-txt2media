"""WorkerConversion: QThread para conversión en segundo plano."""

from __future__ import annotations

from pathlib import Path

try:
    from PySide6.QtCore import QThread, Signal
except ImportError:
    QThread = object
    Signal = None  # type: ignore


class WorkerConversion(QThread):
    progreso = Signal(int, int, str)
    completado = Signal(list)
    error = Signal(str)

    def __init__(
        self,
        archivos: list[Path],
        formato: str,
        carpeta_salida: Path,
        voz: str = "es-PE-CamilaNeural",
        modo: str = "completo",
    ) -> None:
        super().__init__()
        self._archivos = archivos
        self._formato = formato
        self._carpeta_salida = carpeta_salida
        self._voz = voz
        self._modo = modo
        self._cancelar = False

    def cancelar(self) -> None:
        self._cancelar = True

    def run(self) -> None:
        try:
            resultados = self._ejecutar()
            self.completado.emit(resultados)
        except Exception as exc:
            self.error.emit(str(exc))

    def _ejecutar(self) -> list:
        from txt2media.core.orquestador import Orquestador
        from txt2media.generadores.generador_audio import GeneradorAudio
        from txt2media.generadores.generador_video import GeneradorVideo

        if self._formato == "audio" and self._modo == "capitulos":
            return self._audio_capitulos()

        if self._formato == "audio":
            return self._audio_completo()

        if self._formato == "video":
            return self._video()

        _EXT = {"pptx": ".pptx", "docx": ".docx", "xlsx": ".xlsx", "md": ".md", "html": ".html"}
        orq = Orquestador()
        total = len(self._archivos)
        resultados: list[Path] = []

        for i, archivo in enumerate(self._archivos, start=1):
            if self._cancelar:
                break
            self.progreso.emit(i, total, archivo.name)
            try:
                ext = _EXT.get(self._formato, f".{self._formato}")
                salida = self._carpeta_salida / archivo.with_suffix(ext).name
                self._carpeta_salida.mkdir(parents=True, exist_ok=True)
                doc = self._leer(archivo)
                self._generar(doc, salida)
                resultados.append(salida)
            except Exception as exc:
                self.error.emit(f"{archivo.name}: {exc}")

        return [str(r) for r in resultados]

    def _audio_completo(self) -> list:
        from txt2media.generadores.generador_audio import GeneradorAudio

        total = len(self._archivos)
        resultados: list[str] = []
        self._carpeta_salida.mkdir(parents=True, exist_ok=True)
        gen = GeneradorAudio(voz=self._voz)
        for i, archivo in enumerate(self._archivos, start=1):
            if self._cancelar:
                break
            # emitir ANTES: muestra "procesando…" con barra indeterminada
            self.progreso.emit(i - 1, total, f"Sintetizando voz: {archivo.name}…")
            doc = self._leer(archivo)
            salida = self._carpeta_salida / (archivo.stem + ".mp3")
            gen.generar(doc, salida)
            # emitir DESPUÉS: archivo completado
            self.progreso.emit(i, total, archivo.name)
            resultados.append(str(salida))
        return resultados

    def _audio_capitulos(self) -> list:
        from txt2media.generadores.generador_audio import GeneradorAudio

        total = len(self._archivos)
        resultados: list[str] = []
        for i, archivo in enumerate(self._archivos, start=1):
            if self._cancelar:
                break
            self.progreso.emit(i - 1, total, f"Sintetizando capítulos: {archivo.name}…")
            doc = self._leer(archivo)
            sub = self._carpeta_salida / archivo.stem
            gen = GeneradorAudio(voz=self._voz)
            archivos_gen = gen.generar_capitulos(doc, sub)
            self.progreso.emit(i, total, archivo.name)
            resultados.extend(str(a) for a in archivos_gen)
        return resultados

    def _video(self) -> list:
        from txt2media.generadores.generador_video import GeneradorVideo

        total = len(self._archivos)
        resultados: list[str] = []
        self._carpeta_salida.mkdir(parents=True, exist_ok=True)
        gen = GeneradorVideo(voz=self._voz)
        for i, archivo in enumerate(self._archivos, start=1):
            if self._cancelar:
                break
            self.progreso.emit(i - 1, total, f"Generando video: {archivo.name}…")
            doc = self._leer(archivo)
            salida = self._carpeta_salida / (archivo.stem + ".mp4")
            gen.generar(doc, salida)
            self.progreso.emit(i, total, archivo.name)
            resultados.append(str(salida))
        return resultados

    def _leer(self, archivo: Path):
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
        raise ValueError(f"Extensión no soportada: {ext}")

    def _generar(self, doc, salida: Path) -> None:
        fmt = self._formato
        if fmt == "pptx":
            from txt2media.generadores.generador_pptx import GeneradorPPTX
            GeneradorPPTX().generar(doc, salida, {})
        elif fmt == "docx":
            from txt2media.generadores.generador_docx import GeneradorDOCX
            GeneradorDOCX().generar(doc, salida, {})
        elif fmt == "xlsx":
            from txt2media.generadores.generador_xlsx import GeneradorXLSX
            GeneradorXLSX().generar(doc, salida, {})
        elif fmt == "audio":
            from txt2media.generadores.generador_audio import GeneradorAudio
            GeneradorAudio(voz=self._voz).generar(doc, salida)
        elif fmt == "md":
            from txt2media.generadores.generador_md import GeneradorMD
            GeneradorMD().generar(doc, salida, {})
        elif fmt == "html":
            from txt2media.generadores.generador_html import GeneradorHTML
            GeneradorHTML().generar(doc, salida, {})

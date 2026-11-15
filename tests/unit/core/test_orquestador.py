"""Tests del orquestador con stubs."""

import os
from pathlib import Path

import pytest

from txt2media.core.base_generador import BaseGenerador
from txt2media.core.base_lector import BaseLector
from txt2media.core.modelo import Documento, Seccion, Bloque, TipoBloque
from txt2media.core.orquestador import ConfigProceso, Orquestador, ResultadoProceso


# --- Stubs ---

class LectorStub(BaseLector):
    @property
    def formatos_soportados(self) -> list[str]:
        return [".md"]

    def leer(self, ruta: Path) -> Documento:
        return Documento(
            titulo="Documento de Prueba",
            autor="Test",
            origen=ruta,
            formato_origen="md",
            paginas=1,
            secciones=[
                Seccion(nivel=1, titulo="Sección 1", bloques=[
                    Bloque(tipo=TipoBloque.PARRAFO, contenido="Párrafo de prueba")
                ])
            ]
        )


class GeneradorStub(BaseGenerador):
    def __init__(self, formato_out: str = "docx") -> None:
        self._formato = formato_out

    @property
    def formato(self) -> str:
        return self._formato

    def generar(self, doc: Documento, destino: Path, config: dict) -> Path:
        ruta_out = destino / f"{doc.titulo}.{self._formato}"
        ruta_out.write_text("contenido de prueba", encoding="utf-8")
        return ruta_out


class LectorQueFalla(BaseLector):
    @property
    def formatos_soportados(self) -> list[str]:
        return [".err"]

    def leer(self, ruta: Path) -> Documento:
        raise ValueError("Archivo corrupto simulado")


# --- Tests ---


def test_orquestador_llama_lector_y_generador(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CONVDOC_DEV", "1")
    monkeypatch.chdir(tmp_path)

    archivo_md = tmp_path / "doc.md"
    archivo_md.write_text("# Título\n\nContenido", encoding="utf-8")

    orq = Orquestador(lectores=[LectorStub()], generadores=[GeneradorStub("docx")])
    resultados = orq.procesar(
        [archivo_md],
        ConfigProceso(formatos=["docx"], directorio_salida=tmp_path / "salida"),
    )

    assert len(resultados) == 1
    assert resultados[0].exitoso
    assert resultados[0].documento is not None
    assert len(resultados[0].salidas) == 1
    assert resultados[0].salidas[0].exitoso


def test_orquestador_sin_lector_devuelve_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CONVDOC_DEV", "1")
    monkeypatch.chdir(tmp_path)

    archivo = tmp_path / "doc.xyz"
    archivo.write_text("contenido", encoding="utf-8")

    orq = Orquestador(lectores=[LectorStub()], generadores=[])
    resultados = orq.procesar([archivo], ConfigProceso(formatos=["docx"]))

    assert len(resultados) == 1
    assert not resultados[0].exitoso
    assert "lector" in resultados[0].error.lower()


def test_orquestador_error_de_lectura_no_detiene_lote(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CONVDOC_DEV", "1")
    monkeypatch.chdir(tmp_path)

    archivo_err = tmp_path / "roto.err"
    archivo_err.write_text("basura", encoding="utf-8")
    archivo_md = tmp_path / "bueno.md"
    archivo_md.write_text("# OK", encoding="utf-8")

    orq = Orquestador(
        lectores=[LectorQueFalla(), LectorStub()],
        generadores=[GeneradorStub("docx")],
    )
    resultados = orq.procesar(
        [archivo_err, archivo_md],
        ConfigProceso(formatos=["docx"], directorio_salida=tmp_path / "out"),
    )

    assert len(resultados) == 2
    assert not resultados[0].exitoso
    assert resultados[1].exitoso


def test_orquestador_cancelacion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Cancelar durante el proceso detiene el lote antes de completarlo."""
    monkeypatch.setenv("CONVDOC_DEV", "1")
    monkeypatch.chdir(tmp_path)

    archivos = []
    for i in range(5):
        f = tmp_path / f"doc_{i}.md"
        f.write_text(f"# Doc {i}", encoding="utf-8")
        archivos.append(f)

    procesados = []

    class LectorConCancelacion(BaseLector):
        """Cancela después del segundo archivo."""
        @property
        def formatos_soportados(self) -> list[str]:
            return [".md"]

        def leer(self, ruta: Path) -> Documento:
            procesados.append(ruta)
            if len(procesados) >= 2:
                orq.cancelar()
            return LectorStub().leer(ruta)

    orq = Orquestador(
        lectores=[LectorConCancelacion()],
        generadores=[GeneradorStub()],
    )
    resultados = orq.procesar(
        archivos,
        ConfigProceso(formatos=["docx"], directorio_salida=tmp_path / "out"),
    )

    # El orquestador debería procesar menos que los 5 archivos
    assert len(resultados) < 5
    assert orq.esta_cancelado()


def test_orquestador_progreso_callback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CONVDOC_DEV", "1")
    monkeypatch.chdir(tmp_path)

    llamadas: list[tuple[str, int, int]] = []

    def cb(archivo: str, actual: int, total: int) -> None:
        llamadas.append((archivo, actual, total))

    archivos = []
    for i in range(3):
        f = tmp_path / f"d{i}.md"
        f.write_text(f"# {i}", encoding="utf-8")
        archivos.append(f)

    orq = Orquestador(lectores=[LectorStub()], generadores=[GeneradorStub()])
    orq.procesar(
        archivos,
        ConfigProceso(formatos=["docx"], directorio_salida=tmp_path / "out"),
        progreso_cb=cb,
    )

    assert len(llamadas) == 3
    assert llamadas[-1][1] == 3  # actual
    assert llamadas[-1][2] == 3  # total

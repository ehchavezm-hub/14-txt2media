"""Los resultados se guardan junto al documento original salvo que se elija otra carpeta."""

from __future__ import annotations

from pathlib import Path

from txt2media.core.orquestador import Orquestador


def _md(ruta: Path, texto: str = "# Título\n\nTexto.\n") -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")
    return ruta


def test_sin_carpeta_cada_resultado_queda_junto_a_su_original(tmp_path):
    a = _md(tmp_path / "A" / "uno.md")
    b = _md(tmp_path / "B" / "dos.md")
    resultados = Orquestador().procesar([a, b], "md", None)
    assert [r.parent for r in resultados] == [a.parent, b.parent]
    assert all(r.exists() for r in resultados)


def test_con_carpeta_elegida_se_usa_esa(tmp_path):
    a = _md(tmp_path / "A" / "uno.md")
    destino = tmp_path / "salida"
    resultados = Orquestador().procesar([a], "md", destino)
    assert resultados == [destino / "uno.md"]
    assert resultados[0].exists()


def test_cli_sin_salida_guarda_junto_al_original(tmp_path, monkeypatch):
    import sys
    from txt2media.cli import main as cli

    a = _md(tmp_path / "libros" / "uno.md")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["txt2media", "convertir", str(a), "--formato", "html"])
    try:
        cli.main()
    except SystemExit as e:
        assert not e.code
    assert (a.parent / "uno.html").exists()
    assert not (tmp_path / "uno.html").exists()

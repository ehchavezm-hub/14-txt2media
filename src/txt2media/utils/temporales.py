"""Gestión de archivos temporales con escritura atómica y limpieza garantizada."""

import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def escritura_atomica(destino: Path) -> Generator[Path, None, None]:
    """Context manager para escritura atómica: escribe a un temp y renombra al final.

    Uso::

        with escritura_atomica(Path("salida.docx")) as tmp:
            generar_docx(tmp)
        # Si llegamos aquí, destino existe y es válido
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    sufijo = destino.suffix or ".tmp"
    tmp_fd, tmp_str = tempfile.mkstemp(
        suffix=sufijo,
        dir=destino.parent,
        prefix=f".{destino.stem}_tmp_",
    )
    tmp_path = Path(tmp_str)
    try:
        import os
        os.close(tmp_fd)
        yield tmp_path
        tmp_path.replace(destino)
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


@contextmanager
def directorio_temporal() -> Generator[Path, None, None]:
    """Context manager que crea un directorio temporal y lo borra al salir."""
    import shutil

    tmp_dir = Path(tempfile.mkdtemp(prefix="convdoc_"))
    try:
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

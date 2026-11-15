"""Configuración de logging JSON Lines con rotación."""

from __future__ import annotations

import json
import logging
import logging.handlers
from pathlib import Path

from txt2media.utils.rutas import get_datos_dir


def configurar_logging(nivel: int = logging.INFO) -> None:
    directorio = get_datos_dir() / "logs"
    directorio.mkdir(parents=True, exist_ok=True)
    ruta = directorio / "txt2media.log"

    handler = logging.handlers.RotatingFileHandler(
        ruta, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(_JsonLinesFormatter())

    root = logging.getLogger("txt2media")
    root.setLevel(nivel)
    if not root.handlers:
        root.addHandler(handler)


class _JsonLinesFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            entry["exc"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)

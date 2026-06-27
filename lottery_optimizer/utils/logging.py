"""Logging do projeto. Usa rich se disponivel, senao stdlib."""

from __future__ import annotations

import logging


def get_logger(name: str = "lottery_optimizer", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    try:
        from rich.logging import RichHandler

        handler: logging.Handler = RichHandler(rich_tracebacks=True, show_path=False)
        fmt = "%(message)s"
    except Exception:  # pragma: no cover - fallback sem rich
        handler = logging.StreamHandler()
        fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
    logger.propagate = True  # permite captura por caplog; root sem handler nao duplica
    return logger

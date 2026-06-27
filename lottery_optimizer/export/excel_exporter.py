"""Stub do export Excel (openpyxl). Implementacao no Bloco 6."""

from __future__ import annotations

from pathlib import Path

from ..core.portfolio import Portfolio


def export_excel(portfolio: Portfolio, path: str | Path) -> Path:
    raise NotImplementedError("export Excel sera implementado no Bloco 6")

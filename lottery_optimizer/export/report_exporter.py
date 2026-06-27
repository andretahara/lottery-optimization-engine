"""Relatorio textual de carteira. SEMPRE injeta o disclaimer obrigatorio (ADR-005)."""

from __future__ import annotations

from pathlib import Path

from ..core.game import GameSpec
from ..core.portfolio import Portfolio
from ..disclaimer import DISCLAIMER


def build_report(portfolio: Portfolio, spec: GameSpec) -> str:
    """Monta o relatorio em texto. Comeca pelo disclaimer."""
    lines = [
        DISCLAIMER,
        "",
        f"Loteria: {spec.name} ({spec.slug})",
        f"Jogos: {len(portfolio)}",
        "",
    ]
    for i, ticket in enumerate(portfolio, 1):
        lines.append(f"  {i:>3}: {' '.join(f'{n:02d}' for n in ticket.numbers)}")
    return "\n".join(lines)


def export_report(portfolio: Portfolio, spec: GameSpec, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(build_report(portfolio, spec), encoding="utf-8")
    return p

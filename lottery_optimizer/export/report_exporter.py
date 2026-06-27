"""Relatorio textual de carteira. SEMPRE injeta o disclaimer e registra a config de preco usada."""

from __future__ import annotations

from pathlib import Path

from ..core.game import GameSpec
from ..core.portfolio import Portfolio
from ..core.pricing import price_config_summary
from ..disclaimer import DISCLAIMER


def build_report(portfolio: Portfolio, spec: GameSpec) -> str:
    lines = [
        DISCLAIMER,
        "",
        f"Loteria: {spec.name} ({spec.game_id})",
        f"Config de preco: {price_config_summary(spec)}",
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

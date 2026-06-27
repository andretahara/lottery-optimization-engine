"""Export CSV de uma carteira."""

from __future__ import annotations

import csv
from pathlib import Path

from ..core.portfolio import Portfolio


def export_csv(portfolio: Portfolio, path: str | Path) -> Path:
    """Escreve um jogo por linha: ticket, n1, n2, ... Retorna o caminho."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["ticket", "numbers"])
        for i, ticket in enumerate(portfolio, 1):
            writer.writerow([i, " ".join(str(n) for n in ticket.numbers)])
    return p

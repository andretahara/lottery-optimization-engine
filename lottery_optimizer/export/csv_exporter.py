"""Export CSV colunar: uma aposta por linha, dezenas ordenadas, UTF-8."""

from __future__ import annotations

import csv
from pathlib import Path

from ..core.portfolio import Portfolio


def export_csv(portfolio: Portfolio, path, *, game_id: str = "") -> Path:
    """Colunas: jogo_id, aposta_id, tamanho, dezena_01, dezena_02, ... (dezenas ordenadas)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    max_size = max((len(t) for t in portfolio), default=0)
    header = ["jogo_id", "aposta_id", "tamanho"] + [f"dezena_{i:02d}" for i in range(1, max_size + 1)]
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for i, t in enumerate(portfolio, 1):
            nums = list(t.numbers) + [""] * (max_size - len(t))
            w.writerow([game_id, i, len(t), *nums])
    return p


def load_csv(spec, path):
    """Carrega uma carteira de um jogos.csv (inverso de export_csv)."""
    import csv as _csv

    from ..core.portfolio import Portfolio
    from ..core.ticket import Ticket

    tickets = []
    with Path(path).open(encoding="utf-8") as fh:
        reader = _csv.DictReader(fh)
        for row in reader:
            nums = [int(v) for k, v in row.items() if k.startswith("dezena_") and v not in ("", None)]
            tickets.append(Ticket(numbers=tuple(nums)))
    return Portfolio(spec, tickets)

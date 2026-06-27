"""Distancia/diversidade entre jogos da carteira (normalizada em [0, 1])."""

from __future__ import annotations

from ..core.combinations import iter_combinations
from ..core.portfolio import Portfolio


def mean_pairwise_distance(portfolio: Portfolio) -> float:
    """Distancia media par-a-par via distancia de Jaccard: |A^B| / |A v B|.

    0.0 = jogos identicos; 1.0 = totalmente disjuntos. Normalizada para compor o score
    junto das demais metricas. Carteira com < 2 jogos -> 0.0.
    """
    pairs = list(iter_combinations(list(portfolio), 2))
    if not pairs:
        return 0.0
    total = 0.0
    for a, b in pairs:
        sa, sb = set(a.numbers), set(b.numbers)
        union = len(sa | sb)
        inter = len(sa & sb)
        total += (union - inter) / union  # Jaccard distance em [0, 1]
    return total / len(pairs)

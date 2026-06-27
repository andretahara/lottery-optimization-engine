"""Distancia/diversidade entre apostas da carteira."""

from __future__ import annotations

from collections import Counter

from ..core.combinations import iter_combinations
from ..core.portfolio import Portfolio
from ..core.ticket import Ticket


def jaccard_distance(a: Ticket, b: Ticket) -> float:
    """|A^B| / |A v B| em [0,1]. 0 = iguais; 1 = disjuntos."""
    sa, sb = set(a.numbers), set(b.numbers)
    union = len(sa | sb)
    if union == 0:
        return 0.0
    return (union - len(sa & sb)) / union


def mean_pairwise_distance(portfolio: Portfolio) -> float:
    """Distancia de Jaccard media par-a-par. < 2 jogos -> 0.0."""
    pairs = list(iter_combinations(list(portfolio), 2))
    if not pairs:
        return 0.0
    return sum(jaccard_distance(a, b) for a, b in pairs) / len(pairs)


class DistanceMetrics:
    """Sobreposicao e diversidade entre apostas."""

    def __init__(self, spec=None):
        self.spec = spec

    def jaccard_distance(self, a: Ticket, b: Ticket) -> float:
        return jaccard_distance(a, b)

    def mean_pairwise_distance(self, portfolio: Portfolio) -> float:
        return mean_pairwise_distance(portfolio)

    def _overlaps(self, portfolio: Portfolio) -> list[int]:
        return [a.overlap(b) for a, b in iter_combinations(list(portfolio), 2)]

    def mean_intersection(self, portfolio: Portfolio) -> float:
        ov = self._overlaps(portfolio)
        return sum(ov) / len(ov) if ov else 0.0

    def max_intersection(self, portfolio: Portfolio) -> int:
        ov = self._overlaps(portfolio)
        return max(ov) if ov else 0

    def overlap_distribution(self, portfolio: Portfolio) -> dict[int, int]:
        """Quantos pares tem cada tamanho de sobreposicao."""
        return dict(Counter(self._overlaps(portfolio)))

    def similarity_penalty(self, portfolio: Portfolio, threshold: int) -> int:
        """Numero de pares com sobreposicao >= threshold (apostas parecidas)."""
        return sum(1 for ov in self._overlaps(portfolio) if ov >= threshold)

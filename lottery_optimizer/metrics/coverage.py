"""Cobertura de subconjuntos (pares/trincas/...) pela carteira."""

from __future__ import annotations

from ..core.combinations import iter_combinations, k_subsets
from ..core.game import GameSpec
from ..core.portfolio import Portfolio


def covered_subsets(portfolio: Portfolio, size: int) -> set[tuple[int, ...]]:
    """Conjunto de subconjuntos distintos de `size` dezenas cobertos por algum jogo."""
    covered: set[tuple[int, ...]] = set()
    for ticket in portfolio:
        covered.update(k_subsets(ticket.numbers, size))
    return covered


def coverage_ratio(portfolio: Portfolio, spec: GameSpec, size: int) -> float:
    """Fracao dos subconjuntos de `size` dezenas do universo cobertos pela carteira."""
    universe = list(spec.number_universe())
    total = sum(1 for _ in iter_combinations(universe, size))
    if total == 0:
        return 0.0
    return len(covered_subsets(portfolio, size)) / total

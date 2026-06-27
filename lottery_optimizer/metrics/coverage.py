"""Cobertura de subconjuntos pela carteira. Reusa core.CombinationCoverage (modos exact/sampled)."""

from __future__ import annotations

from dataclasses import dataclass

from ..core.combinations import iter_combinations, k_subsets
from ..core.coverage import CombinationCoverage
from ..core.game import GameSpec
from ..core.portfolio import Portfolio


def covered_subsets(portfolio: Portfolio, size: int) -> set[tuple[int, ...]]:
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


@dataclass(frozen=True)
class SubsetCoverage:
    size: int
    unique: int
    raw: int
    redundancy: int       # raw - unique
    unique_raw_ratio: float


class CoverageMetrics:
    """Cobertura unica/bruta/redundancia para subconjuntos de qualquer tamanho."""

    def __init__(self, spec: GameSpec):
        self.spec = spec
        self._cov = CombinationCoverage(spec)

    def at(self, portfolio: Portfolio, size: int, *, mode: str = "exact", **kw) -> SubsetCoverage:
        raw = self._cov.raw_count(portfolio, size)
        unique = self._cov.count_unique(portfolio, size, mode=mode, **kw)
        return SubsetCoverage(
            size=size, unique=unique, raw=raw, redundancy=raw - unique,
            unique_raw_ratio=(unique / raw if raw else 1.0),
        )

    def pairs(self, portfolio: Portfolio, **kw) -> SubsetCoverage:
        return self.at(portfolio, 2, **kw)

    def triples(self, portfolio: Portfolio, **kw) -> SubsetCoverage:
        return self.at(portfolio, 3, **kw)

    def quads(self, portfolio: Portfolio, **kw) -> SubsetCoverage:
        return self.at(portfolio, 4, **kw)

    def main(self, portfolio: Portfolio, *, mode: str = "exact", **kw) -> SubsetCoverage:
        """Cobertura dos K-subsets do premio principal (size == draw_size)."""
        return self.at(portfolio, self.spec.draw_size, mode=mode, **kw)

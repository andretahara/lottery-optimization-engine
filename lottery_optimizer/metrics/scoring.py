"""Score agregado de uma carteira a partir das metricas individuais."""

from __future__ import annotations

from dataclasses import dataclass

from ..core.game import GameSpec
from ..core.portfolio import Portfolio
from .balance import balance_score
from .coverage import coverage_ratio
from .distance import mean_pairwise_distance


@dataclass(frozen=True)
class PortfolioMetrics:
    pair_coverage: float
    triple_coverage: float
    mean_distance: float
    balance: float


def evaluate(portfolio: Portfolio, spec: GameSpec) -> PortfolioMetrics:
    """Calcula o pacote de metricas intra-carteira."""
    return PortfolioMetrics(
        pair_coverage=coverage_ratio(portfolio, spec, 2),
        triple_coverage=coverage_ratio(portfolio, spec, 3),
        mean_distance=mean_pairwise_distance(portfolio),
        balance=balance_score(portfolio, spec),
    )


DEFAULT_WEIGHTS = {"pair_coverage": 0.4, "triple_coverage": 0.3, "mean_distance": 0.2, "balance": 0.1}


def score(portfolio: Portfolio, spec: GameSpec, weights: dict[str, float] | None = None) -> float:
    """Combina as metricas numa nota unica (soma ponderada). Funcao-objetivo dos otimizadores."""
    w = weights or DEFAULT_WEIGHTS
    m = evaluate(portfolio, spec)
    return (
        w.get("pair_coverage", 0) * m.pair_coverage
        + w.get("triple_coverage", 0) * m.triple_coverage
        + w.get("mean_distance", 0) * m.mean_distance
        + w.get("balance", 0) * m.balance
    )

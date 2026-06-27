"""Monta os dados de um relatorio de carteira (reusado por TXT, Excel e graficos)."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction
from typing import Any

from ..core.combinations import n_choose_k
from ..core.game import GameSpec
from ..core.portfolio import Portfolio
from ..core.pricing import price_config_summary
from ..metrics.balance import BalanceMetrics
from ..metrics.coverage import CoverageMetrics
from ..metrics.distance import DistanceMetrics
from ..metrics.frequency import FrequencyMetrics


@dataclass
class ReportData:
    spec: GameSpec
    n_tickets: int
    ticket_sizes: list[int]
    equivalent_simple_total: int
    raw_main: int
    unique_main: int | None
    coverage_mode_used: str
    p_main: Fraction
    frequency: dict[int, int]
    odd_even: dict[str, int]
    low_high: dict[str, int]
    entropy: float
    mean_distance: float
    mean_intersection: float
    max_intersection: int
    pair_cov: Any
    triple_cov: Any
    quad_cov: Any
    budget: Decimal | None = None
    total_cost: Decimal | None = None
    balance_amount: Decimal | None = None
    cost_is_estimate: bool | None = None
    algorithm: str | None = None
    seed: int | None = None
    params: dict[str, Any] = field(default_factory=dict)
    timestamp: str | None = None
    score_history: list[float] = field(default_factory=list)

    @property
    def price_config(self) -> str:
        return price_config_summary(self.spec)


def build_report_data(
    portfolio: Portfolio, spec: GameSpec, *, budget=None, cost_model=None, algorithm=None,
    seed=None, params=None, timestamp=None, score_history=None, coverage_mode="auto",
) -> ReportData:
    cov = CoverageMetrics(spec)
    main = cov.main(portfolio, mode="exact") if coverage_mode != "sampled" else None
    mode_used = "exact"
    if coverage_mode == "auto":
        from ..core.validation import SpecError
        try:
            main = cov.main(portfolio, mode="exact")
        except SpecError:
            main = cov.main(portfolio, mode="sampled")
            mode_used = "sampled"
    elif coverage_mode == "sampled":
        main = cov.main(portfolio, mode="sampled")
        mode_used = "sampled"
    bm = BalanceMetrics(spec)
    dm = DistanceMetrics(spec)
    sizes = portfolio.ticket_sizes()

    total_cost = balance_amount = cost_is_estimate = None
    if cost_model is not None:
        cr = cost_model.portfolio_cost(portfolio)
        total_cost, cost_is_estimate = cr.amount, cr.is_estimate
        if budget is not None:
            balance_amount = budget - cr.amount

    return ReportData(
        spec=spec, n_tickets=len(portfolio), ticket_sizes=sizes,
        equivalent_simple_total=sum(n_choose_k(s, spec.draw_size) for s in sizes),
        raw_main=main.raw, unique_main=main.unique, coverage_mode_used=mode_used,
        p_main=Fraction(main.unique, spec.total_outcomes()),
        frequency=FrequencyMetrics(spec).absolute(portfolio),
        odd_even=bm.odd_even(portfolio), low_high=bm.low_high(portfolio),
        entropy=bm.entropy(portfolio), mean_distance=dm.mean_pairwise_distance(portfolio),
        mean_intersection=dm.mean_intersection(portfolio), max_intersection=dm.max_intersection(portfolio),
        pair_cov=cov.pairs(portfolio), triple_cov=cov.triples(portfolio), quad_cov=cov.quads(portfolio),
        budget=budget, total_cost=total_cost, balance_amount=balance_amount,
        cost_is_estimate=cost_is_estimate, algorithm=algorithm, seed=seed, params=params or {},
        timestamp=timestamp, score_history=list(score_history or []),
    )

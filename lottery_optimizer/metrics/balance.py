"""Balanco: quao uniforme e a frequencia das dezenas na carteira."""

from __future__ import annotations

from statistics import pstdev

from ..core.game import GameSpec
from ..core.portfolio import Portfolio
from .frequency import digit_frequency


def balance_score(portfolio: Portfolio, spec: GameSpec) -> float:
    """1 - (desvio padrao normalizado da frequencia). 1.0 = perfeitamente uniforme.

    Considera TODAS as dezenas do universo (as ausentes contam frequencia 0).
    """
    if len(portfolio) == 0:
        return 1.0
    freq = digit_frequency(portfolio)
    counts = [freq.get(n, 0) for n in spec.number_universe()]
    mean = sum(counts) / len(counts)
    if mean == 0:
        return 1.0
    return max(0.0, 1.0 - pstdev(counts) / mean)

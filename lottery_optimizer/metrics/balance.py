"""Balanco/distribuicao estrutural das dezenas na carteira (intra-carteira)."""

from __future__ import annotations

import math
from collections import Counter

from ..core.game import GameSpec
from ..core.portfolio import Portfolio
from .frequency import digit_frequency


def balance_score(portfolio: Portfolio, spec: GameSpec) -> float:
    """1 - (desvio padrao normalizado da frequencia). 1.0 = uniforme. Conta universo inteiro."""
    if len(portfolio) == 0:
        return 1.0
    from statistics import pstdev

    freq = digit_frequency(portfolio)
    counts = [freq.get(n, 0) for n in spec.number_universe()]
    m = sum(counts) / len(counts)
    if m == 0:
        return 1.0
    return max(0.0, 1.0 - pstdev(counts) / m)


class BalanceMetrics:
    """Distribuicao das dezenas: paridade, baixas/altas, faixas, finais, decadas, entropia."""

    def __init__(self, spec: GameSpec):
        self.spec = spec

    def _all_numbers(self, portfolio: Portfolio) -> list[int]:
        nums: list[int] = []
        for t in portfolio:
            nums.extend(t.numbers)
        return nums

    def odd_even(self, portfolio: Portfolio) -> dict[str, int]:
        nums = self._all_numbers(portfolio)
        odd = sum(1 for n in nums if n % 2)
        return {"odd": odd, "even": len(nums) - odd}

    def low_high(self, portfolio: Portfolio) -> dict[str, int]:
        """Baixas (<= meio do universo) vs altas."""
        mid = (self.spec.universe_min + self.spec.universe_max) // 2
        nums = self._all_numbers(portfolio)
        low = sum(1 for n in nums if n <= mid)
        return {"low": low, "high": len(nums) - low}

    def by_ranges(self, portfolio: Portfolio, ranges: list[tuple[int, int]]) -> dict[str, int]:
        """Contagem por faixas configuraveis [(min,max), ...] (inclusivas)."""
        nums = self._all_numbers(portfolio)
        out: dict[str, int] = {}
        for lo, hi in ranges:
            out[f"{lo}-{hi}"] = sum(1 for n in nums if lo <= n <= hi)
        return out

    def by_endings(self, portfolio: Portfolio) -> dict[int, int]:
        """Contagem por digito final (n % 10)."""
        return dict(Counter(n % 10 for n in self._all_numbers(portfolio)))

    def by_decades(self, portfolio: Portfolio) -> dict[int, int]:
        """Grupos automaticos de 10 a partir de universe_min (decada = (n - min) // 10)."""
        umin = self.spec.universe_min
        return dict(Counter((n - umin) // 10 for n in self._all_numbers(portfolio)))

    def entropy(self, portfolio: Portfolio) -> float:
        """Entropia de Shannon normalizada [0,1] da distribuicao de frequencias.

        1.0 = todas as dezenas igualmente representadas (maxima diversidade); 0 = tudo concentrado.
        """
        freq = digit_frequency(portfolio)
        total = sum(freq.values())
        if total == 0:
            return 0.0
        h = -sum((c / total) * math.log(c / total) for c in freq.values() if c > 0)
        denom = math.log(self.spec.pool)
        return h / denom if denom > 0 else 0.0

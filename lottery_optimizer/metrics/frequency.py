"""Frequencia das dezenas DENTRO da carteira gerada (nunca historico, ADR-004)."""

from __future__ import annotations

from collections import Counter
from statistics import mean, pstdev

from ..core.game import GameSpec
from ..core.portfolio import Portfolio


def digit_frequency(portfolio: Portfolio) -> dict[int, int]:
    """Quantas vezes cada dezena aparece (apenas as presentes)."""
    counter: Counter[int] = Counter()
    for ticket in portfolio:
        counter.update(ticket.numbers)
    return dict(counter)


class FrequencyMetrics:
    """Metricas de frequencia das dezenas, genericas para qualquer GameSpec."""

    def __init__(self, spec: GameSpec):
        self.spec = spec

    def absolute(self, portfolio: Portfolio) -> dict[int, int]:
        """Frequencia absoluta de TODAS as dezenas do universo (ausentes = 0)."""
        freq = digit_frequency(portfolio)
        return {n: freq.get(n, 0) for n in self.spec.number_universe()}

    def total_marks(self, portfolio: Portfolio) -> int:
        return sum(len(t) for t in portfolio)

    def relative(self, portfolio: Portfolio) -> dict[int, float]:
        """Frequencia relativa (fracao do total de marcacoes)."""
        total = self.total_marks(portfolio)
        if total == 0:
            return {n: 0.0 for n in self.spec.number_universe()}
        return {n: c / total for n, c in self.absolute(portfolio).items()}

    def ideal_frequency(self, portfolio: Portfolio) -> float:
        """Frequencia ideal por dezena se a distribuicao fosse perfeitamente uniforme."""
        return self.total_marks(portfolio) / self.spec.pool

    def deviation(self, portfolio: Portfolio) -> dict[int, float]:
        """Desvio de cada dezena em relacao a frequencia ideal."""
        ideal = self.ideal_frequency(portfolio)
        return {n: c - ideal for n, c in self.absolute(portfolio).items()}

    def most_used(self, portfolio: Portfolio) -> tuple[int, int]:
        """(dezena, contagem) mais usada (menor dezena em caso de empate)."""
        counts = self.absolute(portfolio)
        return max(counts.items(), key=lambda kv: (kv[1], -kv[0]))

    def least_used(self, portfolio: Portfolio) -> tuple[int, int]:
        """(dezena, contagem) menos usada (menor dezena em caso de empate)."""
        counts = self.absolute(portfolio)
        return min(counts.items(), key=lambda kv: (kv[1], kv[0]))

    def coefficient_of_variation(self, portfolio: Portfolio) -> float:
        """Desvio padrao / media das frequencias. 0 = perfeitamente uniforme."""
        counts = list(self.absolute(portfolio).values())
        m = mean(counts)
        if m == 0:
            return 0.0
        return pstdev(counts) / m

"""Probabilidade de loteria (docs/MATH_MODEL.md). Otimizacao mexe em COBERTURA, nunca em
probabilidade individual. Regra do premio principal: K-subsets UNICOS cobertos / C(N, K).
"""

from __future__ import annotations

from fractions import Fraction

from .combinations import n_choose_k
from .coverage import CombinationCoverage
from .game import GameSpec
from .portfolio import Portfolio


# --- funcoes puras (sem carteira) ---
def total_outcomes(pool: int, draw_size: int) -> int:
    """C(N, K)."""
    return n_choose_k(pool, draw_size)


def equivalent_simple_games(ticket_size: int, draw_size: int) -> int:
    """C(T, K)."""
    return n_choose_k(ticket_size, draw_size)


def p_main_simple(pool: int, draw_size: int) -> Fraction:
    """1 / C(N, K)."""
    return Fraction(1, total_outcomes(pool, draw_size))


def p_exact_hits(pool: int, draw_size: int, ticket_size: int, hits: int) -> Fraction:
    """Hipergeometrica: C(T,h)*C(N-T,K-h)/C(N,K) para uma aposta de `ticket_size`."""
    if not (0 <= hits <= min(ticket_size, draw_size)):
        return Fraction(0, 1)
    fav = n_choose_k(ticket_size, hits) * n_choose_k(pool - ticket_size, draw_size - hits)
    return Fraction(fav, total_outcomes(pool, draw_size))


class ProbabilityModel:
    """Probabilidades ligadas a uma GameSpec e, quando aplicavel, a uma carteira."""

    def __init__(self, spec: GameSpec):
        self.spec = spec
        self._cov = CombinationCoverage(spec)

    def total_combinations(self) -> int:
        """C(N, K)."""
        return self.spec.total_outcomes()

    def equivalent_simple(self, ticket_size: int) -> int:
        """C(T, K)."""
        return n_choose_k(ticket_size, self.spec.draw_size)

    def raw_coverage(self, portfolio: Portfolio) -> int:
        """Cobertura BRUTA do premio principal: soma de C(T_i, K) (com repeticao)."""
        return self._cov.raw_count(portfolio, self.spec.draw_size)

    def unique_coverage(self, portfolio: Portfolio, *, mode: str = "exact", **kw) -> int:
        """Cobertura UNICA do premio principal: K-subsets distintos cobertos."""
        return self._cov.count_unique(portfolio, self.spec.draw_size, mode=mode, **kw)

    def p_main(self, portfolio: Portfolio, *, mode: str = "exact", **kw) -> Fraction:
        """Probabilidade teorica do premio principal = K-subsets UNICOS / C(N, K)."""
        unique = self.unique_coverage(portfolio, mode=mode, **kw)
        return Fraction(unique, self.total_combinations())

    def p_tier_single(self, ticket_size: int, hits: int) -> Fraction:
        """Probabilidade de exatamente `hits` acertos numa aposta de `ticket_size` (faixa inferior)."""
        return p_exact_hits(self.spec.pool, self.spec.draw_size, ticket_size, hits)

    def p_tier_portfolio_approx(self, portfolio: Portfolio, hits: int) -> Fraction:
        """Aproximacao (cota de Boole) de >= um jogo com exatamente `hits` acertos.

        Soma das probabilidades por jogo, limitada a 1. Aproximada: ignora correlacao/
        sobreposicao entre jogos. Use como cota superior, nao valor exato.
        """
        total = sum(
            (self.p_tier_single(size, hits) for size in portfolio.ticket_sizes()),
            Fraction(0, 1),
        )
        return min(total, Fraction(1, 1))

"""CombinationCoverage: subconjuntos cobertos por apostas (pares, trincas, quadras, K-subsets).

Tres modos para nao explodir memoria em jogos grandes:
- exact:    constroi o conjunto de subconjuntos unicos (com trava de seguranca).
- streaming: gera subconjuntos preguicosamente (itertools), util pra consumir sem materializar.
- sampled:  estimativa Monte Carlo da fracao do espaco coberta (para K-subsets enormes).
"""

from __future__ import annotations

from typing import Iterator

from .combinations import k_subsets, n_choose_k
from .game import GameSpec
from .portfolio import Portfolio
from .ticket import Ticket
from .validation import SpecError

# Trava: acima disso o modo exact recusa, sugerindo sampled (evita estouro de memoria).
DEFAULT_EXACT_CAP = 5_000_000


class CombinationCoverage:
    def __init__(self, spec: GameSpec):
        self.spec = spec

    # ---- streaming ----
    def iter_ticket_subsets(self, ticket: Ticket, size: int) -> Iterator[tuple[int, ...]]:
        """Gera (preguicosamente) os subconjuntos de `size` dezenas de um jogo."""
        if size < 1:
            raise SpecError("size deve ser >= 1")
        return k_subsets(ticket.numbers, size)

    def iter_all_subsets(self, portfolio: Portfolio, size: int) -> Iterator[tuple[int, ...]]:
        """Streaming de todos os subconjuntos da carteira (com multiplicidade)."""
        for ticket in portfolio:
            yield from self.iter_ticket_subsets(ticket, size)

    # ---- contagem bruta vs unica ----
    def raw_count(self, portfolio: Portfolio, size: int) -> int:
        """Cobertura BRUTA: soma de C(T_i, size) (conta repeticoes entre jogos)."""
        return sum(n_choose_k(t_size, size) for t_size in portfolio.ticket_sizes())

    def _expected_cells(self, portfolio: Portfolio, size: int) -> int:
        return self.raw_count(portfolio, size)

    def unique_subsets(
        self, portfolio: Portfolio, size: int, *, allow_large: bool = False
    ) -> set[tuple[int, ...]]:
        """Conjunto EXATO de subconjuntos distintos cobertos. Recusa se exceder a trava."""
        if not allow_large and self._expected_cells(portfolio, size) > DEFAULT_EXACT_CAP:
            raise SpecError(
                f"cobertura exata de {size}-subsets excede a trava ({DEFAULT_EXACT_CAP}); "
                "use mode='sampled' ou allow_large=True"
            )
        covered: set[tuple[int, ...]] = set()
        for ticket in portfolio:
            covered.update(self.iter_ticket_subsets(ticket, size))
        return covered

    def count_unique(
        self,
        portfolio: Portfolio,
        size: int,
        *,
        mode: str = "exact",
        samples: int = 100_000,
        rng=None,
        allow_large: bool = False,
    ) -> int:
        """Contagem de subconjuntos distintos cobertos.

        mode='exact'   -> len do conjunto unico (trava de memoria).
        mode='sampled' -> estima via fracao Monte Carlo * total do espaco C(N, size).
        """
        if mode == "exact":
            return len(self.unique_subsets(portfolio, size, allow_large=allow_large))
        if mode == "sampled":
            frac = self.estimate_coverage_fraction(portfolio, size, samples=samples, rng=rng)
            universe = list(self.spec.number_universe())
            total = n_choose_k(len(universe), size)
            return round(frac * total)
        raise SpecError(f"mode desconhecido: {mode!r} (use exact|sampled)")

    # ---- estimativa Monte Carlo ----
    def estimate_coverage_fraction(
        self, portfolio: Portfolio, size: int, *, samples: int = 100_000, rng=None
    ) -> float:
        """Fracao estimada de TODOS os `size`-subsets do universo cobertos pela carteira.

        Amostra subconjuntos aleatorios do universo e mede quantos estao contidos em algum
        jogo. Para `size == draw_size`, e a estimativa da cobertura do premio principal.
        """
        from ..utils.random import SeededRng

        if rng is None:
            rng = SeededRng(12345)
        universe = list(self.spec.number_universe())
        ticket_sets = [frozenset(t.numbers) for t in portfolio]
        if not ticket_sets:
            return 0.0
        hits = 0
        for _ in range(samples):
            subset = frozenset(rng.sample(universe, size))
            if any(subset <= ts for ts in ticket_sets):
                hits += 1
        return hits / samples

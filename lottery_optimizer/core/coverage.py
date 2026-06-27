"""CombinationCoverage: subconjuntos cobertos por apostas (pares, trincas, quadras, K-subsets).

Modos para nao explodir memoria:
- exact:    conjunto de subconjuntos unicos (com trava de seguranca `exact_cap`).
- streaming: gera subconjuntos preguicosamente (itertools).
- sampled:  estimativa Monte Carlo da fracao do espaco coberta (K-subsets enormes).

A troca de exato para estimado NUNCA e silenciosa: emite log (ADR-031).
"""

from __future__ import annotations

from typing import Iterator

from ..utils.logging import get_logger
from .combinations import k_subsets, n_choose_k
from .game import GameSpec
from .portfolio import Portfolio
from .ticket import Ticket
from .validation import SpecError

DEFAULT_EXACT_CAP = 5_000_000
CONSERVATIVE_EXACT_CAP = 100_000

_log = get_logger("lottery_optimizer.coverage")


class CombinationCoverage:
    def __init__(self, spec: GameSpec, exact_cap: int = DEFAULT_EXACT_CAP):
        self.spec = spec
        self.exact_cap = exact_cap

    # ---- streaming ----
    def iter_ticket_subsets(self, ticket: Ticket, size: int) -> Iterator[tuple[int, ...]]:
        if size < 1:
            raise SpecError("size deve ser >= 1")
        return k_subsets(ticket.numbers, size)

    def iter_all_subsets(self, portfolio: Portfolio, size: int) -> Iterator[tuple[int, ...]]:
        for ticket in portfolio:
            yield from self.iter_ticket_subsets(ticket, size)

    # ---- contagem ----
    def raw_count(self, portfolio: Portfolio, size: int) -> int:
        return sum(n_choose_k(t_size, size) for t_size in portfolio.ticket_sizes())

    def unique_subsets(
        self, portfolio: Portfolio, size: int, *, allow_large: bool = False
    ) -> set[tuple[int, ...]]:
        if not allow_large and self.raw_count(portfolio, size) > self.exact_cap:
            raise SpecError(
                f"cobertura exata de {size}-subsets excede a trava ({self.exact_cap}); "
                "use mode='sampled' ou allow_large=True"
            )
        covered: set[tuple[int, ...]] = set()
        for ticket in portfolio:
            covered.update(self.iter_ticket_subsets(ticket, size))
        return covered

    def count_unique(
        self, portfolio: Portfolio, size: int, *, mode: str = "exact",
        samples: int = 100_000, rng=None, allow_large: bool = False,
    ) -> int:
        if mode == "exact":
            return len(self.unique_subsets(portfolio, size, allow_large=allow_large))
        if mode == "sampled":
            _log.info("cobertura de %d-subsets ESTIMADA (amostral, %d amostras)", size, samples)
            frac = self.estimate_coverage_fraction(portfolio, size, samples=samples, rng=rng)
            total = n_choose_k(self.spec.pool, size)
            return round(frac * total)
        raise SpecError(f"mode desconhecido: {mode!r} (use exact|sampled)")

    def count_unique_auto(self, portfolio: Portfolio, size: int, *, samples=100_000, rng=None) -> int:
        """Exato se couber na trava; senao cai para estimado COM LOG (nunca silencioso)."""
        if self.raw_count(portfolio, size) <= self.exact_cap:
            return self.count_unique(portfolio, size, mode="exact")
        _log.warning(
            "cobertura exata de %d-subsets excede a trava (%d): caindo para ESTIMATIVA amostral",
            size, self.exact_cap,
        )
        return self.count_unique(portfolio, size, mode="sampled", samples=samples, rng=rng)

    # ---- Monte Carlo ----
    def estimate_coverage_fraction(
        self, portfolio: Portfolio, size: int, *, samples: int = 100_000, rng=None
    ) -> float:
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

"""HybridInitialGenerator: combina geradores (cobertura + diversidade + balanceado)."""

from __future__ import annotations

from ..core.portfolio import Portfolio
from ..core.ticket import Ticket
from .balanced_random import BalancedRandomGenerator
from .base import BaseGenerator
from .diversity import DiversityGenerator
from .greedy_coverage import GreedyCoverageGenerator


class HybridInitialGenerator(BaseGenerator):
    name = "hybrid_initial"

    def _build(self, spec, sizes, constraints, rng) -> Portfolio:
        # divide o orcamento entre 3 estrategias; combina e deduplica preservando a ordem.
        n = len(sizes)
        thirds = [sizes[: n // 3], sizes[n // 3 : 2 * n // 3], sizes[2 * n // 3 :]]
        gens = [GreedyCoverageGenerator(), DiversityGenerator(), BalancedRandomGenerator()]
        seen: set[tuple[int, ...]] = set()
        tickets: list[Ticket] = []
        for gen, part in zip(gens, thirds):
            if not part:
                continue
            sub = gen._build(spec, part, constraints, rng)
            for t in sub:
                if constraints.allow_duplicates or t.numbers not in seen:
                    seen.add(t.numbers)
                    tickets.append(t)
        # completa eventuais faltas (duplicatas descartadas) com aleatorio
        idx = len(tickets)
        while len(tickets) < n:
            pick = self._sample_unique(spec, sizes[idx], rng, seen)
            if pick is None:
                break
            seen.add(pick)
            tickets.append(Ticket(numbers=pick))
            idx += 1
        return Portfolio(spec, tickets[:n], allow_duplicates=constraints.allow_duplicates)

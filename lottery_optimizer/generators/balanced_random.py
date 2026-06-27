"""BalancedRandomGenerator: equilibra a frequencia das dezenas na carteira (simetrico, ADR-022)."""

from __future__ import annotations

from ..core.portfolio import Portfolio
from ..core.ticket import Ticket
from ..core.validation import SpecError
from .base import BaseGenerator


class BalancedRandomGenerator(BaseGenerator):
    name = "balanced_random"

    def _build(self, spec, sizes, constraints, rng) -> Portfolio:
        universe = list(spec.number_universe())
        counts = {n: 0 for n in universe}
        seen: set[tuple[int, ...]] = set()
        tickets = []
        for size in sizes:
            pick = None
            for _ in range(200):
                order = rng.shuffle(universe)
                order.sort(key=lambda n: counts[n])  # menos usadas primeiro, desempate aleatorio
                cand = tuple(sorted(order[:size]))
                if constraints.allow_duplicates or cand not in seen:
                    pick = cand
                    break
            if pick is None:
                raise SpecError("nao foi possivel gerar aposta balanceada distinta")
            seen.add(pick)
            tickets.append(Ticket(numbers=pick))
            for n in pick:
                counts[n] += 1
        return Portfolio(spec, tickets, allow_duplicates=constraints.allow_duplicates)

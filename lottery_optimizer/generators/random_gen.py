"""RandomGenerator: apostas uniformemente aleatorias, validas, sem duplicatas."""

from __future__ import annotations

from ..core.portfolio import Portfolio
from ..core.ticket import Ticket
from ..core.validation import SpecError
from .base import BaseGenerator


class RandomGenerator(BaseGenerator):
    name = "random"

    def _build(self, spec, sizes, constraints, rng) -> Portfolio:
        seen: set[tuple[int, ...]] = set()
        tickets = []
        for size in sizes:
            pick = self._sample_unique(spec, size, rng, seen if not constraints.allow_duplicates else set())
            if pick is None:
                raise SpecError("nao foi possivel amostrar aposta distinta (espaco esgotado?)")
            seen.add(pick)
            tickets.append(Ticket(numbers=pick))
        return Portfolio(spec, tickets, allow_duplicates=constraints.allow_duplicates)

"""GreedyCoverageGenerator: escolhe apostas que mais aumentam a cobertura de subconjuntos.

A cada slot gera um pool de candidatos aleatorios e escolhe o que adiciona mais PARES novos
(desempate por trincas novas). Bounded por candidato -> nao explode memoria. Reprodutivel.
"""

from __future__ import annotations

from ..core.combinations import k_subsets
from ..core.portfolio import Portfolio
from ..core.ticket import Ticket
from ..core.validation import SpecError
from .base import BaseGenerator

_CANDIDATES = 40


class GreedyCoverageGenerator(BaseGenerator):
    name = "greedy_coverage"

    def _build(self, spec, sizes, constraints, rng) -> Portfolio:
        seen: set[tuple[int, ...]] = set()
        covered_pairs: set[tuple[int, ...]] = set()
        covered_triples: set[tuple[int, ...]] = set()
        tickets = []
        for size in sizes:
            best = None
            best_gain = (-1, -1)
            for _ in range(_CANDIDATES):
                cand = self._sample_unique(spec, size, rng, seen)
                if cand is None:
                    continue
                pairs = set(k_subsets(cand, 2))
                triples = set(k_subsets(cand, 3)) if size >= 3 else set()
                gain = (len(pairs - covered_pairs), len(triples - covered_triples))
                if gain > best_gain:
                    best_gain, best = gain, cand
            if best is None:
                raise SpecError("nao foi possivel gerar candidato distinto")
            seen.add(best)
            covered_pairs |= set(k_subsets(best, 2))
            if size >= 3:
                covered_triples |= set(k_subsets(best, 3))
            tickets.append(Ticket(numbers=best))
        return Portfolio(spec, tickets, allow_duplicates=constraints.allow_duplicates)

"""DiversityGenerator: maximiza distancia media e reduz sobreposicao entre apostas.

A cada slot escolhe, dentre candidatos aleatorios, o de MENOR sobreposicao maxima com a
carteira ja montada (maior distancia de Jaccard minima). Reprodutivel, bounded.
"""

from __future__ import annotations

from ..core.portfolio import Portfolio
from ..core.ticket import Ticket
from ..core.validation import SpecError
from ..metrics.distance import jaccard_distance
from .base import BaseGenerator

_CANDIDATES = 40


class DiversityGenerator(BaseGenerator):
    name = "diversity"

    def _build(self, spec, sizes, constraints, rng) -> Portfolio:
        seen: set[tuple[int, ...]] = set()
        tickets: list[Ticket] = []
        for size in sizes:
            best = None
            best_score = -1.0
            for _ in range(_CANDIDATES):
                cand = self._sample_unique(spec, size, rng, seen)
                if cand is None:
                    continue
                ct = Ticket(numbers=cand)
                if not tickets:
                    best = cand
                    break
                # distancia minima aos jogos existentes (queremos maximiza-la)
                min_dist = min(jaccard_distance(ct, t) for t in tickets)
                if min_dist > best_score:
                    best_score, best = min_dist, cand
            if best is None:
                raise SpecError("nao foi possivel gerar candidato distinto")
            seen.add(best)
            tickets.append(Ticket(numbers=best))
        return Portfolio(spec, tickets, allow_duplicates=constraints.allow_duplicates)

"""GeneticOptimizer: populacao de carteiras, selecao por score, crossover, mutacao, elitismo."""

from __future__ import annotations

from ..core.portfolio import Portfolio
from ..core.ticket import Ticket
from ..utils.random import SeededRng
from .base import BaseOptimizer, OptimizationResult, RuntimeConfig, make_scorer, random_neighbor


class GeneticOptimizer(BaseOptimizer):
    name = "genetic"

    def optimize(self, initial_portfolio, game_spec, budget, score_config, runtime_config, seed):
        rc: RuntimeConfig = runtime_config
        scorer = make_scorer(score_config, game_spec, rc.coverage_mode, rc.max_memory_mode)
        rng = SeededRng(seed)
        start = self._now()
        n = len(initial_portfolio)
        initial_score = scorer(initial_portfolio)

        # populacao inicial: a carteira dada + variantes mutadas
        pop = [initial_portfolio]
        while len(pop) < rc.population:
            v = initial_portfolio
            for _ in range(3):
                v = random_neighbor(game_spec, v, rng) or v
            pop.append(v)

        history = [initial_score]
        best, best_score = initial_portfolio, initial_score
        accepted = 0

        for _ in range(rc.generations):
            scored = sorted(pop, key=scorer, reverse=True)
            if scorer(scored[0]) > best_score:
                best, best_score = scored[0], scorer(scored[0])
                accepted += 1
            elite = scored[: max(1, rc.elite)]
            new_pop = list(elite)
            while len(new_pop) < rc.population:
                pa = self._tournament(scored, rng, scorer)
                pb = self._tournament(scored, rng, scorer)
                child = self._crossover(game_spec, pa, pb, n, rng)
                if rng.random() < rc.mutation_rate:
                    child = random_neighbor(game_spec, child, rng) or child
                new_pop.append(child)
            pop = new_pop
            history.append(best_score)

        return OptimizationResult(
            best_portfolio=best, best_score=best_score, initial_score=initial_score,
            improvement=best_score - initial_score, iterations=rc.generations,
            elapsed_seconds=self._now() - start, score_history=history,
            accepted_moves=accepted, rejected_moves=rc.generations - accepted,
            logs=[f"genetic: pop={rc.population}, gen={rc.generations}, best={best_score:.4f}"],
        )

    def _tournament(self, scored, rng, scorer, k=3):
        cands = [rng.choice(scored) for _ in range(k)]
        return max(cands, key=scorer)

    def _crossover(self, spec, pa: Portfolio, pb: Portfolio, n: int, rng) -> Portfolio:
        """Combina apostas dos pais, deduplica, completa com aleatorio ate `n`."""
        pool = list(pa) + list(pb)
        pool = rng.shuffle(pool)
        seen: set[tuple[int, ...]] = set()
        kids = []
        for t in pool:
            if t.numbers not in seen:
                seen.add(t.numbers)
                kids.append(t)
            if len(kids) == n:
                break
        universe = list(spec.number_universe())
        size = len(list(pa)[0])
        while len(kids) < n:
            cand = tuple(sorted(rng.sample(universe, size)))
            if cand not in seen:
                seen.add(cand)
                kids.append(Ticket(numbers=cand))
        return Portfolio(spec, kids)

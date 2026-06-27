"""GRASPOptimizer: construcao gulosa randomizada + busca local; varias rodadas, pega a melhor."""

from __future__ import annotations

from ..generators.base import GenerationConstraints
from ..generators.greedy_coverage import GreedyCoverageGenerator
from .base import BaseOptimizer, OptimizationResult, RuntimeConfig, make_scorer
from .local_search import LocalSearchOptimizer


class GRASPOptimizer(BaseOptimizer):
    name = "grasp"

    def optimize(self, initial_portfolio, game_spec, budget, score_config, runtime_config, seed):
        rc: RuntimeConfig = runtime_config
        scorer = make_scorer(score_config, game_spec, rc.coverage_mode)
        start = self._now()
        initial_score = scorer(initial_portfolio)
        n = len(initial_portfolio)
        size = len(list(initial_portfolio)[0])
        constraints = GenerationConstraints(strategy="fixed", ticket_size=size)
        ls = LocalSearchOptimizer()

        best, best_score = initial_portfolio, initial_score
        total_iter = 0
        history = [initial_score]
        for r in range(max(1, rc.grasp_rounds)):
            # construcao gulosa randomizada (seed por rodada -> reprodutivel)
            built = GreedyCoverageGenerator().generate(game_spec, n, constraints, seed + r + 1)
            local_rc = RuntimeConfig(max_iterations=rc.max_iterations // max(1, rc.grasp_rounds),
                                     restarts=1, coverage_mode=rc.coverage_mode)
            res = ls.optimize(built, game_spec, budget, score_config, local_rc, seed + r + 1)
            total_iter += res.iterations
            history.extend(res.score_history)
            if res.best_score > best_score:
                best, best_score = res.best_portfolio, res.best_score

        return OptimizationResult(
            best_portfolio=best, best_score=best_score, initial_score=initial_score,
            improvement=best_score - initial_score, iterations=total_iter,
            elapsed_seconds=self._now() - start, score_history=history,
            logs=[f"grasp: {rc.grasp_rounds} rodadas, best={best_score:.4f}"],
        )

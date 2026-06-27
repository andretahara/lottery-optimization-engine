"""LocalSearchOptimizer: hill-climbing (aceita so melhorias) com multiplos reinicios."""

from __future__ import annotations

from ..utils.random import SeededRng
from .base import (
    BaseOptimizer,
    OptimizationResult,
    RuntimeConfig,
    make_scorer,
    neighbor_replace_worst,
    neighbor_swap_number,
    neighbor_swap_ticket,
)


class LocalSearchOptimizer(BaseOptimizer):
    name = "local_search"

    def optimize(self, initial_portfolio, game_spec, budget, score_config, runtime_config, seed):
        rc: RuntimeConfig = runtime_config
        scorer = make_scorer(score_config, game_spec, rc.coverage_mode, rc.max_memory_mode)
        rng = SeededRng(seed)
        start = self._now()
        initial_score = scorer(initial_portfolio)
        best, best_score = initial_portfolio, initial_score
        history = [initial_score]
        accepted = rejected = iterations = 0

        for restart in range(max(1, rc.restarts)):
            current = best if restart == 0 else (
                neighbor_swap_ticket(game_spec, best, rng) or best
            )
            cur_score = scorer(current)
            no_improve = 0
            while iterations < rc.max_iterations and no_improve < 30:
                iterations += 1
                moves = [
                    neighbor_swap_number(game_spec, current, rng),
                    neighbor_swap_ticket(game_spec, current, rng),
                    neighbor_replace_worst(game_spec, current, rng, scorer),
                ]
                cand = max(
                    (m for m in moves if m is not None), key=scorer, default=None
                )
                if cand is not None and scorer(cand) > cur_score:
                    current, cur_score = cand, scorer(cand)
                    accepted += 1
                    no_improve = 0
                    if cur_score > best_score:
                        best, best_score = current, cur_score
                else:
                    rejected += 1
                    no_improve += 1
                history.append(best_score)
                if rc.runtime_seconds and self._now() - start > rc.runtime_seconds:
                    break

        return OptimizationResult(
            best_portfolio=best, best_score=best_score, initial_score=initial_score,
            improvement=best_score - initial_score, iterations=iterations,
            elapsed_seconds=self._now() - start, score_history=history,
            accepted_moves=accepted, rejected_moves=rejected,
            logs=[f"local_search: {accepted} aceitos, {rejected} rejeitados, {iterations} iter"],
        )

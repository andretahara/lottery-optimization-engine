"""SimulatedAnnealingOptimizer: aceita pioras com prob exp(delta/T); cooling; checkpoint periodico."""

from __future__ import annotations

import math

from ..utils.checkpoint import save_checkpoint
from ..utils.random import SeededRng
from .base import BaseOptimizer, OptimizationResult, RuntimeConfig, make_scorer, random_neighbor


class SimulatedAnnealingOptimizer(BaseOptimizer):
    name = "simulated_annealing"

    def optimize(self, initial_portfolio, game_spec, budget, score_config, runtime_config, seed):
        rc: RuntimeConfig = runtime_config
        scorer = make_scorer(score_config, game_spec, rc.coverage_mode, rc.max_memory_mode)
        rng = SeededRng(seed)
        start = self._now()
        initial_score = scorer(initial_portfolio)
        current, cur_score = initial_portfolio, initial_score
        best, best_score = current, cur_score
        history = [initial_score]
        accepted = rejected = 0
        temp = max(rc.temp_initial, 1e-9)
        ckpt_path = None

        for it in range(1, rc.max_iterations + 1):
            cand = random_neighbor(game_spec, current, rng)
            if cand is not None:
                cs = scorer(cand)
                delta = cs - cur_score
                # exp(delta/T) limitado para evitar overflow; aceita melhora sempre
                accept = delta >= 0 or rng.random() < math.exp(min(0.0, delta) / temp)
                if accept:
                    current, cur_score = cand, cs
                    accepted += 1
                    if cs > best_score:
                        best, best_score = cand, cs
                else:
                    rejected += 1
            history.append(best_score)
            temp *= rc.cooling
            if rc.checkpoint_path and it % rc.checkpoint_every == 0:
                ckpt_path = str(save_checkpoint(
                    {"iter": it, "best_score": best_score,
                     "best": [list(t.numbers) for t in best]},
                    rc.checkpoint_path,
                ))
            if rc.runtime_seconds and self._now() - start > rc.runtime_seconds:
                break

        return OptimizationResult(
            best_portfolio=best, best_score=best_score, initial_score=initial_score,
            improvement=best_score - initial_score, iterations=len(history) - 1,
            elapsed_seconds=self._now() - start, score_history=history,
            accepted_moves=accepted, rejected_moves=rejected, checkpoint_path=ckpt_path,
            logs=[f"SA: temp_final={temp:.4g}, {accepted} aceitos, {rejected} rejeitados"],
        )

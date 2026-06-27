"""HybridOptimizer: GRASP -> refino com Simulated Annealing -> finaliza com Local Search."""

from __future__ import annotations

from .base import BaseOptimizer, OptimizationResult, RuntimeConfig, make_scorer
from .grasp import GRASPOptimizer
from .local_search import LocalSearchOptimizer
from .simulated_annealing import SimulatedAnnealingOptimizer


class HybridOptimizer(BaseOptimizer):
    name = "hybrid"

    def optimize(self, initial_portfolio, game_spec, budget, score_config, runtime_config, seed):
        rc: RuntimeConfig = runtime_config
        scorer = make_scorer(score_config, game_spec, rc.coverage_mode, rc.max_memory_mode)
        start = self._now()
        initial_score = scorer(initial_portfolio)
        third = max(20, rc.max_iterations // 3)

        g = GRASPOptimizer().optimize(
            initial_portfolio, game_spec, budget, score_config,
            RuntimeConfig(max_iterations=third, grasp_rounds=rc.grasp_rounds,
                          coverage_mode=rc.coverage_mode, max_memory_mode=rc.max_memory_mode), seed)
        sa = SimulatedAnnealingOptimizer().optimize(
            g.best_portfolio, game_spec, budget, score_config,
            RuntimeConfig(max_iterations=third, temp_initial=rc.temp_initial, cooling=rc.cooling,
                          coverage_mode=rc.coverage_mode, max_memory_mode=rc.max_memory_mode), seed + 1)
        ls = LocalSearchOptimizer().optimize(
            sa.best_portfolio, game_spec, budget, score_config,
            RuntimeConfig(max_iterations=third, restarts=2, coverage_mode=rc.coverage_mode, max_memory_mode=rc.max_memory_mode), seed + 2)

        stages = [g, sa, ls]
        best = max(stages, key=lambda r: r.best_score)
        history = g.score_history + sa.score_history + ls.score_history
        return OptimizationResult(
            best_portfolio=best.best_portfolio, best_score=best.best_score,
            initial_score=initial_score, improvement=best.best_score - initial_score,
            iterations=sum(s.iterations for s in stages),
            elapsed_seconds=self._now() - start, score_history=history,
            accepted_moves=sum(s.accepted_moves for s in stages),
            rejected_moves=sum(s.rejected_moves for s in stages),
            logs=["hybrid: GRASP -> SA -> LocalSearch",
                  f"scores: grasp={g.best_score:.4f} sa={sa.best_score:.4f} ls={ls.best_score:.4f}"],
        )

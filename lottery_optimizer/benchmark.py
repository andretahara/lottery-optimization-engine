"""Benchmark justo de geradores e otimizadores: mesma seed, orcamento e GameSpec.

Nao escolhe vencedor so pelo score: descarta carteiras invalidas (orcamento violado,
duplicatas, dezena fora do universo, tamanho invalido). Versao base; o bloco de Benchmark
adiciona exports ricos (xlsx/png/report).
"""

from __future__ import annotations

import csv
import time
from pathlib import Path

from .algorithms import OPTIMIZERS, RuntimeConfig
from .core.game import GameSpec
from .generators import GENERATORS, GenerationConstraints
from .metrics.coverage import CoverageMetrics
from .metrics.scoring import PortfolioScore

_SIMPLE = GenerationConstraints(strategy="all_simple")


def _is_valid(portfolio, spec: GameSpec, budget: int) -> bool:
    if len(portfolio) != budget:
        return False
    if len({t.numbers for t in portfolio}) != len(portfolio):
        return False
    for t in portfolio:
        if len(t) not in spec.allowed_ticket_sizes:
            return False
        if not all(spec.contains(n) for n in t.numbers):
            return False
    return True


def _run_one(spec, budget, algo, seed, iterations, runtime_seconds):
    ps = PortfolioScore()
    t0 = time.perf_counter()
    if algo in GENERATORS:
        p = GENERATORS[algo]().generate(spec, budget, _SIMPLE, seed)
        initial_score = best_score = ps.score(p, spec)
        best = p
    elif algo in OPTIMIZERS:
        initial = GENERATORS["hybrid_initial"]().generate(spec, budget, _SIMPLE, seed)
        rc = RuntimeConfig(max_iterations=iterations, runtime_seconds=runtime_seconds, restarts=1)
        res = OPTIMIZERS[algo]().optimize(initial, spec, budget, None, rc, seed)
        initial_score, best_score, best = res.initial_score, res.best_score, res.best_portfolio
    else:
        raise ValueError(f"algoritmo desconhecido: {algo}")
    elapsed = time.perf_counter() - t0
    cov = CoverageMetrics(spec)
    return {
        "algorithm": algo, "score": best_score, "improvement": best_score - initial_score,
        "pair_unique": cov.pairs(best).unique, "elapsed": elapsed,
        "valid": _is_valid(best, spec, budget), "portfolio": best,
    }


def run_benchmark(spec, budget, seeds, algorithms, iterations, runtime_seconds, out_dir: Path):
    rows = []
    for algo in algorithms:
        runs = [_run_one(spec, budget, algo, s, iterations, runtime_seconds) for s in seeds]
        n = len(runs)
        rows.append({
            "algorithm": algo,
            "score": sum(r["score"] for r in runs) / n,
            "improvement": sum(r["improvement"] for r in runs) / n,
            "pair_unique": round(sum(r["pair_unique"] for r in runs) / n),
            "elapsed": sum(r["elapsed"] for r in runs) / n,
            "valid": all(r["valid"] for r in runs),
        })
    valid_rows = [r for r in rows if r["valid"]]
    winner = max(valid_rows, key=lambda r: r["score"])["algorithm"] if valid_rows else "nenhum"
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "benchmark.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["algorithm", "score", "improvement", "pair_unique",
                                           "elapsed", "valid"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return {"rows": rows, "winner": winner}

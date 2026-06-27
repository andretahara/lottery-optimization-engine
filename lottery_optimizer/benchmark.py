"""Benchmark justo de geradores e otimizadores: mesma seed, orcamento e GameSpec.

Vencedor NAO e escolhido so pelo score: carteiras invalidas (orcamento violado, duplicatas,
dezena fora do universo, tamanho invalido, preco invalido) sao descartadas antes da escolha.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .algorithms import OPTIMIZERS, RuntimeConfig
from .core.game import GameSpec
from .disclaimer import DISCLAIMER
from .generators import GENERATORS, GenerationConstraints
from .metrics.coverage import CoverageMetrics
from .metrics.distance import DistanceMetrics
from .metrics.scoring import PortfolioScore
from .utils.profiling import profile_block

_SIMPLE = GenerationConstraints(strategy="all_simple")
_FIELDS = ["algorithm", "score", "improvement", "main_unique", "pair_unique", "triple_unique",
           "quad_unique", "pair_redundancy", "mean_distance", "elapsed", "peak_kb", "valid"]


def _is_valid(portfolio, spec: GameSpec, budget: int) -> bool:
    if len(portfolio) != budget:
        return False
    if len({t.numbers for t in portfolio}) != len(portfolio):
        return False
    for t in portfolio:
        if len(t) not in spec.allowed_ticket_sizes or not all(spec.contains(n) for n in t.numbers):
            return False
    return True


def _run_one(spec, budget, algo, seed, iterations, runtime_seconds):
    ps = PortfolioScore()
    with profile_block(f"bench:{algo}", track_memory=True) as prof:
        if algo in GENERATORS:
            best = GENERATORS[algo]().generate(spec, budget, _SIMPLE, seed)
            initial_score = best_score = ps.score(best, spec)
        elif algo in OPTIMIZERS:
            initial = GENERATORS["hybrid_initial"]().generate(spec, budget, _SIMPLE, seed)
            rc = RuntimeConfig(max_iterations=iterations, runtime_seconds=runtime_seconds, restarts=1)
            res = OPTIMIZERS[algo]().optimize(initial, spec, budget, None, rc, seed)
            initial_score, best_score, best = res.initial_score, res.best_score, res.best_portfolio
        else:
            raise ValueError(f"algoritmo desconhecido: {algo}")
    cov = CoverageMetrics(spec)
    pair, triple, quad = cov.pairs(best), cov.triples(best), cov.quads(best)
    return {
        "algorithm": algo, "score": best_score, "improvement": best_score - initial_score,
        "main_unique": cov.main(best).unique, "pair_unique": pair.unique,
        "triple_unique": triple.unique, "quad_unique": quad.unique,
        "pair_redundancy": pair.redundancy, "mean_distance": DistanceMetrics().mean_pairwise_distance(best),
        "elapsed": prof["elapsed"], "peak_kb": prof.get("peak_kb", 0.0),
        "valid": _is_valid(best, spec, budget),
    }


def _avg_rows(spec, budget, algorithms, seeds, iterations, runtime_seconds):
    rows = []
    for algo in algorithms:
        runs = [_run_one(spec, budget, algo, s, iterations, runtime_seconds) for s in seeds]
        n = len(runs)
        row = {"algorithm": algo, "valid": all(r["valid"] for r in runs)}
        for k in ("score", "improvement", "mean_distance", "elapsed", "peak_kb"):
            row[k] = sum(r[k] for r in runs) / n
        for k in ("main_unique", "pair_unique", "triple_unique", "quad_unique", "pair_redundancy"):
            row[k] = round(sum(r[k] for r in runs) / n)
        rows.append(row)
    return rows


def _export(spec, rows, winner, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    # CSV
    with (out_dir / "benchmark.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in _FIELDS})
    # Excel
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Benchmark"
    ws.append(_FIELDS)
    for r in rows:
        ws.append([r.get(k, "") for k in _FIELDS])
    ws.freeze_panes = "A2"
    wsa = wb.create_sheet("AvisoMatematico")
    wsa.append([DISCLAIMER])
    wb.save(out_dir / "benchmark.xlsx")
    # Relatorio
    lines = [DISCLAIMER, "", f"Benchmark - {spec.name} ({spec.game_id})", "",
             f"{'algoritmo':<22}{'score':>10}{'melhoria':>10}{'cob.pares':>10}{'tempo_s':>9}{'valido':>8}"]
    for r in rows:
        lines.append(f"{r['algorithm']:<22}{r['score']:>10.4f}{r['improvement']:>10.4f}"
                     f"{r['pair_unique']:>10}{r['elapsed']:>9.2f}{'sim' if r['valid'] else 'NAO':>8}")
    lines += ["", f"VENCEDOR (entre validos, por score): {winner}",
              "Carteiras invalidas (orcamento/duplicata/universo/tamanho) sao descartadas antes "
              "da escolha - score sozinho nao decide.", "", DISCLAIMER]
    (out_dir / "benchmark_report.txt").write_text("\n".join(lines), encoding="utf-8")
    _charts(rows, out_dir)


def _charts(rows, out_dir: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    algos = [r["algorithm"] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(algos, [r["score"] for r in rows], color="#2a6f97")
    ax.set_title("Benchmark - score final")
    ax.set_ylabel("score")
    plt.xticks(rotation=30, ha="right")
    fig.savefig(out_dir / "benchmark_score.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    import numpy as np
    fig, ax = plt.subplots(figsize=(11, 4))
    x = np.arange(len(algos))
    for i, key in enumerate(("pair_unique", "triple_unique", "quad_unique")):
        ax.bar(x + i * 0.25, [r[key] for r in rows], width=0.25, label=key)
    ax.set_xticks(x + 0.25)
    ax.set_xticklabels(algos, rotation=30, ha="right")
    ax.set_title("Benchmark - cobertura unica por subconjunto")
    ax.legend()
    fig.savefig(out_dir / "benchmark_coverage.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def run_benchmark(spec, budget, seeds, algorithms, iterations, runtime_seconds, out_dir: Path):
    rows = _avg_rows(spec, budget, algorithms, seeds, iterations, runtime_seconds)
    valid = [r for r in rows if r["valid"]]
    winner = max(valid, key=lambda r: r["score"])["algorithm"] if valid else "nenhum"
    _export(spec, rows, winner, Path(out_dir))
    return {"rows": rows, "winner": winner}

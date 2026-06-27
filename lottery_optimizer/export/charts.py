"""Graficos PNG (matplotlib, backend Agg, sem seaborn). Cada grafico em figura separada."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from ..core.game import GameSpec  # noqa: E402
from ..core.portfolio import Portfolio  # noqa: E402
from ..metrics.coverage import CoverageMetrics  # noqa: E402
from ..metrics.distance import DistanceMetrics  # noqa: E402
from ..metrics.frequency import FrequencyMetrics  # noqa: E402

_DPI = 150


def _save(fig, path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(p, dpi=_DPI, bbox_inches="tight")
    plt.close(fig)
    return p


def plot_frequency(portfolio: Portfolio, spec: GameSpec, path) -> Path:
    freq = FrequencyMetrics(spec).absolute(portfolio)
    xs = sorted(freq)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(xs, [freq[n] for n in xs], color="#2a6f97")
    ax.set_title(f"Frequencia das dezenas - {spec.name}")
    ax.set_xlabel("dezena")
    ax.set_ylabel("frequencia na carteira")
    return _save(fig, path)


def plot_score_history(score_history, path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(range(len(score_history)), score_history, color="#1b9e77")
    ax.set_title("Evolucao do score")
    ax.set_xlabel("iteracao")
    ax.set_ylabel("score")
    return _save(fig, path)


def plot_overlap_distribution(portfolio: Portfolio, path) -> Path:
    dist = DistanceMetrics().overlap_distribution(portfolio)
    xs = sorted(dist)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar([str(x) for x in xs], [dist[x] for x in xs], color="#d95f02")
    ax.set_title("Distribuicao de sobreposicao entre apostas")
    ax.set_xlabel("dezenas em comum")
    ax.set_ylabel("numero de pares")
    return _save(fig, path)


def plot_coverage_by_subset(portfolio: Portfolio, spec: GameSpec, path) -> Path:
    cov = CoverageMetrics(spec)
    labels = ["pares", "trincas", "quadras"]
    vals = [cov.pairs(portfolio).unique, cov.triples(portfolio).unique, cov.quads(portfolio).unique]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, vals, color="#7570b3")
    ax.set_title(f"Cobertura unica por subconjunto - {spec.name}")
    ax.set_ylabel("subconjuntos distintos cobertos")
    return _save(fig, path)

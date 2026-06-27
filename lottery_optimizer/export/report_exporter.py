"""Relatorio TXT completo. SEMPRE injeta o disclaimer e registra config de preco/seed/algoritmo."""

from __future__ import annotations

from pathlib import Path

from ..core.game import GameSpec
from ..core.portfolio import Portfolio
from ..disclaimer import DISCLAIMER
from .report_data import ReportData, build_report_data


def _fmt_money(v) -> str:
    return "n/d" if v is None else f"R$ {v:,.2f}"


def render_report(rd: ReportData) -> str:
    p_main = rd.p_main
    one_in = (1 / p_main) if p_main > 0 else 0
    lines = [
        DISCLAIMER, "",
        "=" * 70,
        f"Loteria: {rd.spec.name} ({rd.spec.game_id})",
        f"Data/hora: {rd.timestamp or 'n/d'}",
        f"Algoritmo: {rd.algorithm or 'n/d'}    Seed: {rd.seed if rd.seed is not None else 'n/d'}",
        f"Config de preco: {rd.price_config}",
        "-" * 70,
        f"Apostas: {rd.n_tickets}    Tamanhos: {sorted(set(rd.ticket_sizes))}",
        f"Combinacoes simples equivalentes: {rd.equivalent_simple_total:,}",
        f"Orcamento: {_fmt_money(rd.budget)}    Custo total: {_fmt_money(rd.total_cost)}"
        + (" (ESTIMATIVA)" if rd.cost_is_estimate else ""),
        f"Saldo: {_fmt_money(rd.balance_amount)}",
        "-" * 70,
        f"Cobertura principal (K={rd.spec.draw_size}) - bruta: {rd.raw_main:,}  "
        f"unica: {rd.unique_main:,} ({rd.coverage_mode_used})",
        f"Probabilidade teorica do premio principal: {float(p_main):.3e}"
        + (f"  (~1 em {float(one_in):,.0f})" if one_in else ""),
        f"Cobertura de pares: unica {rd.pair_cov.unique:,} / bruta {rd.pair_cov.raw:,} "
        f"(redundancia {rd.pair_cov.redundancy:,})",
        f"Cobertura de trincas: unica {rd.triple_cov.unique:,} / bruta {rd.triple_cov.raw:,}",
        f"Cobertura de quadras: unica {rd.quad_cov.unique:,} / bruta {rd.quad_cov.raw:,}",
        "-" * 70,
        f"Equilibrio: pares/impares {rd.odd_even}  baixas/altas {rd.low_high}  "
        f"entropia {rd.entropy:.3f}",
        f"Distancia media (Jaccard): {rd.mean_distance:.3f}    "
        f"Intersecao media: {rd.mean_intersection:.2f}  max: {rd.max_intersection}",
        "-" * 70,
        "Frequencia das dezenas:",
        "  " + "  ".join(f"{n:02d}:{c}" for n, c in sorted(rd.frequency.items()) if c > 0),
        "=" * 70,
        "",
        DISCLAIMER,
    ]
    return "\n".join(lines)


def build_report(portfolio: Portfolio, spec: GameSpec, **meta) -> str:
    """Compat + completo: aceita budget/cost_model/algorithm/seed/params/timestamp/score_history."""
    rd = build_report_data(portfolio, spec, **meta)
    return render_report(rd)


def export_report(portfolio: Portfolio, spec: GameSpec, path, **meta) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(build_report(portfolio, spec, **meta), encoding="utf-8")
    return p

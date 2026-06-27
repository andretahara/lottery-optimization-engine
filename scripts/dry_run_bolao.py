"""Dry-run do fluxo completo do bolao com um jogo PEQUENO ARTIFICIAL (rapido, exato).

Prova que generate -> optimize -> export -> report funciona ponta-a-ponta. Usa preco FICTICIO
marcado como exemplo (NAO oficial) so para demonstrar custo/saldo.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from lottery_optimizer.algorithms import OPTIMIZERS, RuntimeConfig
from lottery_optimizer.core.cost import CostModel
from lottery_optimizer.core.game import GameSpec
from lottery_optimizer.disclaimer import DISCLAIMER
from lottery_optimizer.export import charts, export_csv, export_excel, export_report
from lottery_optimizer.generators import GENERATORS, GenerationConstraints


def small_spec() -> GameSpec:
    # jogo artificial: universo 1..20, sorteia 5, aposta simples de 5 - preco de EXEMPLO
    return GameSpec(game_id="mini-bolao", name="Mini Bolao (teste)", universe_min=1,
                    universe_max=20, draw_size=5, allowed_ticket_sizes=(5,),
                    price_table={5: Decimal("2.50")}, price_status="example",
                    price_source_note="EXAMPLE_NOT_OFFICIAL - jogo de teste")


def run(seed: int = 20260627, budget: int = 8, output_base=None) -> dict:
    spec = small_spec()
    out = Path(output_base or "output/dry_run_bolao")
    out.mkdir(parents=True, exist_ok=True)
    cm = CostModel(spec)

    initial = GENERATORS["hybrid_initial"]().generate(
        spec, budget, GenerationConstraints(strategy="all_simple"), seed)
    res = OPTIMIZERS["hybrid"]().optimize(
        initial, spec, budget, None, RuntimeConfig(max_iterations=40), seed)
    best = res.best_portfolio

    meta = dict(algorithm="hybrid", seed=seed)
    export_csv(best, out / "jogos.csv", game_id=spec.game_id)
    export_report(best, spec, out / "relatorio.txt", cost_model=cm,
                  budget=Decimal(budget) * Decimal("2.50"), score_history=res.score_history, **meta)
    export_excel(best, out / "jogos.xlsx", spec=spec, cost_model=cm,
                 budget=Decimal(budget) * Decimal("2.50"), score_history=res.score_history, **meta)
    charts.plot_frequency(best, spec, out / "frequencia_dezenas.png")
    charts.plot_score_history(res.score_history, out / "score_history.png")

    total = cm.portfolio_cost(best)
    return dict(spec=spec.name, apostas=len(best), custo=total.amount, estimativa=total.is_estimate,
                score=res.best_score, output_dir=str(out))


def main() -> None:  # pragma: no cover
    print(DISCLAIMER, "\n")
    s = run()
    print(f"[1] jogo: {s['spec']}  [3] apostas: {s['apostas']}")
    print(f"[9] custo total: R$ {s['custo']}" + ("  (ESTIMATIVA - preco de teste)" if s["estimativa"] else ""))
    print(f"[12] score final: {s['score']:.4f}")
    print(f"[7-8] arquivos (CSV/Excel/relatorio/graficos) em {s['output_dir']}")
    print("\n" + DISCLAIMER)


if __name__ == "__main__":  # pragma: no cover
    main()

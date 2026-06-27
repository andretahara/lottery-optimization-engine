"""Exemplo operacional: Quina de Sao Joao (orcamento R$ 19.140,00).

Demonstra o fluxo real SEM prender a engine a Quina e SEM inventar preco oficial:
carrega GameSpec da Quina + orcamento, valida precos (PARA se null/exemplo), decide
simples/multipla/mista pelo custo por combinacao equivalente, gera, otimiza e exporta.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import yaml

from lottery_optimizer.algorithms import OPTIMIZERS, RuntimeConfig
from lottery_optimizer.core.cost import CostModel
from lottery_optimizer.core.pricing import assert_prices_usable, price_config_summary
from lottery_optimizer.disclaimer import DISCLAIMER
from lottery_optimizer.export import export_csv, export_excel, export_report
from lottery_optimizer.export import charts
from lottery_optimizer.games.registry import GameRegistry
from lottery_optimizer.generators import GENERATORS, GenerationConstraints
from lottery_optimizer.metrics.scoring import PortfolioScore

_DEFAULT_CONFIG = Path(__file__).parent.parent / "configs" / "quina_sao_joao_budget_19140.yaml"

# campos de preco que viram override da spec
_PRICE_FIELDS = ("price_status", "official_price_last_checked", "price_source_note", "price_table")


def load_config(path=_DEFAULT_CONFIG) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def build_spec(config: dict):
    reg = GameRegistry()
    override = {k: config[k] for k in _PRICE_FIELDS if k in config}
    if config.get("price_table") is not None:
        override["price_table"] = {int(k): Decimal(str(v)) for k, v in config["price_table"].items()}
    if override:
        reg.apply_overrides({config["game_id"]: override})
    return reg.get(config["game_id"])


def decide_ticket_sizing(spec, cost_model: CostModel) -> tuple[str, str]:
    """Decide simples/multipla/mista pelo custo por combinacao simples equivalente."""
    per = {}
    for size in spec.allowed_ticket_sizes:
        per[size] = cost_model.cost_per_simple_combination(size).amount
    cheapest = min(per, key=per.get)
    all_equal = len(set(per.values())) == 1
    if all_equal:
        note = ("Custo por combinacao simples equivalente IGUAL entre tamanhos: apostas "
                "multiplas NAO aumentam a eficiencia matematica do premio principal - apenas "
                "consolidam combinacoes. Usando aposta simples (max cobertura distinta).")
        return "all_simple", note
    note = (f"Tamanho {cheapest} tem menor custo por combinacao equivalente "
            f"(R$ {per[cheapest]}). Usando-o.")
    strategy = "all_simple" if cheapest == spec.min_ticket_size else "fixed"
    return strategy, note


def run(config: dict, *, seed=None, allow_example=False, output_base=None, iterations=None) -> dict:
    spec = build_spec(config)
    # validacao de preco: PARA se nao utilizavel (null/exemplo sem flag)
    assert_prices_usable(spec, allow_example=allow_example)

    budget = Decimal(str(config["budget"]))
    seed = int(seed if seed is not None else config.get("seed", 12345))
    cost_model = CostModel(spec)

    simple_price = cost_model.ticket_cost(spec.min_ticket_size).amount
    num_tickets = int(budget // simple_price)
    if num_tickets < 1:
        raise ValueError(f"orcamento {budget} insuficiente para 1 aposta de {simple_price}")

    strategy, sizing_note = decide_ticket_sizing(spec, cost_model)
    constraints = (GenerationConstraints(strategy="fixed",
                   ticket_size=min(spec.allowed_ticket_sizes, key=lambda s: cost_model.cost_per_simple_combination(s).amount))
                   if strategy == "fixed" else GenerationConstraints(strategy="all_simple"))

    initial = GENERATORS[config.get("initial_strategy", "hybrid_initial")]().generate(
        spec, num_tickets, constraints, seed)
    sc = PortfolioScore(weights=config.get("score_weights"))
    rc = RuntimeConfig(max_iterations=int(iterations if iterations is not None
                                          else config.get("iterations", 300)),
                       coverage_mode="auto")
    res = OPTIMIZERS[config.get("optimizer", "hybrid")]().optimize(
        initial, spec, num_tickets, sc, rc, seed)

    out = Path(output_base or config.get("output_dir", "output/quina_sao_joao"))
    out.mkdir(parents=True, exist_ok=True)
    meta = dict(algorithm=config.get("optimizer", "hybrid"), seed=seed,
                params={"budget": str(budget), "num_tickets": num_tickets, "sizing": sizing_note})
    export_csv(res.best_portfolio, out / "jogos.csv", game_id=spec.game_id)
    export_report(res.best_portfolio, spec, out / "relatorio.txt", cost_model=cost_model,
                  budget=budget, score_history=res.score_history, **meta)
    export_excel(res.best_portfolio, out / "jogos.xlsx", spec=spec, cost_model=cost_model,
                 budget=budget, score_history=res.score_history, **meta)
    charts.plot_frequency(res.best_portfolio, spec, out / "frequencia_dezenas.png")
    charts.plot_score_history(res.score_history, out / "score_history.png")

    summary = dict(game=spec.name, budget=budget, num_tickets=num_tickets,
                   simple_price=simple_price, sizing_note=sizing_note,
                   initial_score=res.initial_score, best_score=res.best_score,
                   improvement=res.improvement, output_dir=str(out),
                   price_config=price_config_summary(spec))
    return summary


def main() -> None:  # pragma: no cover
    import sys

    from lottery_optimizer.core.pricing import PriceError

    allow = "--allow-example-prices" in sys.argv
    print(DISCLAIMER, "\n")
    try:
        s = run(load_config(), allow_example=allow)
    except PriceError as e:
        print(f"PARADO: {e}")
        print("Atualize o preco oficial vigente em configs/quina_sao_joao_budget_19140.yaml.")
        sys.exit(2)
    print(f"{s['game']}: {s['num_tickets']} apostas (R$ {s['simple_price']} cada), "
          f"orcamento R$ {s['budget']}")
    print(s["sizing_note"])
    print(f"Score {s['initial_score']:.4f} -> {s['best_score']:.4f} (+{s['improvement']:.4f})")
    print(f"Arquivos em {s['output_dir']}")
    print("\n" + DISCLAIMER)


if __name__ == "__main__":  # pragma: no cover
    main()

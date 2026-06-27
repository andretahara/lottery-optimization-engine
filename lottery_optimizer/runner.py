"""Runner generico de execucao a partir de uma config YAML. NAO preso a nenhum jogo.

Carrega GameSpec por game_id, aplica override de preco, valida (PARA se null/exemplo),
decide simples/multipla pelo custo por combinacao equivalente, gera, otimiza e exporta.
Usado pelos scripts de exemplo (Quina de Sao Joao, Mega da Virada, etc).
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import yaml

from .algorithms import OPTIMIZERS, RuntimeConfig
from .core.cost import CostModel
from .core.pricing import assert_prices_usable, price_config_summary
from .export import charts, export_csv, export_excel, export_report
from .games.registry import GameRegistry
from .generators import GENERATORS, GenerationConstraints
from .metrics.scoring import PortfolioScore

_PRICE_FIELDS = ("price_status", "official_price_last_checked", "price_source_note", "price_table")


def load_config(path) -> dict:
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
    """Decide simples/multipla pelo custo por combinacao simples equivalente."""
    per = {s: cost_model.cost_per_simple_combination(s).amount for s in spec.allowed_ticket_sizes}
    cheapest = min(per, key=per.get)
    if len(set(per.values())) == 1:
        note = ("Custo por combinacao simples equivalente IGUAL entre tamanhos: apostas "
                "multiplas NAO aumentam a eficiencia matematica do premio principal - apenas "
                "consolidam combinacoes. Usando aposta simples (max cobertura distinta).")
        return "all_simple", note
    note = f"Tamanho {cheapest} tem menor custo por combinacao equivalente (R$ {per[cheapest]})."
    return ("all_simple" if cheapest == spec.min_ticket_size else "fixed"), note


def run_from_config(config: dict, *, seed=None, allow_example=False, output_base=None,
                    iterations=None) -> dict:
    spec = build_spec(config)
    assert_prices_usable(spec, allow_example=allow_example)  # PARA se null/exemplo sem flag

    budget = Decimal(str(config["budget"]))
    seed = int(seed if seed is not None else config.get("seed", 12345))
    cost_model = CostModel(spec)
    simple_price = cost_model.ticket_cost(spec.min_ticket_size).amount
    num_tickets = int(budget // simple_price)
    if num_tickets < 1:
        raise ValueError(f"orcamento {budget} insuficiente para 1 aposta de {simple_price}")

    strategy, sizing_note = decide_ticket_sizing(spec, cost_model)
    if strategy == "fixed":
        size = min(spec.allowed_ticket_sizes, key=lambda s: cost_model.cost_per_simple_combination(s).amount)
        constraints = GenerationConstraints(strategy="fixed", ticket_size=size)
    else:
        constraints = GenerationConstraints(strategy="all_simple")

    initial = GENERATORS[config.get("initial_strategy", "hybrid_initial")]().generate(
        spec, num_tickets, constraints, seed)
    sc = PortfolioScore(weights=config.get("score_weights"))
    rc = RuntimeConfig(max_iterations=int(iterations if iterations is not None
                                          else config.get("iterations", 300)), coverage_mode="auto")
    res = OPTIMIZERS[config.get("optimizer", "hybrid")]().optimize(
        initial, spec, num_tickets, sc, rc, seed)

    out = Path(output_base or config.get("output_dir", "output/run"))
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

    return dict(game=spec.name, game_id=spec.game_id, draw_size=spec.draw_size, budget=budget,
                num_tickets=num_tickets, simple_price=simple_price, sizing_note=sizing_note,
                initial_score=res.initial_score, best_score=res.best_score,
                improvement=res.improvement, output_dir=str(out),
                price_config=price_config_summary(spec))

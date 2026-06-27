import pytest

from lottery_optimizer.core.pricing import PriceError
from lottery_optimizer.disclaimer import DISCLAIMER

import scripts.run_quina_sao_joao as rqsj


def base_config(**over):
    cfg = dict(
        game_id="quina", budget=30.00, seed=1, optimizer="hybrid",
        initial_strategy="hybrid_initial", iterations=15,
        score_weights={"main_coverage": 0.5, "intermediate_coverage": 0.3},
        # PRECO FICTICIO marcado como EXEMPLO/TESTE - nao oficial
        price_status="example",
        price_source_note="EXAMPLE_NOT_OFFICIAL - preco de teste",
        price_table={5: "2.50"},
    )
    cfg.update(over)
    return cfg


def test_stops_on_null_price():
    # config sem preco (unset) -> PARA com PriceError
    cfg = base_config(price_status="unset", price_table=None, price_source_note="x")
    with pytest.raises(PriceError):
        rqsj.run(cfg, allow_example=False)


def test_example_price_needs_flag():
    with pytest.raises(PriceError):
        rqsj.run(base_config(), allow_example=False)  # example sem flag -> PARA


def test_runs_with_test_price(tmp_path):
    cfg = base_config()
    s = rqsj.run(cfg, allow_example=True, output_base=tmp_path, iterations=12)
    assert s["num_tickets"] == 12          # 30.00 / 2.50
    assert s["best_score"] >= s["initial_score"]
    assert "multiplas NAO aumentam" in s["sizing_note"]
    for f in ["jogos.csv", "relatorio.txt", "jogos.xlsx", "frequencia_dezenas.png",
              "score_history.png"]:
        assert (tmp_path / f).exists(), f
    assert DISCLAIMER in (tmp_path / "relatorio.txt").read_text(encoding="utf-8")


def test_shipped_config_is_null_price():
    cfg = rqsj.load_config()
    assert cfg["price_table"] is None and cfg["price_status"] == "unset"
    assert float(cfg["budget"]) == 19140.00

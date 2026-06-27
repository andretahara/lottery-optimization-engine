import re
from pathlib import Path

import pytest

from lottery_optimizer.core.pricing import PriceError
from lottery_optimizer.core.probability import ProbabilityModel
from lottery_optimizer.disclaimer import DISCLAIMER
from lottery_optimizer.metrics.coverage import CoverageMetrics

import scripts.run_mega_sena_virada as rmsv
import scripts.run_quina_sao_joao as rqsj


def cfg(**over):
    c = dict(game_id="mega-sena", budget=60.00, seed=1, optimizer="hybrid",
             initial_strategy="hybrid_initial", iterations=12,
             score_weights={"main_coverage": 0.55, "intermediate_coverage": 0.30},
             price_status="example", price_source_note="EXAMPLE_NOT_OFFICIAL - teste",
             price_table={6: "5.00"})
    c.update(over)
    return c


def test_mega_different_spec_than_quina():
    mega = rmsv.runner.build_spec(cfg())
    quina = rqsj.runner.build_spec(dict(game_id="quina", price_status="unset"))
    assert (mega.pool, mega.draw_size) == (60, 6)
    assert (quina.pool, quina.draw_size) == (80, 5)
    assert ProbabilityModel(mega).total_combinations() == 50_063_860  # C(60,6)


def test_stops_on_null_price():
    with pytest.raises(PriceError):
        rmsv.run(cfg(price_status="unset", price_table=None), allow_example=False)


def test_runs_and_main_coverage_is_six(tmp_path):
    s = rmsv.run(cfg(), allow_example=True, output_base=tmp_path, iterations=10)
    assert s["num_tickets"] == 12  # 60.00 / 5.00
    assert s["draw_size"] == 6
    # cobertura principal usa subconjuntos de 6 dezenas
    from lottery_optimizer.export.csv_exporter import load_csv
    spec = rmsv.runner.build_spec(cfg())
    p = load_csv(spec, tmp_path / "jogos.csv")
    assert CoverageMetrics(spec).main(p).size == 6
    txt = (tmp_path / "relatorio.txt").read_text(encoding="utf-8")
    assert "Mega-Sena" in txt and "K=6" in txt and DISCLAIMER in txt


def test_no_quina_hardcoded_in_engine():
    # nenhum modulo de algoritmo/gerador/otimizador menciona uma loteria especifica
    roots = ["lottery_optimizer/algorithms", "lottery_optimizer/generators",
             "lottery_optimizer/core", "lottery_optimizer/metrics"]
    pattern = re.compile(r"\b(quina|mega|lotofacil|lotomania|timemania)\b", re.I)
    for root in roots:
        for f in Path(root).rglob("*.py"):
            text = f.read_text(encoding="utf-8")
            # remove comentarios/docstrings simples nao: basta nao ter logica ramificando por nome
            assert not pattern.search(text), f"{f} menciona loteria especifica"

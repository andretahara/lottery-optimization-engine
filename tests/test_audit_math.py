"""Auditoria matematica: trava invariantes de probabilidade, custo, carteira, metricas,
otimizadores e relatorios. Nenhuma feature nova - so verificacao."""

from decimal import Decimal
from fractions import Fraction

import pytest

from lottery_optimizer.algorithms import OPTIMIZERS, RuntimeConfig
from lottery_optimizer.core.cost import CostModel
from lottery_optimizer.core.game import GameSpec
from lottery_optimizer.core.pricing import PriceError, assert_prices_usable
from lottery_optimizer.core.portfolio import Portfolio
from lottery_optimizer.core.probability import ProbabilityModel
from lottery_optimizer.core.ticket import Ticket
from pydantic import ValidationError

from lottery_optimizer.core.validation import TicketError
from lottery_optimizer.export.report_exporter import build_report
from lottery_optimizer.generators import GENERATORS, GenerationConstraints
from lottery_optimizer.games import registry
from lottery_optimizer.metrics.coverage import CoverageMetrics

SIMPLE = GenerationConstraints(strategy="all_simple")
GAMES = ["quina", "mega-sena", "lotofacil"]


# ===== 1. PROBABILIDADE =====
@pytest.mark.parametrize("gid,expected", [
    ("quina", 24_040_016), ("mega-sena", 50_063_860), ("lotofacil", 3_268_760)])
def test_total_combinations_correct(gid, expected):
    assert ProbabilityModel(registry.get(gid)).total_combinations() == expected


def test_p_main_uses_unique_not_raw():
    spec = registry.get("quina")
    p = GENERATORS["random"]().generate(spec, 20, SIMPLE, 1)
    pm = ProbabilityModel(spec)
    unique = pm.unique_coverage(p)
    raw = pm.raw_coverage(p)
    assert unique <= raw                                   # unica nunca passa da bruta
    assert pm.p_main(p) == Fraction(unique, spec.total_outcomes())
    assert pm.p_main(p) <= 1                                # nunca infla acima de 1


def test_no_double_count_overlapping_multiples():
    # dois jogos multiplos com sobreposicao: cobertura unica < soma das coberturas
    spec = registry.get("mega-sena")
    a = Ticket(numbers=tuple(range(1, 8)))   # C(7,6)=7
    b = Ticket(numbers=tuple(range(2, 9)))   # C(7,6)=7, sobrepoe
    p = Portfolio(spec, [a, b])
    cov = CoverageMetrics(spec).main(p)
    assert cov.raw == 14 and cov.unique < 14   # dedup real


# ===== 2. CUSTO =====
def test_cost_respects_table_and_marks_estimates():
    spec = GameSpec(game_id="t", name="T", universe_min=1, universe_max=60, draw_size=6,
                    allowed_ticket_sizes=(6, 7), price_table={6: Decimal("6.00")},
                    price_status="official", official_price_last_checked="2026-06-27")
    cm = CostModel(spec)
    assert cm.ticket_cost(6).is_estimate is False           # oficial
    assert cm.ticket_cost(7).is_estimate is True            # estimado (sem tabela p/ 7)
    p = Portfolio(spec, [Ticket(numbers=tuple(range(1, 7)))])
    assert cm.balance(p, Decimal("10.00")).amount == Decimal("4.00")  # saldo correto


def test_real_run_blocked_without_official_price():
    with pytest.raises(PriceError):
        assert_prices_usable(registry.get("quina"))         # unset -> bloqueia


# ===== 3. CARTEIRA =====
def test_portfolio_rejects_invalid():
    spec = registry.get("quina")
    # nivel Ticket: erro encapsulado em pydantic.ValidationError
    with pytest.raises(ValidationError):
        Ticket(numbers=(1, 1, 2, 3, 4))                     # dezena repetida
    # nivel Portfolio (validate_against): TicketError direto
    with pytest.raises(TicketError):
        Portfolio(spec, [Ticket(numbers=(1, 2, 3, 4, 99))]) # 99 fora do universo (1-80)
    with pytest.raises(TicketError):
        Portfolio(spec, [Ticket(numbers=(1, 2, 3))])        # tamanho invalido (precisa 5-7)
    with pytest.raises(TicketError):
        p = Portfolio(spec, [Ticket(numbers=(1, 2, 3, 4, 5))])
        p.add(Ticket(numbers=(1, 2, 3, 4, 5)))              # duplicata


# ===== 4. METRICAS =====
def test_metrics_coverage_and_redundancy():
    spec = registry.get("quina")
    cov = CoverageMetrics(spec)
    p = Portfolio(spec, [Ticket(numbers=(1, 2, 3, 4, 5)), Ticket(numbers=(1, 2, 3, 4, 6))])
    pairs = cov.pairs(p)
    assert pairs.redundancy == pairs.raw - pairs.unique
    assert 0 <= pairs.unique_raw_ratio <= 1


# ===== 5. OTIMIZADORES =====
@pytest.mark.parametrize("name", list(OPTIMIZERS))
def test_optimizer_invariants(name):
    spec = registry.get("quina")
    p0 = GENERATORS["random"]().generate(spec, 10, SIMPLE, 1)
    rc = RuntimeConfig(max_iterations=40, restarts=1, population=8, generations=8, grasp_rounds=2)
    res = OPTIMIZERS[name]().optimize(p0, spec, 10, None, rc, seed=3)
    best = res.best_portfolio
    assert len(best) == 10                                  # orcamento preservado
    assert len({t.numbers for t in best}) == 10             # sem duplicatas
    assert best.spec is spec                                # GameSpec preservado
    assert all(len(t) in spec.allowed_ticket_sizes for t in best)
    assert res.best_score >= res.initial_score              # melhora de verdade (nunca piora)


# ===== 6. RELATORIOS =====
def test_report_no_prediction_claims_has_disclaimer():
    spec = registry.get("quina")
    p = GENERATORS["random"]().generate(spec, 8, SIMPLE, 1)
    report = build_report(p, spec, algorithm="hybrid", seed=1, timestamp="2026-06-27")
    low = report.lower()
    assert "não prevê" in low                               # disclaimer presente
    for forbidden in ["garantia de premio", "garante premio", "vai ganhar", "numeros que vao sair"]:
        assert forbidden not in low                         # sem promessa de previsao/garantia
    assert "probabilidade teorica" in low                   # chance teorica apresentada

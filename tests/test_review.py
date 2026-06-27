"""Revisao de 2o engenheiro: testes que travam os achados (sem confirmar so a implementacao)."""

from fractions import Fraction

from lottery_optimizer.algorithms.genetic import GeneticOptimizer
from lottery_optimizer.algorithms.base import RuntimeConfig
from lottery_optimizer.core.probability import ProbabilityModel
from lottery_optimizer.export.report_exporter import build_report
from lottery_optimizer.generators import GenerationConstraints, RandomGenerator
from lottery_optimizer.games import registry


def test_report_flags_estimated_probability():
    # MEDIUM-1: quando a cobertura e amostral, o relatorio sinaliza ESTIMADA
    spec = registry.get("mega-sena")
    p = RandomGenerator().generate(spec, 6, GenerationConstraints(strategy="all_simple"), 1)
    exact = build_report(p, spec, coverage_mode="exact")
    sampled = build_report(p, spec, coverage_mode="sampled")
    assert "ESTIMADA" not in exact
    assert "ESTIMADA" in sampled


def test_genetic_crossover_handles_mixed_sizes():
    # MEDIUM-2: otimizar carteira de tamanhos mistos nao quebra nem gera tamanho invalido
    spec = registry.get("mega-sena")
    initial = RandomGenerator().generate(
        spec, 6, GenerationConstraints(strategy="mixed_ticket_sizes", mixed_sizes=(6, 7)), 1)
    rc = RuntimeConfig(max_iterations=20, population=8, generations=6)
    res = GeneticOptimizer().optimize(initial, spec, 6, None, rc, seed=2)
    best = res.best_portfolio
    assert len(best) == 6
    assert all(len(t) in spec.allowed_ticket_sizes for t in best)
    assert len({t.numbers for t in best}) == 6


def test_lower_tier_boole_is_upper_bound_and_not_in_report():
    # MEDIUM-3: cota de Boole e LIMITE SUPERIOR (pode inflar) -> nunca aparece no relatorio
    spec = registry.get("mega-sena")
    p = RandomGenerator().generate(spec, 10, GenerationConstraints(strategy="all_simple"), 1)
    pm = ProbabilityModel(spec)
    approx = pm.p_tier_portfolio_approx(p, 4)
    single = pm.p_tier_single(6, 4)
    assert approx >= single             # cota superior
    assert approx <= Fraction(1, 1)
    report = build_report(p, spec)
    assert "Boole" not in report and "p_tier_portfolio" not in report

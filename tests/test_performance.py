"""Auditoria de engenharia/performance: modos exact/estimated/conservative, logs nao-silenciosos,
reprodutibilidade e validade preservadas, profiling."""

import logging

from lottery_optimizer.core.coverage import CONSERVATIVE_EXACT_CAP, CombinationCoverage
from lottery_optimizer.core.portfolio import Portfolio
from lottery_optimizer.core.ticket import Ticket
from lottery_optimizer.generators import GenerationConstraints, RandomGenerator
from lottery_optimizer.games import registry
from lottery_optimizer.metrics.coverage import coverage_ratio
from lottery_optimizer.metrics.scoring import PortfolioScore
from lottery_optimizer.utils.profiling import profile_block
from lottery_optimizer.utils.random import SeededRng


def test_exact_mode_small_game(mini):
    cov = CombinationCoverage(mini)
    p = Portfolio(mini, [Ticket(numbers=(1, 2, 3)), Ticket(numbers=(1, 2, 4))])
    assert cov.count_unique(p, 2, mode="exact") == 5  # exato em jogo pequeno


def test_estimated_not_silent(mini, caplog):
    # trava baixa forca fallback amostral -> DEVE logar (nunca silencioso)
    cov = CombinationCoverage(mini, exact_cap=5)
    p = Portfolio(mini, [Ticket(numbers=(1, 2, 3, 4)), Ticket(numbers=(5, 6, 7, 8))])
    with caplog.at_level(logging.WARNING, logger="lottery_optimizer.coverage"):
        cov.count_unique_auto(p, 3)  # raw=8 > cap=5 -> estimado
    assert any("ESTIMATIVA" in r.message for r in caplog.records)


def test_conservative_avoids_memory_explosion(caplog):
    # carteira com cobertura principal bruta > trava conservadora -> nao estoura, cai p/ amostral
    spec = registry.get("mega-sena")
    big = RandomGenerator().generate(
        spec, 25, GenerationConstraints(strategy="fixed", ticket_size=15), seed=1)
    raw_main = sum(15 for _ in big) and CombinationCoverage(spec).raw_count(big, 6)
    assert raw_main > CONSERVATIVE_EXACT_CAP  # garante que exceeds (25*C(15,6)=125125)
    ps = PortfolioScore(max_memory_mode="conservative")
    with caplog.at_level(logging.WARNING, logger="lottery_optimizer.scoring"):
        s = ps.score(big, spec, coverage_mode="auto")
    assert isinstance(s, float)
    assert any("ESTIMATIVA" in r.message for r in caplog.records)


def test_coverage_ratio_still_correct(mini):
    p = Portfolio(mini, [Ticket(numbers=(1, 2, 3)), Ticket(numbers=(4, 5, 6))])
    assert abs(coverage_ratio(p, mini, 2) - 6 / 36) < 1e-9  # total = C(9,2)=36


def test_seed_reproducible():
    assert SeededRng(7).sample(range(1, 61), 6) == SeededRng(7).sample(range(1, 61), 6)


def test_profile_block():
    with profile_block("teste") as p:
        sum(range(10000))
    assert p["elapsed"] >= 0 and "peak_kb" in p

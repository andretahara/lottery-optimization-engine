import math

from lottery_optimizer.core.portfolio import Portfolio
from lottery_optimizer.core.ticket import Ticket
from lottery_optimizer.metrics.balance import BalanceMetrics
from lottery_optimizer.metrics.coverage import CoverageMetrics
from lottery_optimizer.metrics.distance import DistanceMetrics
from lottery_optimizer.metrics.frequency import FrequencyMetrics
from lottery_optimizer.metrics.scoring import PortfolioScore


def p_disjoint(mini):
    return Portfolio(mini, [Ticket(numbers=(1, 2, 3)), Ticket(numbers=(4, 5, 6))])


def p_overlap(mini):
    return Portfolio(mini, [Ticket(numbers=(1, 2, 3, 4)), Ticket(numbers=(3, 4, 5, 6))])


# ---------- FrequencyMetrics ----------
def test_frequency_metrics(mini):
    fm = FrequencyMetrics(mini)
    p = p_disjoint(mini)
    absf = fm.absolute(p)
    assert absf[1] == 1 and absf[7] == 0 and len(absf) == 9
    assert abs(fm.ideal_frequency(p) - 6 / 9) < 1e-9
    assert fm.most_used(p) == (1, 1)
    assert fm.least_used(p) == (7, 0)
    assert abs(fm.relative(p)[1] - 1 / 6) < 1e-9
    assert abs(fm.coefficient_of_variation(p) - 0.70710678) < 1e-6


# ---------- BalanceMetrics ----------
def test_balance_metrics(mini):
    bm = BalanceMetrics(mini)
    p = p_disjoint(mini)
    assert bm.odd_even(p) == {"odd": 3, "even": 3}
    assert bm.low_high(p) == {"low": 5, "high": 1}   # mid=5
    assert bm.by_ranges(p, [(1, 3), (4, 9)]) == {"1-3": 3, "4-9": 3}
    assert bm.by_endings(p) == {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}
    assert bm.by_decades(p) == {0: 6}
    expected_entropy = math.log(6) / math.log(9)
    assert abs(bm.entropy(p) - expected_entropy) < 1e-9


# ---------- CoverageMetrics ----------
def test_coverage_metrics(mini):
    cm = CoverageMetrics(mini)
    p = p_overlap(mini)
    pairs = cm.pairs(p)
    assert (pairs.raw, pairs.unique, pairs.redundancy) == (12, 11, 1)
    assert abs(pairs.unique_raw_ratio - 11 / 12) < 1e-9
    triples = cm.triples(p)
    assert (triples.raw, triples.unique, triples.redundancy) == (8, 8, 0)
    assert cm.main(p).size == 3  # draw_size do mini


# ---------- DistanceMetrics ----------
def test_distance_metrics(mini):
    dm = DistanceMetrics(mini)
    p = p_overlap(mini)
    a, b = list(p)
    assert abs(dm.jaccard_distance(a, b) - (4 / 6)) < 1e-9
    assert dm.mean_intersection(p) == 2.0
    assert dm.max_intersection(p) == 2
    assert dm.overlap_distribution(p) == {2: 1}
    assert dm.similarity_penalty(p, threshold=2) == 1
    assert dm.similarity_penalty(p, threshold=3) == 0


# ---------- PortfolioScore ----------
def test_score_main_weight_prefers_more_coverage(mini):
    # A: 1 jogo size4 -> C(4,3)=4 trincas unicas; B: 2 jogos size3 -> 2 trincas unicas
    a = Portfolio(mini, [Ticket(numbers=(1, 2, 3, 4))])
    b = Portfolio(mini, [Ticket(numbers=(1, 2, 3)), Ticket(numbers=(1, 2, 4))])
    ps = PortfolioScore(weights={"main_coverage": 1.0, "intermediate_coverage": 0.0,
                                 "diversity": 0.0, "balance": 0.0, "low_redundancy": 0.0,
                                 "budget_adherence": 0.0},
                        penalties={"duplicates": 0.0, "concentration": 0.0, "low_distance": 0.0})
    assert ps.score(a, mini) > ps.score(b, mini)


def test_score_penalizes_similarity(mini):
    diverse = Portfolio(mini, [Ticket(numbers=(1, 2, 3)), Ticket(numbers=(4, 5, 6))])
    similar = Portfolio(mini, [Ticket(numbers=(1, 2, 3)), Ticket(numbers=(1, 2, 4))])
    ps = PortfolioScore()
    assert ps.score(diverse, mini) > ps.score(similar, mini)


def test_score_breakdown_keys(mini):
    bd = PortfolioScore().breakdown(p_disjoint(mini), mini)
    assert set(bd) == {"main_coverage", "intermediate_coverage", "diversity", "balance",
                       "low_redundancy", "budget_adherence"}
    assert 0.0 <= bd["diversity"] <= 1.0


def test_score_weights_from_file(tmp_path):
    f = tmp_path / "w.json"
    f.write_text('{"weights": {"main_coverage": 0.9}, "penalties": {"concentration": 0.0}}',
                 encoding="utf-8")
    ps = PortfolioScore.from_file(f)
    assert ps.weights["main_coverage"] == 0.9
    assert ps.penalties["concentration"] == 0.0

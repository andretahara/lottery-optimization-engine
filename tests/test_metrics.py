from lottery_optimizer.core.portfolio import Portfolio
from lottery_optimizer.core.ticket import Ticket
from lottery_optimizer.metrics import coverage, distance, frequency, scoring


def two_disjoint(mini):
    return Portfolio(mini, [Ticket(numbers=(1, 2, 3)), Ticket(numbers=(4, 5, 6))])


def test_frequency(mini):
    f = frequency.digit_frequency(two_disjoint(mini))
    assert f[1] == 1 and f[6] == 1 and 7 not in f


def test_pair_coverage_ratio(mini):
    # 2 jogos disjuntos de 3 dezenas => 6 pares distintos; universo C(9,2)=36
    r = coverage.coverage_ratio(two_disjoint(mini), mini, 2)
    assert abs(r - 6 / 36) < 1e-9


def test_mean_distance_disjoint(mini):
    assert distance.mean_pairwise_distance(two_disjoint(mini)) == 1.0


def test_balance_and_score_bounds(mini):
    s = scoring.score(two_disjoint(mini), mini)
    assert 0.0 <= s <= 1.0
    m = scoring.evaluate(two_disjoint(mini), mini)
    assert 0.0 <= m.balance <= 1.0

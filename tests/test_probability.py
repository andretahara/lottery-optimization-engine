from fractions import Fraction

from lottery_optimizer.core import probability as prob


def test_total_and_simple():
    assert prob.total_outcomes(60, 6) == 50_063_860
    assert prob.p_main_simple(60, 6) == Fraction(1, 50_063_860)


def test_multiple_equals_coverage_over_total():
    assert prob.equivalent_simple_games(7, 6) == 7
    assert prob.p_main_multiple(60, 6, 7) == Fraction(7, 50_063_860)


def test_multiple_equals_n_simple_no_edge():
    # razao premio/custo constante: P(multipla)/C(T,K) == P(simples)
    pool, k, marks = 60, 6, 8
    mult = prob.p_main_multiple(pool, k, marks)
    simple = prob.p_main_simple(pool, k)
    assert mult / prob.equivalent_simple_games(marks, k) == simple


def test_at_least_one_linear():
    assert prob.p_at_least_one_main(60, 6, 10) == Fraction(10, 50_063_860)


def test_exact_hits_hypergeometric_sums_to_one():
    pool, k, marks = 60, 6, 6
    total = sum(prob.p_exact_hits(pool, k, marks, h) for h in range(0, 7))
    assert total == Fraction(1, 1)


def test_exact_hits_out_of_range_zero():
    assert prob.p_exact_hits(60, 6, 6, 7) == 0

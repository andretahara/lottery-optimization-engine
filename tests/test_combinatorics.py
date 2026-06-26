import pytest
from hypothesis import given, strategies as st

from lottery_engine.combinatorics import n_choose_k, iter_combinations, k_subsets


def test_known_values():
    assert n_choose_k(60, 6) == 50_063_860   # Mega-Sena
    assert n_choose_k(80, 5) == 24_040_016   # Quina
    assert n_choose_k(25, 15) == 3_268_760   # Lotofacil
    assert n_choose_k(100, 20) == 535_983_370_403_809_682_970  # Lotomania


def test_edge_cases():
    assert n_choose_k(5, 0) == 1
    assert n_choose_k(5, 5) == 1
    assert n_choose_k(5, 6) == 0   # k > n
    assert n_choose_k(5, -1) == 0  # k < 0


def test_negative_n_raises():
    with pytest.raises(ValueError):
        n_choose_k(-1, 2)


@given(n=st.integers(0, 40), k=st.integers(0, 40))
def test_symmetry_property(n, k):
    assert n_choose_k(n, k) == n_choose_k(n, n - k)


def test_iter_combinations_count_and_shape():
    combos = list(iter_combinations([1, 2, 3, 4], 2))
    assert len(combos) == n_choose_k(4, 2) == 6
    assert (1, 2) in combos and (3, 4) in combos


def test_k_subsets_sorted():
    subs = list(k_subsets([5, 1, 3], 2))
    assert subs == [(1, 3), (1, 5), (3, 5)]

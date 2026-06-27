import pytest

from lottery_optimizer.algorithms.random_balanced import RandomBalancedOptimizer
from lottery_optimizer.core.validation import SpecError
from lottery_optimizer.games import registry
from lottery_optimizer.metrics.balance import balance_score
from lottery_optimizer.metrics.frequency import digit_frequency
from lottery_optimizer.utils.random import SeededRng


def quina():
    return registry.get("quina")


def test_respects_spec(mini):
    opt = RandomBalancedOptimizer()
    p = opt.optimize(mini, num_tickets=5, marks=3, rng=SeededRng(1))
    assert len(p) == 5
    for t in p:
        assert len(t) == 3
        assert t.numbers == tuple(sorted(set(t.numbers)))
        assert all(mini.contains(n) for n in t.numbers)
    # sem duplicatas
    assert len({t.numbers for t in p}) == 5


def test_reproducible_same_seed():
    opt = RandomBalancedOptimizer()
    a = opt.optimize(quina(), 30, 5, SeededRng(123))
    b = opt.optimize(quina(), 30, 5, SeededRng(123))
    assert [t.numbers for t in a] == [t.numbers for t in b]


def test_different_seed_differs():
    opt = RandomBalancedOptimizer(balanced=False)
    a = opt.optimize(quina(), 30, 5, SeededRng(1))
    b = opt.optimize(quina(), 30, 5, SeededRng(2))
    assert [t.numbers for t in a] != [t.numbers for t in b]


def test_fair_uniform_no_number_favored():
    # modo puro uniforme: nenhuma dezena sistematicamente favorecida (qui-quadrado moderado)
    spec = quina()
    opt = RandomBalancedOptimizer(balanced=False)
    p = opt.optimize(spec, num_tickets=3000, marks=5, rng=SeededRng(42))
    freq = digit_frequency(p)
    pool = spec.pool
    expected = 3000 * 5 / pool  # = 187.5
    chi2 = sum((freq.get(n, 0) - expected) ** 2 / expected for n in spec.number_universe())
    df = pool - 1  # 79
    # qui-quadrado deve ficar perto de df; bound generoso (critico 0.001 ~ 130)
    assert chi2 < 2 * df
    assert min(freq.values()) > 0  # toda dezena aparece


def test_balanced_more_uniform_than_pure():
    spec = quina()
    bal = RandomBalancedOptimizer(balanced=True).optimize(spec, 40, 5, SeededRng(7))
    pure = RandomBalancedOptimizer(balanced=False).optimize(spec, 40, 5, SeededRng(7))
    assert balance_score(bal, spec) >= balance_score(pure, spec)


def test_balanced_spreads_digits(mini):
    # 3 jogos de 3 num universo de 9 -> 9 dezenas usadas, idealmente 1x cada
    p = RandomBalancedOptimizer(balanced=True).optimize(mini, num_tickets=3, marks=3, rng=SeededRng(5))
    freq = digit_frequency(p)
    assert max(freq.values()) - min(freq.values()) <= 1  # bem distribuido


def test_guards():
    opt = RandomBalancedOptimizer()
    with pytest.raises(SpecError):
        opt.optimize(quina(), 5, 99, SeededRng(1))   # marks nao permitido
    with pytest.raises(SpecError):
        opt.optimize(quina(), 0, 5, SeededRng(1))    # num_tickets < 1
    # num_tickets > combinacoes distintas (mini: C(9,3)=84)
    from lottery_optimizer.core.game import GameSpec
    tiny = GameSpec(game_id="tiny", name="Tiny", universe_min=1, universe_max=4, draw_size=3,
                    allowed_ticket_sizes=(3,))
    with pytest.raises(SpecError):
        opt.optimize(tiny, 99, 3, SeededRng(1))      # C(4,3)=4 < 99

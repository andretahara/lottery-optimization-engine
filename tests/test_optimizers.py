import pytest

from lottery_optimizer.algorithms import OPTIMIZERS, RuntimeConfig
from lottery_optimizer.algorithms.simulated_annealing import SimulatedAnnealingOptimizer
from lottery_optimizer.generators import GenerationConstraints, RandomGenerator
from lottery_optimizer.games import registry
from lottery_optimizer.utils.checkpoint import load_checkpoint

SIMPLE = GenerationConstraints(strategy="all_simple")


def initial(game="quina", budget=12, seed=1):
    spec = registry.get(game)
    return spec, RandomGenerator().generate(spec, budget, SIMPLE, seed)


def rc(**kw):
    base = dict(max_iterations=60, restarts=1, population=8, generations=8, grasp_rounds=2)
    base.update(kw)
    return RuntimeConfig(**base)


@pytest.mark.parametrize("name", list(OPTIMIZERS))
def test_no_worse_than_initial(name):
    spec, p0 = initial()
    res = OPTIMIZERS[name]().optimize(p0, spec, 12, None, rc(), seed=5)
    assert res.best_score >= res.initial_score          # nunca piora
    assert res.improvement >= 0


@pytest.mark.parametrize("name", list(OPTIMIZERS))
def test_budget_and_no_duplicates(name):
    spec, p0 = initial()
    res = OPTIMIZERS[name]().optimize(p0, spec, 12, None, rc(), seed=5)
    best = res.best_portfolio
    assert len(best) == 12                              # orcamento preservado
    assert all(len(t) == 5 for t in best)               # tamanhos validos
    assert len({t.numbers for t in best}) == 12         # sem duplicatas
    for t in best:
        assert all(spec.contains(n) for n in t.numbers)


@pytest.mark.parametrize("name", list(OPTIMIZERS))
def test_reproducible(name):
    spec, p0 = initial()
    a = OPTIMIZERS[name]().optimize(p0, spec, 12, None, rc(), seed=9)
    b = OPTIMIZERS[name]().optimize(p0, spec, 12, None, rc(), seed=9)
    assert [t.numbers for t in a.best_portfolio] == [t.numbers for t in b.best_portfolio]
    assert a.best_score == b.best_score


def test_local_search_improves_poor_initial():
    # carteira inicial proposital ruim (jogos quase iguais) -> local search melhora
    spec = registry.get("quina")
    from lottery_optimizer.core.portfolio import Portfolio
    from lottery_optimizer.core.ticket import Ticket
    poor = Portfolio(spec, [Ticket(numbers=(1, 2, 3, 4, 5)), Ticket(numbers=(1, 2, 3, 4, 6)),
                            Ticket(numbers=(1, 2, 3, 4, 7))])
    res = OPTIMIZERS["local_search"]().optimize(poor, spec, 3, None, rc(max_iterations=100), seed=2)
    assert res.improvement > 0                          # melhora real


def test_sa_checkpoint_save_load(tmp_path):
    spec, p0 = initial()
    ckpt = tmp_path / "sa.json"
    res = SimulatedAnnealingOptimizer().optimize(
        p0, spec, 12, None, rc(max_iterations=50, checkpoint_path=str(ckpt), checkpoint_every=10),
        seed=3)
    assert res.checkpoint_path is not None
    data = load_checkpoint(res.checkpoint_path)
    assert "best_score" in data and "best" in data

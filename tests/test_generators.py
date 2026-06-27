import pytest

from lottery_optimizer.core.validation import SpecError
from lottery_optimizer.generators import (
    BalancedRandomGenerator,
    DiversityGenerator,
    GenerationConstraints,
    GreedyCoverageGenerator,
    HybridInitialGenerator,
    RandomGenerator,
)
from lottery_optimizer.games import registry
from lottery_optimizer.metrics.balance import balance_score
from lottery_optimizer.metrics.distance import mean_pairwise_distance

ALL = [RandomGenerator, BalancedRandomGenerator, GreedyCoverageGenerator,
       DiversityGenerator, HybridInitialGenerator]


def simple():
    return GenerationConstraints(strategy="all_simple")


@pytest.mark.parametrize("Gen", ALL)
def test_budget_and_no_duplicates_quina(Gen):
    p = Gen().generate(registry.get("quina"), budget=20, constraints=simple(), seed=1)
    assert len(p) == 20
    assert len({t.numbers for t in p}) == 20            # sem duplicatas
    for t in p:
        assert len(t) == 5                              # all_simple -> tamanho simples (=draw_size)
        assert all(registry.get("quina").contains(n) for n in t.numbers)


@pytest.mark.parametrize("Gen", ALL)
def test_reproducible_same_seed(Gen):
    a = Gen().generate(registry.get("mega-sena"), 15, simple(), seed=7)
    b = Gen().generate(registry.get("mega-sena"), 15, simple(), seed=7)
    assert [t.numbers for t in a] == [t.numbers for t in b]


@pytest.mark.parametrize("Gen", ALL)
def test_works_on_mini(Gen, mini):
    p = Gen().generate(mini, budget=5, constraints=simple(), seed=3)
    assert len(p) == 5


def test_fixed_and_mixed_sizes():
    spec = registry.get("mega-sena")
    fixed = RandomGenerator().generate(
        spec, 6, GenerationConstraints(strategy="fixed", ticket_size=7), seed=1)
    assert all(len(t) == 7 for t in fixed)
    mixed = RandomGenerator().generate(
        spec, 6, GenerationConstraints(strategy="mixed_ticket_sizes", mixed_sizes=(6, 7, 8)), seed=1)
    assert sorted({len(t) for t in mixed}) == [6, 7, 8]


def test_invalid_size_and_budget():
    spec = registry.get("quina")
    with pytest.raises(SpecError):
        RandomGenerator().generate(spec, 5, GenerationConstraints(strategy="fixed", ticket_size=99), seed=1)
    with pytest.raises(SpecError):
        RandomGenerator().generate(spec, 0, simple(), seed=1)


def test_diversity_beats_random_on_distance():
    spec = registry.get("quina")
    div = DiversityGenerator().generate(spec, 15, simple(), seed=2)
    rnd = RandomGenerator().generate(spec, 15, simple(), seed=2)
    assert mean_pairwise_distance(div) >= mean_pairwise_distance(rnd)


def test_balanced_beats_random_on_balance():
    spec = registry.get("quina")
    bal = BalancedRandomGenerator().generate(spec, 16, simple(), seed=4)
    rnd = RandomGenerator().generate(spec, 16, simple(), seed=4)
    assert balance_score(bal, spec) >= balance_score(rnd, spec)

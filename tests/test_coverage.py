from lottery_optimizer.core.coverage import CombinationCoverage
from lottery_optimizer.core.game import GameSpec
from lottery_optimizer.core.portfolio import Portfolio
from lottery_optimizer.core.ticket import Ticket
from lottery_optimizer.core.validation import SpecError
from lottery_optimizer.utils.random import SeededRng


def test_streaming_lazy_count(mini):
    cov = CombinationCoverage(mini)
    t = Ticket(numbers=(1, 2, 3, 4))
    pairs = list(cov.iter_ticket_subsets(t, 2))
    assert len(pairs) == 6  # C(4,2)
    assert pairs == sorted(pairs)  # ordenado/canonico


def test_exact_unique_pairs(mini):
    cov = CombinationCoverage(mini)
    p = Portfolio(mini, [Ticket(numbers=(1, 2, 3)), Ticket(numbers=(1, 2, 4))])
    # pares: jogo1 {12,13,23}, jogo2 {12,14,24}; uniao distinta = 5 (12 comum)
    assert cov.count_unique(p, 2, mode="exact") == 5
    assert cov.raw_count(p, 2) == 6  # 3 + 3 com repeticao


def test_exact_cap_guard():
    # Lotomania: K-subsets do jogo de 50 = C(50,20) ~ 4.7e13 -> exact deve recusar
    spec = GameSpec(game_id="lm", name="LM", universe_min=0, universe_max=99, draw_size=20,
                    allowed_ticket_sizes=(50,), prize_tiers=(0, 20))
    cov = CombinationCoverage(spec)
    p = Portfolio(spec, [Ticket(numbers=tuple(range(0, 50)))])
    try:
        cov.count_unique(p, 20, mode="exact")
        assert False, "deveria recusar exact gigante"
    except SpecError:
        pass


def test_sampled_estimate_matches_exact_small(mini):
    cov = CombinationCoverage(mini)
    # cobre todo o universo com tamanho 4? nao; use cobertura de trincas estimada vs exata
    p = Portfolio(mini, [Ticket(numbers=(1, 2, 3, 4)), Ticket(numbers=(5, 6, 7, 8))])
    exact = cov.count_unique(p, 3, mode="exact")  # 4 + 4 = 8 trincas distintas
    assert exact == 8
    sampled = cov.count_unique(p, 3, mode="sampled", samples=20000, rng=SeededRng(7))
    # estimativa de 8/C(9,3)=8/84 do espaco; tolerancia ampla
    assert abs(sampled - 8) <= 3

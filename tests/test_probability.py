from fractions import Fraction

from lottery_optimizer.core.game import GameSpec
from lottery_optimizer.core.portfolio import Portfolio
from lottery_optimizer.core.probability import ProbabilityModel
from lottery_optimizer.core.ticket import Ticket


def test_total_combinations_real_games():
    assert ProbabilityModel(GameSpec(game_id="q", name="Q", universe_min=1, universe_max=80,
                                     draw_size=5, allowed_ticket_sizes=(5,))).total_combinations() == 24_040_016
    assert ProbabilityModel(GameSpec(game_id="m", name="M", universe_min=1, universe_max=60,
                                     draw_size=6, allowed_ticket_sizes=(6,))).total_combinations() == 50_063_860
    assert ProbabilityModel(GameSpec(game_id="l", name="L", universe_min=1, universe_max=25,
                                     draw_size=15, allowed_ticket_sizes=(15,))).total_combinations() == 3_268_760


def test_equivalent_simple():
    pm = ProbabilityModel(GameSpec(game_id="m", name="M", universe_min=1, universe_max=60,
                                   draw_size=6, allowed_ticket_sizes=(6, 7, 8)))
    assert pm.equivalent_simple(7) == 7
    assert pm.equivalent_simple(8) == 28


def test_unique_vs_raw_coverage_exact_mini(mini):
    # dois jogos de tamanho 4 sobrepostos: (1,2,3,4) e (3,4,5,6)
    p = Portfolio(mini, [Ticket(numbers=(1, 2, 3, 4)), Ticket(numbers=(3, 4, 5, 6))])
    pm = ProbabilityModel(mini)
    # cobertura BRUTA = C(4,3)+C(4,3) = 8
    assert pm.raw_coverage(p) == 8
    # trincas unicas: cada jogo cobre 4 trincas; comum = {(3,4,?)}? (3,4) em ambos mas trinca de 3
    # jogo1 trincas: 123 124 134 234 ; jogo2: 345 346 356 456 ; intersecao vazia -> 8 unicas
    assert pm.unique_coverage(p) == 8


def test_unique_coverage_with_real_overlap(mini):
    # (1,2,3) e (1,2,4): cada cobre 1 trinca; distintas -> 2
    p = Portfolio(mini, [Ticket(numbers=(1, 2, 3)), Ticket(numbers=(1, 2, 4))])
    pm = ProbabilityModel(mini)
    assert pm.raw_coverage(p) == 2
    assert pm.unique_coverage(p) == 2


def test_p_main_is_unique_over_total(mini):
    p = Portfolio(mini, [Ticket(numbers=(1, 2, 3)), Ticket(numbers=(4, 5, 6))])
    pm = ProbabilityModel(mini)
    # 2 trincas unicas / C(9,3)=84
    assert pm.p_main(p) == Fraction(2, 84)


def test_p_main_multiple_ticket(mini):
    # um jogo de tamanho 4 cobre C(4,3)=4 trincas unicas
    p = Portfolio(mini, [Ticket(numbers=(1, 2, 3, 4))])
    assert ProbabilityModel(mini).p_main(p) == Fraction(4, 84)


def test_lower_tier_single_hypergeometric():
    pm = ProbabilityModel(GameSpec(game_id="m", name="M", universe_min=1, universe_max=60,
                                   draw_size=6, allowed_ticket_sizes=(6,)))
    total = sum(pm.p_tier_single(6, h) for h in range(0, 7))
    assert total == Fraction(1, 1)  # distribuicao soma 1

"""Exemplo: inspeciona a spec da Mega-Sena e a matematica de cobertura. Nao gera apostas reais."""

from fractions import Fraction

from lottery_optimizer.core import probability as prob
from lottery_optimizer.disclaimer import DISCLAIMER
from lottery_optimizer.games import registry


def main() -> None:
    print(DISCLAIMER, "\n")
    spec = registry.get("mega-sena")
    print(f"{spec.name}: pool={spec.pool} sorteio={spec.draw_size} marcas={spec.min_marks}-{spec.max_marks}")
    print(f"Espaco amostral C(60,6) = {spec.total_outcomes():,}")
    p = prob.p_main_simple(spec.pool, spec.draw_size)
    print(f"P(premio principal, aposta simples) = 1 em {1 / Fraction(p):,.0f}")
    for marks in (6, 7, 8, 15):
        print(f"  aposta de {marks} marcas = {spec.simple_combinations(marks):,} jogos simples")


if __name__ == "__main__":
    main()

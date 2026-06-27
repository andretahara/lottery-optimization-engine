"""Exemplo: spec da Mega-Sena + matematica de cobertura. Nao gera apostas reais."""

from lottery_optimizer.core.probability import ProbabilityModel
from lottery_optimizer.disclaimer import DISCLAIMER
from lottery_optimizer.games import registry


def main() -> None:
    print(DISCLAIMER, "\n")
    spec = registry.get("mega-sena")
    pm = ProbabilityModel(spec)
    print(f"{spec.name}: universo {spec.universe_min}-{spec.universe_max} "
          f"sorteio={spec.draw_size} tamanhos={spec.allowed_ticket_sizes}")
    print(f"Espaco amostral C(60,6) = {pm.total_combinations():,}")
    for size in (6, 7, 8, 15):
        print(f"  aposta de {size} marcas = {pm.equivalent_simple(size):,} jogos simples")


if __name__ == "__main__":
    main()

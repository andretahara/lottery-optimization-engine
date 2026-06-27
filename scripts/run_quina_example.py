"""Exemplo: spec da Quina + matematica de cobertura. Nao gera apostas reais."""

from lottery_optimizer.core.probability import ProbabilityModel
from lottery_optimizer.disclaimer import DISCLAIMER
from lottery_optimizer.games import registry


def main() -> None:
    print(DISCLAIMER, "\n")
    spec = registry.get("quina")
    pm = ProbabilityModel(spec)
    print(f"{spec.name}: universo {spec.universe_min}-{spec.universe_max} "
          f"sorteio={spec.draw_size} tamanhos={spec.allowed_ticket_sizes}")
    print(f"Espaco amostral C(80,5) = {pm.total_combinations():,}")
    for size in spec.allowed_ticket_sizes:
        print(f"  aposta de {size} marcas = {pm.equivalent_simple(size)} jogos simples")


if __name__ == "__main__":
    main()

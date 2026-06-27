"""Exemplo operacional: Mega-Sena da Virada. MESMA engine, N=60 K=6, score adaptado ao jogo.

Demonstra que nada e especifico da Quina: so muda a GameSpec (via game_id) e os pesos.
"""

from __future__ import annotations

import sys
from pathlib import Path

from lottery_optimizer.core.pricing import PriceError
from lottery_optimizer.disclaimer import DISCLAIMER
from lottery_optimizer import runner

_CONFIG = Path(__file__).parent.parent / "configs" / "mega_sena_virada_example.yaml"


def load_config():
    return runner.load_config(_CONFIG)


def run(config=None, **kw):
    return runner.run_from_config(config or load_config(), **kw)


def main() -> None:  # pragma: no cover
    print(DISCLAIMER, "\n")
    allow = "--allow-example-prices" in sys.argv
    try:
        s = run(allow_example=allow)
    except PriceError as e:
        print(f"PARADO: {e}\nAtualize o preco oficial em {_CONFIG}.")
        sys.exit(2)
    print(f"{s['game']} (N=60, K={s['draw_size']}): {s['num_tickets']} apostas "
          f"(R$ {s['simple_price']} cada), R$ {s['budget']}")
    print(s["sizing_note"])
    print(f"Score {s['initial_score']:.4f} -> {s['best_score']:.4f} (+{s['improvement']:.4f})")
    print(f"Arquivos em {s['output_dir']}\n\n{DISCLAIMER}")


if __name__ == "__main__":  # pragma: no cover
    main()

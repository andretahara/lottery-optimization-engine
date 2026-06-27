import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from lottery_optimizer.core.game import GameSpec


@pytest.fixture
def mini():
    """Jogo artificial pequeno para validacao EXATA: universo 1..9, sorteia 3."""
    return GameSpec(
        game_id="mini", name="Mini", universe_min=1, universe_max=9, draw_size=3,
        allowed_ticket_sizes=(3, 4), prize_tiers=(2, 3),
    )

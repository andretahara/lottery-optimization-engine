"""Carrega GameSpecs dos YAML em configs/. Logica nunca ramifica por nome de loteria.

Parametros conferidos vs regras oficiais CAIXA jun/2026. Mudou regra -> editar o YAML.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from ..core.game import GameSpec

_CONFIG_DIR = Path(__file__).parent / "configs"


@lru_cache(maxsize=1)
def _load_all() -> dict[str, GameSpec]:
    specs: dict[str, GameSpec] = {}
    for path in sorted(_CONFIG_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        spec = GameSpec(**data)
        if spec.slug in specs:
            raise ValueError(f"slug duplicado '{spec.slug}' em {path.name}")
        specs[spec.slug] = spec
    return specs


def available() -> tuple[str, ...]:
    """Slugs registrados, ordenados."""
    return tuple(sorted(_load_all()))


def get(slug: str) -> GameSpec:
    """GameSpec do slug. KeyError se desconhecido."""
    specs = _load_all()
    try:
        return specs[slug]
    except KeyError:
        raise KeyError(f"loteria '{slug}' desconhecida; disponiveis: {', '.join(available())}") from None

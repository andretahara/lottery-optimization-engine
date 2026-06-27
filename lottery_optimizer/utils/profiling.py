"""Profiling basico: tempo e pico de memoria de um bloco. Sem dependencia externa."""

from __future__ import annotations

import time
import tracemalloc
from contextlib import contextmanager

from .logging import get_logger

_log = get_logger("lottery_optimizer.profiling")


@contextmanager
def profile_block(name: str, *, track_memory: bool = True):
    """Mede tempo (e opcionalmente pico de memoria via tracemalloc) de um bloco.

    Uso:
        with profile_block("otimizacao") as p:
            ...
        print(p["elapsed"], p["peak_kb"])
    """
    result: dict[str, float] = {}
    if track_memory:
        tracemalloc.start()
    t0 = time.perf_counter()
    try:
        yield result
    finally:
        result["elapsed"] = time.perf_counter() - t0
        if track_memory:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            result["peak_kb"] = peak / 1024
        _log.info("profile[%s]: %.3fs%s", name, result["elapsed"],
                  f", pico {result.get('peak_kb', 0):.0f}KB" if track_memory else "")

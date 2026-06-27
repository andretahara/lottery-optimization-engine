from lottery_optimizer.disclaimer import DISCLAIMER

import scripts.dry_run_bolao as dry


def test_full_flow_small_game(tmp_path):
    s = dry.run(seed=1, budget=8, output_base=tmp_path)
    assert s["apostas"] == 8
    for f in ["jogos.csv", "relatorio.txt", "jogos.xlsx", "frequencia_dezenas.png",
              "score_history.png"]:
        assert (tmp_path / f).exists(), f
    report = (tmp_path / "relatorio.txt").read_text(encoding="utf-8")
    assert DISCLAIMER in report
    # custo de exemplo aparece como estimativa (nao oficial)
    assert s["estimativa"] is True


def test_reproducible_same_seed(tmp_path):
    a = dry.run(seed=42, budget=6, output_base=tmp_path / "a")
    b = dry.run(seed=42, budget=6, output_base=tmp_path / "b")
    ca = (tmp_path / "a" / "jogos.csv").read_text(encoding="utf-8")
    cb = (tmp_path / "b" / "jogos.csv").read_text(encoding="utf-8")
    assert ca == cb
    assert a["score"] == b["score"]


def test_runbook_docs_have_disclaimer():
    from pathlib import Path
    for doc in ["docs/RUNBOOK_BOLAO.md", "docs/CHECKLIST_PRE_REGISTRO.md"]:
        assert "mesma probabilidade individual" in Path(doc).read_text(encoding="utf-8")

from pathlib import Path

from typer.testing import CliRunner

from lottery_optimizer.cli.main import app
from lottery_optimizer.disclaimer import DISCLAIMER

runner = CliRunner()


def _only_subdir(base: Path) -> Path:
    subs = [d for d in base.iterdir() if d.is_dir()]
    assert len(subs) == 1
    return subs[0]


def test_list_games():
    r = runner.invoke(app, ["list-games"])
    assert r.exit_code == 0
    assert "quina" in r.stdout
    assert "otimiz" in r.stdout  # disclaimer (rich pode quebrar linha)


def test_inspect_and_validate():
    r = runner.invoke(app, ["inspect-game", "mega-sena"])
    assert r.exit_code == 0 and "50,063,860" in r.stdout
    r2 = runner.invoke(app, ["validate-config", "quina"])
    assert r2.exit_code == 0 and "OK" in r2.stdout
    r3 = runner.invoke(app, ["validate-config", "inexistente"])
    assert r3.exit_code != 0


def test_generate_creates_files(tmp_path):
    r = runner.invoke(app, ["generate", "quina", "--budget", "6", "--seed", "1",
                            "--output-dir", str(tmp_path)])
    assert r.exit_code == 0, r.stdout
    run = _only_subdir(tmp_path)
    for f in ["jogos.csv", "relatorio.txt", "jogos.xlsx", "frequencia_dezenas.png",
              "distribuicao_sobreposicao.png", "cobertura_por_subconjunto.png", "config.log"]:
        assert (run / f).exists(), f
    assert DISCLAIMER in (run / "relatorio.txt").read_text(encoding="utf-8")


def test_optimize_creates_files(tmp_path):
    r = runner.invoke(app, ["optimize", "quina", "--budget", "5", "--optimizer", "local_search",
                            "--iterations", "15", "--seed", "2", "--output-dir", str(tmp_path)])
    assert r.exit_code == 0, r.stdout
    run = _only_subdir(tmp_path)
    assert (run / "jogos.csv").exists()
    assert (run / "score_history.png").exists()


def test_report_export_compare(tmp_path):
    g = runner.invoke(app, ["generate", "quina", "--budget", "5", "--seed", "1",
                            "--output-dir", str(tmp_path / "a")])
    assert g.exit_code == 0
    csv_a = _only_subdir(tmp_path / "a") / "jogos.csv"
    runner.invoke(app, ["generate", "quina", "--budget", "5", "--seed", "99",
                       "--output-dir", str(tmp_path / "b")])
    csv_b = _only_subdir(tmp_path / "b") / "jogos.csv"
    rep = runner.invoke(app, ["report", "quina", str(csv_a)])
    assert rep.exit_code == 0 and "Probabilidade teorica" in rep.stdout
    exp = runner.invoke(app, ["export", "quina", str(csv_a), "--output-dir", str(tmp_path / "e")])
    assert exp.exit_code == 0
    cmp = runner.invoke(app, ["compare", "quina", str(csv_a), str(csv_b)])
    assert cmp.exit_code == 0 and "Melhor score" in cmp.stdout


def test_benchmark(tmp_path):
    r = runner.invoke(app, ["benchmark", "quina", "--budget", "6", "--seeds", "1",
                            "--algorithms", "random,local_search", "--iterations", "20",
                            "--output-dir", str(tmp_path)])
    assert r.exit_code == 0, r.stdout
    assert "Vencedor" in r.stdout
    run = _only_subdir(tmp_path)
    assert (run / "benchmark.csv").exists()

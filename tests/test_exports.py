import pytest

from lottery_optimizer.core.game import GameSpec
from lottery_optimizer.core.portfolio import Portfolio
from lottery_optimizer.core.ticket import Ticket
from lottery_optimizer.disclaimer import DISCLAIMER
from lottery_optimizer.export import csv_exporter, excel_exporter, report_exporter


def spec():
    return GameSpec(slug="mega-sena", name="Mega-Sena", pool=60, draw_size=6,
                    min_marks=6, max_marks=15, prize_tiers=(4, 5, 6))


def portfolio():
    return Portfolio([Ticket(numbers=(1, 2, 3, 4, 5, 6)), Ticket(numbers=(7, 8, 9, 10, 11, 12))])


def test_csv_export_roundtrip(tmp_path):
    p = csv_exporter.export_csv(portfolio(), tmp_path / "out.csv")
    text = p.read_text(encoding="utf-8")
    assert "ticket,numbers" in text
    assert "1 2 3 4 5 6" in text


def test_report_contains_disclaimer():
    report = report_exporter.build_report(portfolio(), spec())
    assert DISCLAIMER in report
    assert "Mega-Sena" in report


def test_excel_stub_not_implemented(tmp_path):
    with pytest.raises(NotImplementedError):
        excel_exporter.export_excel(portfolio(), tmp_path / "x.xlsx")

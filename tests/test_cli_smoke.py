from types import SimpleNamespace

from src.cli import analyze_main, batch_main, main


class DummyReportGenerator:
    def save_report(self, report, report_format):
        return f"outputs/dummy_report.{report_format}"


class DummyAnalyzer:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.report_generator = DummyReportGenerator()

    def analyze(self, pdf_path, company_name="", report_year=0):
        return SimpleNamespace(
            risk_assessment=SimpleNamespace(
                risk_level=SimpleNamespace(value="中"),
                total_score=18.5,
                fraud_patterns=[1, 2],
            ),
            investment_recommendation="保持观察。",
        )

    def batch_analyze(self, pdf_files, output_dir, report_format="markdown"):
        return [object() for _ in pdf_files]


def test_analyze_main_smoke_uses_shared_entrypoint(monkeypatch, capsys):
    monkeypatch.setattr("src.cli.configure_logging", lambda verbose=False: None)
    monkeypatch.setattr(
        "src.cli.validate_pdf_file",
        lambda path: {"valid": True, "file_info": {"name": "demo.pdf", "size_mb": 1.23}, "errors": []},
    )
    monkeypatch.setattr("src.cli.FinancialFraudAnalyzer", DummyAnalyzer)

    exit_code = analyze_main(["demo.pdf", "--output", "outputs", "--format", "json"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "分析完成" in captured.out
    assert "dummy_report.json" in captured.out


def test_batch_main_smoke_uses_shared_entrypoint(monkeypatch, capsys, tmp_path):
    pdf_path = tmp_path / "demo.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 demo")

    monkeypatch.setattr("src.cli.configure_logging", lambda verbose=False: None)
    monkeypatch.setattr(
        "src.cli.validate_pdf_file",
        lambda path: {"valid": True, "file_info": {"name": "demo.pdf", "size_mb": 1.23}, "errors": []},
    )
    monkeypatch.setattr("src.cli.FinancialFraudAnalyzer", DummyAnalyzer)

    exit_code = batch_main([str(pdf_path), "--output", "outputs", "--format", "markdown"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "批量分析完成" in captured.out
    assert "成功分析: 1" in captured.out


def test_main_help_lists_shared_subcommands(capsys):
    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "analyze" in captured.out
    assert "batch" in captured.out

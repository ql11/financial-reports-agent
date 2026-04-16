import json
from pathlib import Path

import pytest

from src.core.analyzer import FinancialFraudAnalyzer
from src.core.data_extractor import PDFDataExtractor


ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "tests" / "fixtures" / "pdf_regression_cases.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", CASES, ids=[Path(case["path"]).name for case in CASES])
def test_extract_from_pdf_matches_sample_regressions(case):
    extractor = PDFDataExtractor()

    data = extractor.extract_from_pdf(str(ROOT / case["path"]))

    assert data.company_name == case["company_name"]
    assert data.stock_code == case["stock_code"]
    assert data.report_year == case["report_year"]

    for field, expected in case["current"].items():
        assert getattr(data.current_year, field) == expected

    previous = data.historical_data[data.report_year - 1]
    for field, expected in case.get("previous", {}).items():
        assert getattr(previous, field) == expected

    for key, expected in case.get("notes", {}).items():
        assert data.notes[key] == expected

    for key in case.get("missing_notes", []):
        assert key not in data.notes


def test_chongqing_sample_report_keeps_review_override_consistent(tmp_path):
    analyzer = FinancialFraudAnalyzer(output_dir=str(tmp_path))

    report = analyzer.analyze(str(ROOT / "inputs" / "H2_AN202604161821261879_1.pdf"))
    markdown = report.to_markdown()

    assert "原文摘录（第2页）" in markdown
    assert "## 投资建议" in markdown
    assert "## 执行摘要" in markdown
    assert "**待核验**。审计意见为“带持续经营重大不确定性段落的无保留意见”" in markdown
    assert "- 待核验：证据链未闭合或审计意见存在重大不确定性，暂不采用自动投资建议。" in markdown
    assert "仔细阅读审计报告说明段" in markdown
    assert "**极高风险**：建议立即停止投资，深入调查公司财务状况" not in markdown
    assert "重点关注现金流异常和审计问题" not in markdown

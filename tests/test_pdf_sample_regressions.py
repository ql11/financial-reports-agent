import json
from pathlib import Path

import pytest

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

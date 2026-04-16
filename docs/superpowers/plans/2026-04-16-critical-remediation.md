# Critical Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the highest-impact correctness and output workflow issues, then add a maintained roadmap document with future expansion directions.

**Architecture:** Keep the current package structure and repair behavior in place. Analysis becomes separate from persistence, serialization preserves assessor-computed values, and model-level ratio computation is completed so downstream rules operate on real data.

**Tech Stack:** Python 3.9+, pytest, dataclasses, pathlib

---

### Task 1: Add Regression Tests For Ratio And Serialization Behavior

**Files:**
- Create: `tests/test_models.py`
- Test: `tests/test_models.py`

- [ ] **Step 1: Write the failing tests**

```python
from src.models.financial_data import FinancialStatement
from src.models.fraud_indicators import RiskLevel
from src.models.report_model import RiskAssessment


def test_financial_statement_calculates_turnover_ratios():
    statement = FinancialStatement(
        operating_revenue=200.0,
        gross_profit=80.0,
        net_profit=20.0,
        total_assets=100.0,
        total_equity=50.0,
        total_liabilities=50.0,
        inventory=25.0,
        accounts_receivable=40.0,
    )

    statement.calculate_ratios()

    assert statement.inventory_turnover == 8.0
    assert statement.receivables_turnover == 5.0
    assert statement.total_asset_turnover == 2.0


def test_risk_assessment_to_dict_preserves_existing_score_and_level():
    assessment = RiskAssessment(total_score=31.5, risk_level=RiskLevel.HIGH)

    payload = assessment.to_dict()

    assert payload["total_score"] == 31.5
    assert payload["risk_level"] == "高"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_models.py -v`
Expected: FAIL because turnover ratios remain `0.0` and/or risk serialization recomputes defaults.

- [ ] **Step 3: Write minimal implementation**

Update `src/models/financial_data.py` and `src/models/report_model.py` so:

```python
if self.inventory > 0 and self.operating_revenue > 0:
    self.inventory_turnover = self.operating_revenue / self.inventory

if self.accounts_receivable > 0 and self.operating_revenue > 0:
    self.receivables_turnover = self.operating_revenue / self.accounts_receivable

if self.total_assets > 0 and self.operating_revenue > 0:
    self.total_asset_turnover = self.operating_revenue / self.total_assets
```

and:

```python
def to_dict(self) -> Dict[str, Any]:
    return {
        "total_score": self.total_score,
        "risk_level": self.risk_level.value,
        "fraud_patterns": [pattern.to_dict() for pattern in self.fraud_patterns],
        "key_risks": self.key_risks,
        "recommendations": self.recommendations,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_models.py src/models/financial_data.py src/models/report_model.py
git commit -m "fix: preserve risk serialization and turnover ratios"
```

### Task 2: Add Regression Tests For Save Flow

**Files:**
- Create: `tests/test_analyzer_workflow.py`
- Modify: `src/core/analyzer.py`
- Modify: `main.py`
- Modify: `scripts/batch_analyze.py`
- Test: `tests/test_analyzer_workflow.py`

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path
from types import SimpleNamespace

from src.core.analyzer import FinancialFraudAnalyzer
from src.models.report_model import AnalysisReport


class StubExtractor:
    def extract_from_pdf(self, pdf_path):
        return SimpleNamespace(
            company_name="测试公司",
            report_year=2025,
            auditor="审计机构",
            audit_opinion="标准无保留意见",
            current_year=SimpleNamespace(),
            historical_data={},
            notes={},
            get_growth_rate=lambda metric, years=1: 0.0,
        )


class StubDetector:
    def detect_fraud_patterns(self, financial_data):
        return []


class StubAssessor:
    def assess_risk(self, fraud_patterns, financial_data):
        return SimpleNamespace(
            total_score=0.0,
            risk_level=SimpleNamespace(value="低"),
            fraud_patterns=[],
            key_risks=[],
            recommendations=[],
        )


class RecordingReportGenerator:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.saved_formats = []

    def generate_report(self, financial_data, financial_analysis, risk_assessment, fraud_patterns):
        report = AnalysisReport()
        report.company_name = financial_data.company_name
        report.report_year = financial_data.report_year
        report.risk_assessment = risk_assessment
        report.investment_recommendation = "保持观察"
        return report

    def save_report(self, report, fmt):
        self.saved_formats.append(fmt)
        return str(self.output_dir / f"report.{fmt}")

    def print_report_summary(self, report):
        return None


def build_analyzer(tmp_path):
    analyzer = FinancialFraudAnalyzer(output_dir=str(tmp_path))
    analyzer.data_extractor = StubExtractor()
    analyzer.fraud_detector = StubDetector()
    analyzer.risk_assessor = StubAssessor()
    analyzer.report_generator = RecordingReportGenerator(tmp_path)
    analyzer._analyze_financials = lambda data: SimpleNamespace(
        profitability_ratios={},
        solvency_ratios={},
        operation_ratios={},
        growth_ratios={},
        trends={},
        industry_comparisons={},
        anomalies=[],
    )
    return analyzer


def test_analyze_does_not_save_report_implicitly(tmp_path):
    analyzer = build_analyzer(tmp_path)

    analyzer.analyze("dummy.pdf")

    assert analyzer.report_generator.saved_formats == []


def test_batch_analyze_saves_once_per_report_in_requested_format(tmp_path):
    analyzer = build_analyzer(tmp_path)

    reports = analyzer.batch_analyze(["a.pdf", "b.pdf"], output_dir=str(tmp_path), report_format="json")

    assert len(reports) == 2
    assert analyzer.report_generator.saved_formats == ["json", "json"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_analyzer_workflow.py -v`
Expected: FAIL because `analyze()` saves Markdown implicitly and batch analysis does not accept/propagate `report_format`.

- [ ] **Step 3: Write minimal implementation**

Update `src/core/analyzer.py` so:

```python
def analyze(... ) -> AnalysisReport:
    ...
    report = self.report_generator.generate_report(...)
    self.report_generator.print_report_summary(report)
    return report


def batch_analyze(self, pdf_files, output_dir="reports", report_format="markdown", save_reports=True):
    ...
    report = self.analyze(pdf_file)
    if save_reports:
        self.report_generator.save_report(report, report_format)
```

Update callers so batch commands pass the requested format:

```python
reports = analyzer.batch_analyze(valid_files, args.output, report_format=args.format)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_analyzer_workflow.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_analyzer_workflow.py src/core/analyzer.py main.py scripts/batch_analyze.py
git commit -m "fix: separate analysis from persistence"
```

### Task 3: Add The Living Project Roadmap

**Files:**
- Create: `PROJECT_ROADMAP.md`

- [ ] **Step 1: Write the roadmap document**

Create `PROJECT_ROADMAP.md` with sections covering:

```markdown
# Project Roadmap

## Purpose
- Keep project improvement work visible and update this file whenever major remediation or feature work lands.

## Current Priorities
- Correct output workflow
- Preserve scoring consistency
- Improve metric completeness

## Phase 1: Stability And Trustworthiness
- Expand extractor test coverage
- Wire config thresholds and weights into runtime logic
- Unify logging and error reporting

## Phase 2: Analysis Depth
- Multi-year trend extraction
- Industry benchmark comparison
- Cross-statement consistency engine

## Phase 3: Productization
- Structured CLI/API contract
- Batch concurrency
- Report templates and export formats

## Functional Expansion Directions
- Data source adapters beyond PDF
- Company history and governance knowledge base
- Industry peer comparison
- Analyst review workflow
- Evidence traceability per fraud signal
```

- [ ] **Step 2: Verify the roadmap file content**

Run: `Get-Content -Raw PROJECT_ROADMAP.md`
Expected: File exists and contains stability priorities plus functional expansion directions.

- [ ] **Step 3: Commit**

```bash
git add PROJECT_ROADMAP.md
git commit -m "docs: add project roadmap"
```

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

    def generate_report(
        self, financial_data, financial_analysis, risk_assessment, fraud_patterns
    ):
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

    reports = analyzer.batch_analyze(
        ["a.pdf", "b.pdf"], output_dir=str(tmp_path), report_format="json"
    )

    assert len(reports) == 2
    assert analyzer.report_generator.saved_formats == ["json", "json"]

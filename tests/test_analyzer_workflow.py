from pathlib import Path
from types import SimpleNamespace
import logging

from src.core.analyzer import FinancialFraudAnalyzer
from src.core.risk_assessor import RiskAssessor
from src.models.financial_data import FinancialData, FinancialStatement
from src.models.fraud_indicators import FraudIndicator, FraudPattern, FraudType, RiskLevel
from src.models.report_model import AnalysisReport
from src.models.report_model import FinancialAnalysis


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


def test_detect_anomalies_uses_threshold_config(tmp_path):
    thresholds_path = tmp_path / "thresholds.yaml"
    thresholds_path.write_text(
        """
profitability:
  gross_margin:
    warning: 50.0
  net_margin:
    warning: 3.0
solvency:
  debt_ratio:
    warning: 90.0
  current_ratio:
    warning: 0.5
growth:
  revenue_growth:
    critical: -20.0
  cash_flow_growth:
    warning: -30.0
fraud_detection:
  cash_revenue_ratio:
    warning: 0.95
  receivable_ratio:
    warning: 0.5
  cash_profit_ratio:
    warning: 0.5
  receivables_growth_vs_revenue:
    spread: 10.0
    warning: 20.0
  inventory_growth_vs_revenue:
    spread: 15.0
    warning: 20.0
""".strip(),
        encoding="utf-8",
    )

    analyzer = FinancialFraudAnalyzer(
        output_dir=str(tmp_path), thresholds_config_path=str(thresholds_path)
    )
    statement = FinancialStatement(
        operating_revenue=100.0,
        gross_profit=40.0,
        net_profit=10.0,
        cash_from_sales=90.0,
        net_cash_flow_operating=20.0,
        total_assets=100.0,
        total_liabilities=80.0,
        current_assets=80.0,
        current_liabilities=100.0,
    )
    statement.calculate_ratios()
    data = FinancialData(report_year=2025, current_year=statement)
    analysis = FinancialAnalysis(
        growth_ratios={"营业收入增长率": 0.0, "经营活动现金流增长率": 0.0}
    )

    anomalies = analyzer._detect_anomalies(data, analysis)

    gross_margin = next(item for item in anomalies if item["metric"] == "毛利率")
    cash_revenue = next(item for item in anomalies if item["metric"] == "现金收入比")

    assert gross_margin["threshold"] == 50.0
    assert cash_revenue["threshold"] == "95%"
    assert not any(item["metric"] == "资产负债率" for item in anomalies)
    assert not any(item["metric"] == "流动比率" for item in anomalies)


def test_risk_assessor_uses_weight_and_level_configs(tmp_path):
    weights_path = tmp_path / "weights.yaml"
    weights_path.write_text(
        """
fraud_pattern_weights:
  revenue_profit_divergence: 2.0
risk_level_base_scores:
  critical: 12.0
  high: 9.0
  medium: 3.0
  low: 1.0
risk_level_thresholds:
  critical: 45.0
  high: 35.0
  medium: 25.0
max_risk_bonus:
  critical: 0.0
  high: 0.0
  medium: 0.0
  low: 0.0
density_rules:
  power: 1.0
  scale: 0.0
  critical_density: 1.0
  critical_score_floor: 999.0
breadth_rules:
  per_pattern: 0.0
  max_score: 0.0
concentration_rules:
  power: 1.0
  scale: 0.0
financial_severity:
  net_profit_negative: 0.0
  loss_ratio_over_5pct: 0.0
  revenue_growth_below_negative_20: 0.0
  revenue_growth_below_negative_10: 0.0
  operating_cash_flow_negative: 0.0
  debt_ratio_above_70: 0.0
  debt_ratio_above_60: 0.0
critical_pattern_rules:
  critical_min_score: 999.0
  critical_min_density: 1.0
  high_floor_for_critical_pattern: true
score_caps:
  total: 50.0
""".strip(),
        encoding="utf-8",
    )

    assessor = RiskAssessor(weights_config_path=str(weights_path))
    pattern = FraudPattern(
        name="业绩背离",
        description="测试模式",
        indicators=[
            FraudIndicator(
                type=FraudType.REVENUE_MANIPULATION,
                name="测试指标",
                description="测试说明",
                risk_level=RiskLevel.HIGH,
                score=1.0,
            )
        ],
    )
    data = FinancialData(
        report_year=2025,
        current_year=FinancialStatement(
            operating_revenue=100.0,
            net_profit=10.0,
            net_cash_flow_operating=10.0,
            total_assets=100.0,
            total_liabilities=20.0,
        ),
    )
    data.current_year.calculate_ratios()

    assessment = assessor.assess_risk([pattern], data)

    assert assessment.total_score == 18.0
    assert assessment.risk_level == RiskLevel.LOW


def test_analyze_logs_progress_instead_of_printing(tmp_path, caplog, capsys):
    analyzer = build_analyzer(tmp_path)

    with caplog.at_level(logging.INFO):
        analyzer.analyze("dummy.pdf")

    stdout = capsys.readouterr().out

    assert stdout == ""
    assert "开始财报造假分析" in caplog.text
    assert "提取财务数据" in caplog.text
    assert "生成分析报告" in caplog.text

from src.models.financial_data import FinancialStatement
from src.models.fraud_indicators import FraudIndicator
from src.models.fraud_indicators import FraudPattern
from src.models.fraud_indicators import FraudType
from src.models.fraud_indicators import RiskLevel
from src.models.report_model import AnalysisReport
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
    pattern = FraudPattern(
        name="测试模式",
        description="用于验证序列化不应重算分数",
        indicators=[
            FraudIndicator(
                type=FraudType.REVENUE_MANIPULATION,
                name="测试指标",
                description="测试指标说明",
                risk_level=RiskLevel.MEDIUM,
                score=2.0,
            )
        ],
    )
    pattern.calculate_score()
    assessment = RiskAssessment(
        total_score=31.5, risk_level=RiskLevel.HIGH, fraud_patterns=[pattern]
    )

    payload = assessment.to_dict()

    assert payload["total_score"] == 31.5
    assert payload["risk_level"] == "高"


def test_analysis_report_markdown_includes_indicator_evidence():
    indicator = FraudIndicator(
        type=FraudType.REVENUE_MANIPULATION,
        name="收入确认异常",
        description="期末收入确认节奏异常",
        risk_level=RiskLevel.HIGH,
        score=3.0,
        evidence=[
            "营业收入同比增长 35.2%，但经营现金流净额同比下降 48.7%。",
            "附注披露第四季度收入占全年收入 54.1%。",
        ],
    )
    pattern = FraudPattern(
        name="收入操纵风险",
        description="收入确认与现金回款出现明显背离",
        indicators=[indicator],
    )
    pattern.calculate_score()
    assessment = RiskAssessment(
        total_score=pattern.total_score,
        risk_level=RiskLevel.HIGH,
        fraud_patterns=[pattern],
    )
    report = AnalysisReport(
        report_id="FR-TEST",
        company_name="测试公司",
        stock_code="000001",
        report_year=2025,
        risk_assessment=assessment,
        investment_recommendation="保持谨慎",
    )

    markdown = report.to_markdown()

    assert "### 发现的造假模式" in markdown
    assert "##### 风险信号" in markdown
    assert "收入确认异常" in markdown
    assert "###### 证据片段" in markdown
    assert "营业收入同比增长 35.2%" in markdown
    assert "附注披露第四季度收入占全年收入 54.1%" in markdown

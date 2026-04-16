from src.models.financial_data import FinancialStatement
from src.models.fraud_indicators import FraudIndicator
from src.models.fraud_indicators import FraudPattern
from src.models.fraud_indicators import FraudType
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

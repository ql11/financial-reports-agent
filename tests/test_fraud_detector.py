from src.core.fraud_detector import FraudDetector
from src.models.financial_data import FinancialData, FinancialStatement


def build_financial_data(current, previous=None, notes=None):
    current.calculate_ratios()
    data = FinancialData(report_year=2025, current_year=current, notes=notes or {})
    if previous is not None:
        previous.calculate_ratios()
        data.historical_data[2024] = previous
    return data


def test_fraud_detector_uses_config_for_divergence_thresholds_and_scores(tmp_path):
    thresholds_path = tmp_path / "thresholds.yaml"
    thresholds_path.write_text(
        """
fraud_detection:
  revenue_profit_divergence:
    revenue_decline: -1.0
    profit_growth: 5.0
    score: 4.2
  cash_flow_divergence:
    profit_growth: 5.0
    cash_flow_decline: -5.0
    score: 4.6
""".strip(),
        encoding="utf-8",
    )

    detector = FraudDetector(thresholds_config_path=str(thresholds_path))
    current = FinancialStatement(
        operating_revenue=98.0,
        net_profit=106.0,
        net_cash_flow_operating=90.0,
    )
    previous = FinancialStatement(
        operating_revenue=100.0,
        net_profit=100.0,
        net_cash_flow_operating=100.0,
    )
    data = build_financial_data(current=current, previous=previous)

    patterns = detector.detect_fraud_patterns(data)
    pattern_map = {pattern.name: pattern for pattern in patterns}

    revenue_pattern = pattern_map["业绩背离模式"]
    cash_flow_pattern = pattern_map["现金流异常模式"]

    assert revenue_pattern.indicators[0].score == 4.2
    assert cash_flow_pattern.indicators[0].score == 4.6


def test_fraud_detector_uses_config_for_ratio_and_related_party_thresholds(tmp_path):
    thresholds_path = tmp_path / "thresholds.yaml"
    thresholds_path.write_text(
        """
fraud_detection:
  cash_revenue_ratio:
    warning: 0.95
    score: 4.1
  receivable_ratio:
    warning: 0.15
    score: 4.3
  related_party_transactions:
    percentage_threshold: 10.0
    score: 4.7
""".strip(),
        encoding="utf-8",
    )

    detector = FraudDetector(thresholds_config_path=str(thresholds_path))
    current = FinancialStatement(
        operating_revenue=100.0,
        net_profit=20.0,
        cash_from_sales=90.0,
        accounts_receivable=20.0,
    )
    data = build_financial_data(
        current=current,
        notes={"related_party_transactions": "12%"},
    )

    patterns = detector.detect_fraud_patterns(data)
    pattern_map = {pattern.name: pattern for pattern in patterns}

    fictitious_pattern = pattern_map["虚构收入嫌疑模式"]
    related_party_pattern = pattern_map["关联交易异常模式"]

    indicator_scores = {indicator.name: indicator.score for indicator in fictitious_pattern.indicators}

    assert indicator_scores["现金收入比过低"] == 4.1
    assert indicator_scores["应收账款占收入比过高"] == 4.3
    assert related_party_pattern.indicators[0].score == 4.7

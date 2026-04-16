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


def test_fraud_detector_uses_config_for_capacity_and_asset_overstatement(tmp_path):
    thresholds_path = tmp_path / "thresholds.yaml"
    thresholds_path.write_text(
        """
fraud_detection:
  capacity_anomalies:
    total_asset_turnover_warning: 0.6
    score: 3.2
  asset_overstatement:
    total_asset_turnover_warning: 0.6
    asset_growth_warning: 5.0
    revenue_growth_ceiling: 2.0
    score: 3.6
""".strip(),
        encoding="utf-8",
    )

    detector = FraudDetector(thresholds_config_path=str(thresholds_path))
    current = FinancialStatement(
        operating_revenue=105.0,
        total_assets=200.0,
        net_profit=10.0,
    )
    previous = FinancialStatement(
        operating_revenue=104.0,
        total_assets=180.0,
        net_profit=10.0,
    )
    data = build_financial_data(current=current, previous=previous)

    patterns = detector.detect_fraud_patterns(data)
    pattern_map = {pattern.name: pattern for pattern in patterns}

    capacity_pattern = pattern_map["产能与投资异常模式"]
    asset_pattern = pattern_map["资产高估模式"]

    assert capacity_pattern.indicators[0].score == 3.2
    assert asset_pattern.indicators[0].score == 3.6


def test_fraud_detector_uses_config_for_cross_statement_and_cash_flow_quality(tmp_path):
    thresholds_path = tmp_path / "thresholds.yaml"
    thresholds_path.write_text(
        """
fraud_detection:
  cross_statement_inconsistency:
    cash_profit_ratio_warning: 0.6
    cash_profit_ratio_score: 4.1
    profit_positive_cash_negative_score: 4.8
    check_failed_score: 4.5
  cash_flow_quality:
    free_cash_flow_negative_score: 4.4
    cash_balance_interest_mismatch_score: 4.9
""".strip(),
        encoding="utf-8",
    )

    detector = FraudDetector(thresholds_config_path=str(thresholds_path))
    current = FinancialStatement(
        operating_revenue=100.0,
        total_assets=100.0,
        net_profit=100.0,
        net_cash_flow_operating=40.0,
        net_cash_flow_investing=-50.0,
    )
    data = build_financial_data(
        current=current,
        notes={"cross_statement_check_failed": "现金变动与现金流量表不一致"},
    )

    patterns = detector.detect_fraud_patterns(data)
    pattern_map = {pattern.name: pattern for pattern in patterns}

    cross_pattern = pattern_map["报表勾稽异常模式"]
    cash_flow_pattern = pattern_map["现金流质量异常模式"]

    cross_scores = {indicator.name: indicator.score for indicator in cross_pattern.indicators}
    cash_scores = {indicator.name: indicator.score for indicator in cash_flow_pattern.indicators}

    assert cross_scores["经营现金流与净利润严重背离"] == 4.1
    assert cross_scores["报表勾稽关系不匹配"] == 4.5
    assert cash_scores["自由现金流为负但净利润为正"] == 4.4

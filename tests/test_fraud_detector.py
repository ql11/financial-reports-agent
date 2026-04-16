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


def test_fraud_detector_uses_config_for_expense_and_liability_patterns(tmp_path):
    thresholds_path = tmp_path / "thresholds.yaml"
    thresholds_path.write_text(
        """
fraud_detection:
  expense_capitalization:
    rd_capitalization_ratio_warning: 0.4
    rd_capitalization_ratio_score: 4.2
    depreciation_policy_change_score: 3.8
  liability_concealment:
    contingent_liabilities_score: 3.7
    off_balance_sheet_items_score: 4.4
""".strip(),
        encoding="utf-8",
    )

    detector = FraudDetector(thresholds_config_path=str(thresholds_path))
    current = FinancialStatement(operating_revenue=100.0, total_assets=100.0, net_profit=10.0)
    data = build_financial_data(
        current=current,
        notes={
            "rd_capitalization_ratio": "0.6",
            "depreciation_policy_change": True,
            "contingent_liabilities": "存在大额未决诉讼",
            "off_balance_sheet_items": True,
        },
    )

    patterns = detector.detect_fraud_patterns(data)
    pattern_map = {pattern.name: pattern for pattern in patterns}

    expense_pattern = pattern_map["费用资本化模式"]
    liability_pattern = pattern_map["负债隐瞒模式"]

    expense_scores = {indicator.name: indicator.score for indicator in expense_pattern.indicators}
    liability_scores = {
        indicator.name: indicator.score for indicator in liability_pattern.indicators
    }

    assert expense_scores["研发费用资本化比例异常"] == 4.2
    assert expense_scores["折旧政策变更"] == 3.8
    assert liability_scores["或有事项披露不足"] == 3.7
    assert liability_scores["表外融资嫌疑"] == 4.4


def test_fraud_detector_uses_config_for_estimate_and_auditor_patterns(tmp_path):
    thresholds_path = tmp_path / "thresholds.yaml"
    thresholds_path.write_text(
        """
fraud_detection:
  accounting_estimate_changes:
    accounting_estimate_changes_score: 3.6
    bad_debt_ratio_decreased_score: 4.5
  auditor_change:
    auditor_change_score: 4.6
    audit_fee_abnormal_score: 3.3
""".strip(),
        encoding="utf-8",
    )

    detector = FraudDetector(thresholds_config_path=str(thresholds_path))
    current = FinancialStatement(operating_revenue=100.0, total_assets=100.0, net_profit=10.0)
    data = build_financial_data(
        current=current,
        notes={
            "accounting_estimate_changes": "延长固定资产折旧年限",
            "bad_debt_ratio_decreased": True,
            "auditor_change": "更换会计师事务所",
            "audit_fee_abnormal": True,
        },
    )

    patterns = detector.detect_fraud_patterns(data)
    pattern_map = {pattern.name: pattern for pattern in patterns}

    estimate_pattern = pattern_map["会计估计变更模式"]
    auditor_pattern = pattern_map["审计师变更模式"]

    estimate_scores = {
        indicator.name: indicator.score for indicator in estimate_pattern.indicators
    }
    auditor_scores = {indicator.name: indicator.score for indicator in auditor_pattern.indicators}

    assert estimate_scores["会计估计变更"] == 3.6
    assert estimate_scores["坏账准备计提比例下降"] == 4.5
    assert auditor_scores["审计师变更"] == 4.6
    assert auditor_scores["审计费用异常波动"] == 3.3


def test_fraud_detector_uses_config_for_cashflow_provision_and_subsidy_patterns(tmp_path):
    thresholds_path = tmp_path / "thresholds.yaml"
    thresholds_path.write_text(
        """
fraud_detection:
  cash_flow_divergence:
    cash_flow_negative_score: 3.9
  receivables_anomalies:
    bad_debt_provision_score: 4.1
  inventory_anomalies:
    inventory_provision_score: 4.2
  subsidy_manipulation:
    government_subsidies_score: 3.4
    deferred_income_score: 4.4
""".strip(),
        encoding="utf-8",
    )

    detector = FraudDetector(thresholds_config_path=str(thresholds_path))
    current = FinancialStatement(
        operating_revenue=100.0,
        total_assets=100.0,
        net_profit=10.0,
        net_cash_flow_operating=-5.0,
    )
    data = build_financial_data(
        current=current,
        notes={
            "bad_debt_provision": "100.00",
            "inventory_provision": "200.00",
            "government_subsidies": "300.00",
            "deferred_income": "400.00",
        },
    )

    patterns = detector.detect_fraud_patterns(data)
    pattern_map = {pattern.name: pattern for pattern in patterns}

    cash_flow_pattern = pattern_map["现金流异常模式"]
    subsidy_pattern = pattern_map["政府补助操纵模式"]

    assert {i.name: i.score for i in cash_flow_pattern.indicators}["经营活动现金流为负"] == 3.9
    assert "应收账款异常模式" not in pattern_map
    assert "存货异常模式" not in pattern_map
    subsidy_scores = {i.name: i.score for i in subsidy_pattern.indicators}
    assert subsidy_scores["政府补助异常增长"] == 3.4
    assert subsidy_scores["递延收益摊销异常"] == 4.4


def test_fraud_detector_does_not_create_provision_risk_from_note_presence_alone():
    detector = FraudDetector()
    current = FinancialStatement(
        operating_revenue=1000.0,
        total_assets=1500.0,
        net_profit=200.0,
        accounts_receivable=400.0,
        inventory=500.0,
    )
    data = build_financial_data(
        current=current,
        notes={
            "bad_debt_provision": "100.00",
            "inventory_provision": "200.00",
            "government_subsidies": "300.00",
            "deferred_income": "400.00",
        },
    )

    patterns = detector.detect_fraud_patterns(data)
    pattern_map = {pattern.name: pattern for pattern in patterns}
    assert "应收账款异常模式" not in pattern_map
    assert "存货异常模式" not in pattern_map
    subsidy_evidence = {
        indicator.name: indicator.evidence
        for indicator in pattern_map["政府补助操纵模式"].indicators
    }
    assert subsidy_evidence["政府补助异常增长"] == [
        "政府补助附注金额: 300.00元",
        "政府补助/净利润: 150.00%",
    ]
    assert subsidy_evidence["递延收益摊销异常"] == [
        "递延收益附注金额: 400.00元",
        "递延收益/净利润: 200.00%",
    ]


def test_fraud_detector_does_not_flag_immaterial_government_subsidy():
    detector = FraudDetector()
    current = FinancialStatement(
        operating_revenue=1000.0,
        total_assets=1500.0,
        net_profit=62000.0,
    )
    data = build_financial_data(
        current=current,
        notes={"government_subsidies": "330.24"},
    )

    patterns = detector.detect_fraud_patterns(data)
    pattern_names = {pattern.name for pattern in patterns}

    assert "政府补助操纵模式" not in pattern_names


def test_fraud_detector_uses_config_for_policy_audit_and_history_patterns(tmp_path):
    thresholds_path = tmp_path / "thresholds.yaml"
    thresholds_path.write_text(
        """
fraud_detection:
  accounting_changes:
    accounting_policy_changes_score: 3.1
  audit_issues:
    non_standard_opinion_score: 4.8
  historical_violations:
    score: 4.6
""".strip(),
        encoding="utf-8",
    )

    detector = FraudDetector(thresholds_config_path=str(thresholds_path))
    current = FinancialStatement(operating_revenue=100.0, total_assets=100.0, net_profit=10.0)
    data = build_financial_data(
        current=current,
        notes={
            "accounting_policy_changes": True,
            "historical_violations": "收到监管警示函",
        },
    )
    data.audit_opinion = "保留意见"

    patterns = detector.detect_fraud_patterns(data)
    pattern_map = {pattern.name: pattern for pattern in patterns}

    accounting_pattern = pattern_map["会计政策变更模式"]
    audit_pattern = pattern_map["审计问题模式"]
    history_pattern = pattern_map["历史违规模式"]

    assert accounting_pattern.indicators[0].score == 3.1
    assert audit_pattern.indicators[0].score == 4.8
    assert history_pattern.indicators[0].score == 4.6


def test_fraud_detector_flags_going_concern_unqualified_opinion_with_page_evidence():
    detector = FraudDetector()
    current = FinancialStatement(
        operating_revenue=100.0,
        total_assets=100.0,
        total_liabilities=20.0,
        net_profit=10.0,
    )
    data = build_financial_data(current=current)
    data.audit_opinion = "带持续经营重大不确定性段落的无保留意见"
    data.evidence_refs["audit:opinion"] = [
        {
            "page": 12,
            "excerpt": "我们出具了带与持续经营相关的重大不确定性段落的无保留意见。",
        }
    ]

    patterns = detector.detect_fraud_patterns(data)
    pattern_map = {pattern.name: pattern for pattern in patterns}

    audit_pattern = pattern_map["审计问题模式"]
    assert audit_pattern.indicators[0].name == "审计意见非标"
    assert audit_pattern.indicators[0].evidence == [
        "原文摘录（第12页）: 我们出具了带与持续经营相关的重大不确定性段落的无保留意见。"
    ]

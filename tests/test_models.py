from src.models.financial_data import FinancialData, FinancialStatement
from src.models.fraud_indicators import FraudIndicator
from src.models.fraud_indicators import FraudPattern
from src.models.fraud_indicators import FraudType
from src.models.fraud_indicators import RiskLevel
from src.core.report_generator import ReportGenerator
from src.models.report_model import AnalysisReport
from src.models.report_model import FinancialAnalysis
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


def test_analysis_report_markdown_includes_paged_evidence_and_score_formula():
    indicator = FraudIndicator(
        type=FraudType.REVENUE_MANIPULATION,
        name="收入确认异常",
        description="期末收入确认节奏异常",
        risk_level=RiskLevel.HIGH,
        score=3.0,
        evidence=[
            "营业收入同比增长 35.2%，但经营现金流净额同比下降 48.7%。",
            "原文摘录（第12页）: 营业收入 135,200,000.00 100,000,000.00",
            "原文摘录（第47页）: 第四季度收入占全年收入 54.1%",
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
        score_breakdown={
            "formula": "总分 = min(模式严重度 + 财务严重度 + 风险密度 + 风险广度 + 风险集中度 + 最高风险加分, 50)",
            "severity_score": 9.0,
            "financial_severity": 4.0,
            "density_score": 3.0,
            "breadth_score": 1.5,
            "concentration_score": 2.5,
            "max_risk_bonus": 1.0,
            "total_before_cap": 21.0,
            "total_score": 21.0,
        },
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
    assert "##### 证据摘录" in markdown
    assert "营业收入同比增长 35.2%" not in markdown
    assert "原文摘录（第12页）" in markdown
    assert "原文摘录（第47页）" in markdown
    assert "### 风险评分计算式" in markdown
    assert "总分 = min(模式严重度 + 财务严重度 + 风险密度 + 风险广度 + 风险集中度 + 最高风险加分, 50)" in markdown
    assert "- 模式严重度: 9.0" in markdown


def test_report_generator_marks_low_risk_report_as_pending_review_when_key_evidence_missing(
    tmp_path,
):
    generator = ReportGenerator(output_dir=str(tmp_path))
    statement = FinancialStatement(
        operating_revenue=100.0,
        net_profit=10.0,
        net_cash_flow_operating=12.0,
        total_assets=120.0,
        total_liabilities=30.0,
        total_equity=90.0,
    )
    statement.calculate_ratios()
    financial_data = FinancialData(
        company_name="测试公司",
        stock_code="000001",
        report_year=2025,
        auditor="测试会计师事务所",
        audit_opinion="标准无保留意见",
        current_year=statement,
    )
    assessment = RiskAssessment(total_score=0.0, risk_level=RiskLevel.LOW)

    report = generator.generate_report(
        financial_data,
        FinancialAnalysis(),
        assessment,
        [],
    )

    assert "待核验" in report.investment_recommendation


def test_report_generator_review_override_filters_conflicting_summary_recommendations(
    tmp_path,
):
    generator = ReportGenerator(output_dir=str(tmp_path))
    statement = FinancialStatement(
        operating_revenue=100.0,
        net_profit=10.0,
        net_cash_flow_operating=20.0,
        total_assets=120.0,
        total_liabilities=30.0,
        total_equity=90.0,
    )
    statement.calculate_ratios()
    financial_data = FinancialData(
        company_name="测试公司",
        stock_code="000001",
        report_year=2025,
        auditor="测试会计师事务所",
        audit_opinion="带持续经营重大不确定性段落的无保留意见",
        current_year=statement,
    )
    indicator = FraudIndicator(
        type=FraudType.AUDIT_ISSUE,
        name="审计意见非标",
        description="审计意见存在持续经营重大不确定性",
        risk_level=RiskLevel.CRITICAL,
        score=3.0,
        recommendations=[
            "仔细阅读审计报告说明段",
            "分析导致非标意见的原因",
        ],
    )
    pattern = FraudPattern(
        name="审计问题模式",
        description="审计意见非标或存在审计问题",
        indicators=[indicator],
    )
    pattern.calculate_score()
    assessment = RiskAssessment(
        total_score=33.5,
        risk_level=RiskLevel.CRITICAL,
        fraud_patterns=[pattern],
        recommendations=[
            "**极高风险**：建议立即停止投资，深入调查公司财务状况",
            "重点关注现金流异常和审计问题",
            "仔细阅读审计报告说明段",
            "分析导致非标意见的原因",
        ],
    )

    report = generator.generate_report(
        financial_data,
        FinancialAnalysis(),
        assessment,
        [pattern],
    )
    markdown = report.to_markdown()

    assert "待核验" in report.investment_recommendation
    assert "待核验：证据链未闭合或审计意见存在重大不确定性" in markdown
    assert "**极高风险**：建议立即停止投资，深入调查公司财务状况" not in markdown
    assert "重点关注现金流异常和审计问题" not in markdown
    assert "仔细阅读审计报告说明段" in markdown

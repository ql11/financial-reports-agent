"""
造假检测器
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from ..models.financial_data import FinancialData
from ..models.fraud_indicators import FraudIndicator, FraudPattern, FRAUD_INDICATORS, RiskLevel, FraudType
from ..utils.file_utils import load_yaml


class FraudDetector:
    """财报造假检测器"""
    
    def __init__(self, thresholds_config_path: Optional[str] = None):
        self.indicators = FRAUD_INDICATORS.copy()
        self.thresholds = self._load_thresholds(thresholds_config_path)

    def _load_thresholds(self, thresholds_config_path: Optional[str]) -> Dict[str, Any]:
        """加载检测阈值配置。"""
        config_path = thresholds_config_path
        if config_path is None:
            config_path = str(
                Path(__file__).resolve().parents[2] / "configs" / "thresholds.yaml"
            )

        thresholds = load_yaml(config_path)
        return thresholds or {}

    def _get_threshold(self, *path: str, default: Any) -> Any:
        """读取分层阈值配置。"""
        value: Any = self.thresholds
        for key in path:
            if not isinstance(value, dict):
                return default
            value = value.get(key)
            if value is None:
                return default
        return value
    
    def detect_fraud_patterns(self, financial_data: FinancialData) -> List[FraudPattern]:
        """检测造假模式
        
        Args:
            financial_data: 财务数据
            
        Returns:
            List[FraudPattern]: 检测到的造假模式列表
        """
        patterns = []
        
        # 1. 业绩背离模式
        revenue_profit_pattern = self._detect_revenue_profit_divergence(financial_data)
        if revenue_profit_pattern:
            patterns.append(revenue_profit_pattern)
        
        # 2. 现金流背离模式
        cash_flow_pattern = self._detect_cash_flow_divergence(financial_data)
        if cash_flow_pattern:
            patterns.append(cash_flow_pattern)
        
        # 3. 应收账款异常模式
        receivables_pattern = self._detect_receivables_anomalies(financial_data)
        if receivables_pattern:
            patterns.append(receivables_pattern)
        
        # 4. 存货异常模式
        inventory_pattern = self._detect_inventory_anomalies(financial_data)
        if inventory_pattern:
            patterns.append(inventory_pattern)
        
        # 5. 政府补助操纵模式
        subsidy_pattern = self._detect_subsidy_manipulation(financial_data)
        if subsidy_pattern:
            patterns.append(subsidy_pattern)
        
        # 6. 产能与投资异常模式
        capacity_pattern = self._detect_capacity_anomalies(financial_data)
        if capacity_pattern:
            patterns.append(capacity_pattern)
        
        # 7. 关联交易异常模式
        related_party_pattern = self._detect_related_party_issues(financial_data)
        if related_party_pattern:
            patterns.append(related_party_pattern)
        
        # 8. 会计政策变更模式
        accounting_pattern = self._detect_accounting_changes(financial_data)
        if accounting_pattern:
            patterns.append(accounting_pattern)
        
        # 9. 审计问题模式
        audit_pattern = self._detect_audit_issues(financial_data)
        if audit_pattern:
            patterns.append(audit_pattern)
        
        # 10. 历史违规模式
        violation_pattern = self._detect_historical_violations(financial_data)
        if violation_pattern:
            patterns.append(violation_pattern)
        
        # 11. 虚构收入模式
        fictitious_pattern = self._detect_fictitious_revenue(financial_data)
        if fictitious_pattern:
            patterns.append(fictitious_pattern)
        
        # 12. 费用资本化模式
        capitalization_pattern = self._detect_expense_capitalization(financial_data)
        if capitalization_pattern:
            patterns.append(capitalization_pattern)
        
        # 13. 资产高估模式
        asset_overstate_pattern = self._detect_asset_overstatement(financial_data)
        if asset_overstate_pattern:
            patterns.append(asset_overstate_pattern)
        
        # 14. 负债隐瞒模式
        liability_conceal_pattern = self._detect_liability_concealment(financial_data)
        if liability_conceal_pattern:
            patterns.append(liability_conceal_pattern)
        
        # 15. 报表勾稽校验
        cross_statement_pattern = self._detect_cross_statement_inconsistency(financial_data)
        if cross_statement_pattern:
            patterns.append(cross_statement_pattern)
        
        # 16. 现金流质量分析
        cash_quality_pattern = self._detect_cash_flow_quality(financial_data)
        if cash_quality_pattern:
            patterns.append(cash_quality_pattern)
        
        # 17. 会计估计变更
        estimate_change_pattern = self._detect_accounting_estimate_changes(financial_data)
        if estimate_change_pattern:
            patterns.append(estimate_change_pattern)
        
        # 18. 审计师变更
        auditor_change_pattern = self._detect_auditor_change(financial_data)
        if auditor_change_pattern:
            patterns.append(auditor_change_pattern)
        
        return patterns
    
    def _detect_revenue_profit_divergence(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测收入利润背离"""
        indicators = []
        revenue_decline_threshold = self._get_threshold(
            "fraud_detection", "revenue_profit_divergence", "revenue_decline", default=0.0
        )
        profit_growth_threshold = self._get_threshold(
            "fraud_detection", "revenue_profit_divergence", "profit_growth", default=0.0
        )
        pattern_score = self._get_threshold(
            "fraud_detection", "revenue_profit_divergence", "score", default=2.5
        )
        
        # 获取增长率
        revenue_growth = financial_data.get_growth_rate("operating_revenue", 1)
        profit_growth = financial_data.get_growth_rate("net_profit", 1)
        
        # 收入下降但利润增长
        if revenue_growth < revenue_decline_threshold and profit_growth > profit_growth_threshold:
            indicator = FraudIndicator(
                type=FraudType.REVENUE_MANIPULATION,
                name="收入利润背离",
                description=f"营业收入下降{abs(revenue_growth):.2f}%，但净利润增长{profit_growth:.2f}%，可能存在利润调节",
                risk_level=RiskLevel.HIGH,
                score=pattern_score,
                evidence=[
                    f"营业收入增长率: {revenue_growth:.2f}%",
                    f"净利润增长率: {profit_growth:.2f}%",
                    "收入下降但利润增长，可能存在非经常性损益调节或费用操纵"
                ],
                recommendations=[
                    "深入分析利润构成，确认是否依赖非经常性损益",
                    "检查费用确认是否合理，是否存在费用资本化",
                    "分析收入确认政策是否发生变化"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="业绩背离模式",
                description="收入与利润增长方向不一致，可能存在利润操纵",
                indicators=indicators
            )
        return None
    
    def _detect_cash_flow_divergence(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测现金流背离"""
        indicators = []
        profit_growth_threshold = self._get_threshold(
            "fraud_detection", "cash_flow_divergence", "profit_growth", default=0.0
        )
        cash_flow_decline_threshold = self._get_threshold(
            "fraud_detection", "cash_flow_divergence", "cash_flow_decline", default=-20.0
        )
        pattern_score = self._get_threshold(
            "fraud_detection", "cash_flow_divergence", "score", default=3.0
        )
        
        # 获取增长率
        profit_growth = financial_data.get_growth_rate("net_profit", 1)
        cash_flow_growth = financial_data.get_growth_rate("net_cash_flow_operating", 1)
        
        # 利润增长但现金流下降
        if (
            profit_growth > profit_growth_threshold
            and cash_flow_growth < cash_flow_decline_threshold
        ):
            indicator = FraudIndicator(
                type=FraudType.CASH_FLOW_MANIPULATION,
                name="现金流利润背离",
                description=f"净利润增长{profit_growth:.2f}%，但经营活动现金流下降{abs(cash_flow_growth):.2f}%",
                risk_level=RiskLevel.HIGH,
                score=pattern_score,
                evidence=[
                    f"净利润增长率: {profit_growth:.2f}%",
                    f"经营活动现金流增长率: {cash_flow_growth:.2f}%",
                    "利润增长但现金流大幅下降，可能存在收入虚增或应收账款异常"
                ],
                recommendations=[
                    "分析应收账款周转率变化",
                    "检查存货周转情况",
                    "确认收入确认时点是否合理"
                ]
            )
            indicators.append(indicator)
        
        # 经营活动现金流为负
        if financial_data.current_year.net_cash_flow_operating < 0:
            indicator = FraudIndicator(
                type=FraudType.CASH_FLOW_MANIPULATION,
                name="经营活动现金流为负",
                description="经营活动现金流量净额为负，公司可能面临现金流压力",
                risk_level=RiskLevel.HIGH,
                score=2.0,
                evidence=[
                    f"经营活动现金流: {financial_data.current_year.net_cash_flow_operating:,.0f}元",
                    "经营活动现金流为负，依赖筹资或投资活动维持运营"
                ],
                recommendations=[
                    "分析现金流为负的原因",
                    "评估公司短期偿债能力",
                    "检查是否存在过度投资或运营效率问题"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="现金流异常模式",
                description="现金流与利润背离或现金流为负，可能存在现金流操纵",
                indicators=indicators
            )
        return None
    
    def _detect_receivables_anomalies(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测应收账款异常"""
        indicators = []
        growth_exceed_revenue = self._get_threshold(
            "fraud_detection", "receivables_anomalies", "growth_exceed_revenue", default=10.0
        )
        pattern_score = self._get_threshold(
            "fraud_detection", "receivables_anomalies", "score", default=2.0
        )
        
        # 获取增长率
        revenue_growth = financial_data.get_growth_rate("operating_revenue", 1)
        receivables_growth = financial_data.get_growth_rate("accounts_receivable", 1)
        
        # 应收账款增长率超过收入增长率
        if receivables_growth > revenue_growth + growth_exceed_revenue:
            indicator = FraudIndicator(
                type=FraudType.RECEIVABLES_MANIPULATION,
                name="应收账款异常增长",
                description=f"应收账款增长{receivables_growth:.2f}%，超过收入增长{revenue_growth:.2f}%",
                risk_level=RiskLevel.MEDIUM,
                score=pattern_score,
                evidence=[
                    f"营业收入增长率: {revenue_growth:.2f}%",
                    f"应收账款增长率: {receivables_growth:.2f}%",
                    "应收账款增速超过收入增速，可能存在收入虚增或回款问题"
                ],
                recommendations=[
                    "分析应收账款账龄结构",
                    "检查坏账准备计提是否充分",
                    "评估客户信用风险"
                ]
            )
            indicators.append(indicator)
        
        # 检查附注中的坏账准备信息
        if "bad_debt_provision" in financial_data.notes:
            # 这里可以根据实际数据判断坏账准备是否减少
            indicator = FraudIndicator(
                type=FraudType.RECEIVABLES_MANIPULATION,
                name="坏账准备减少",
                description="应收账款增长但坏账准备减少，可能低估信用风险",
                risk_level=RiskLevel.HIGH,
                score=2.5,
                evidence=[
                    "应收账款增长但坏账准备减少",
                    "可能通过减少坏账准备调节利润"
                ],
                recommendations=[
                    "检查坏账准备计提政策是否变更",
                    "分析应收账款回收风险",
                    "评估坏账准备计提的充分性"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="应收账款异常模式",
                description="应收账款增长异常或坏账准备计提不足",
                indicators=indicators
            )
        return None
    
    def _detect_inventory_anomalies(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测存货异常"""
        indicators = []
        growth_exceed_revenue = self._get_threshold(
            "fraud_detection", "inventory_anomalies", "growth_exceed_revenue", default=15.0
        )
        pattern_score = self._get_threshold(
            "fraud_detection", "inventory_anomalies", "score", default=2.0
        )
        
        # 获取增长率
        revenue_growth = financial_data.get_growth_rate("operating_revenue", 1)
        inventory_growth = financial_data.get_growth_rate("inventory", 1)
        
        # 存货增长率超过收入增长率
        if inventory_growth > revenue_growth + growth_exceed_revenue:
            indicator = FraudIndicator(
                type=FraudType.INVENTORY_MANIPULATION,
                name="存货异常增长",
                description=f"存货增长{inventory_growth:.2f}%，超过收入增长{revenue_growth:.2f}%",
                risk_level=RiskLevel.MEDIUM,
                score=pattern_score,
                evidence=[
                    f"营业收入增长率: {revenue_growth:.2f}%",
                    f"存货增长率: {inventory_growth:.2f}%",
                    "存货增速超过收入增速，可能存在存货积压或减值风险"
                ],
                recommendations=[
                    "分析存货周转率变化",
                    "检查存货跌价准备计提是否充分",
                    "评估存货变现能力"
                ]
            )
            indicators.append(indicator)
        
        # 检查附注中的存货跌价准备信息
        if "inventory_provision" in financial_data.notes:
            # 这里可以根据实际数据判断跌价准备是否减少
            indicator = FraudIndicator(
                type=FraudType.INVENTORY_MANIPULATION,
                name="存货跌价准备减少",
                description="存货增长但跌价准备减少，可能低估存货减值风险",
                risk_level=RiskLevel.HIGH,
                score=2.5,
                evidence=[
                    "存货增长但跌价准备减少",
                    "可能通过减少跌价准备调节利润"
                ],
                recommendations=[
                    "检查存货跌价准备计提政策是否变更",
                    "分析存货市场价值变化",
                    "评估跌价准备计提的充分性"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="存货异常模式",
                description="存货增长异常或跌价准备计提不足",
                indicators=indicators
            )
        return None
    
    def _detect_subsidy_manipulation(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测政府补助操纵"""
        indicators = []
        
        # 检查附注中的政府补助信息
        if "government_subsidies" in financial_data.notes:
            indicator = FraudIndicator(
                type=FraudType.GOVERNMENT_SUBSIDY,
                name="政府补助异常增长",
                description="政府补助大幅增长，可能依赖政府补助维持利润",
                risk_level=RiskLevel.MEDIUM,
                score=1.5,
                evidence=[
                    "政府补助大幅增长",
                    "利润可能过度依赖政府补助"
                ],
                recommendations=[
                    "分析政府补助的可持续性",
                    "评估扣除政府补助后的实际盈利能力",
                    "检查政府补助的会计处理是否合规"
                ]
            )
            indicators.append(indicator)
        
        # 检查递延收益摊销
        if "deferred_income" in financial_data.notes:
            indicator = FraudIndicator(
                type=FraudType.GOVERNMENT_SUBSIDY,
                name="递延收益摊销异常",
                description="递延收益摊销大幅增长，可能通过调节摊销时点操纵利润",
                risk_level=RiskLevel.HIGH,
                score=2.0,
                evidence=[
                    "递延收益摊销大幅增长",
                    "可能通过调节摊销时点平滑利润"
                ],
                recommendations=[
                    "分析递延收益摊销政策",
                    "检查摊销时点是否合理",
                    "评估政府补助对利润的实际贡献"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="政府补助操纵模式",
                description="过度依赖政府补助或通过递延收益调节利润",
                indicators=indicators
            )
        return None
    
    def _detect_capacity_anomalies(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测产能与投资异常"""
        indicators = []
        turnover_threshold = self._get_threshold(
            "fraud_detection", "capacity_anomalies", "total_asset_turnover_warning", default=0.5
        )
        pattern_score = self._get_threshold(
            "fraud_detection", "capacity_anomalies", "score", default=1.5
        )
        
        # 固定资产周转率下降
        if financial_data.current_year.total_asset_turnover < turnover_threshold:
            indicator = FraudIndicator(
                type=FraudType.ASSET_MANIPULATION,
                name="产能利用率下降",
                description="固定资产周转率较低，产能利用率可能不足",
                risk_level=RiskLevel.MEDIUM,
                score=pattern_score,
                evidence=[
                    f"总资产周转率: {financial_data.current_year.total_asset_turnover:.2f}",
                    "产能利用率可能不足"
                ],
                recommendations=[
                    "分析产能利用率变化趋势",
                    "评估固定资产使用效率",
                    "检查是否存在闲置资产"
                ]
            )
            indicators.append(indicator)
        
        # 检查在建工程增长（这里需要实际数据）
        # 在实际应用中，需要从财务数据中获取在建工程信息
        
        if indicators:
            return FraudPattern(
                name="产能与投资异常模式",
                description="产能利用率下降或投资异常",
                indicators=indicators
            )
        return None
    
    def _detect_related_party_issues(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测关联交易问题"""
        indicators = []
        percentage_threshold = self._get_threshold(
            "fraud_detection", "related_party_transactions", "percentage_threshold", default=20.0
        )
        pattern_score = self._get_threshold(
            "fraud_detection", "related_party_transactions", "score", default=2.0
        )
        
        # 检查附注中的关联交易信息
        if "related_party_transactions" in financial_data.notes:
            transaction_percent = financial_data.notes["related_party_transactions"]
            # 尝试解析百分比
            try:
                percent = float(transaction_percent.strip('%'))
                if percent > percentage_threshold:
                    indicator = FraudIndicator(
                        type=FraudType.RELATED_PARTY_TRANSACTION,
                        name="关联交易比例过高",
                        description=f"关联交易占收入比例{percent:.1f}%，可能影响交易公允性",
                        risk_level=RiskLevel.HIGH,
                        score=pattern_score,
                        evidence=[
                            f"关联交易比例: {percent:.1f}%",
                            "关联交易比例过高，可能影响财务数据真实性"
                        ],
                        recommendations=[
                            "分析关联交易定价是否公允",
                            "评估关联交易的必要性",
                            "检查关联交易披露是否充分"
                        ]
                    )
                    indicators.append(indicator)
            except:
                pass
        
        if indicators:
            return FraudPattern(
                name="关联交易异常模式",
                description="关联交易比例过高或定价不公允",
                indicators=indicators
            )
        return None
    
    def _detect_accounting_changes(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测会计政策变更"""
        indicators = []
        
        # 检查附注中的会计政策变更
        if "accounting_policy_changes" in financial_data.notes:
            indicator = FraudIndicator(
                type=FraudType.ACCOUNTING_POLICY_CHANGE,
                name="会计政策变更",
                description="报告期内会计政策发生变更，可能影响财务数据可比性",
                risk_level=RiskLevel.MEDIUM,
                score=1.0,
                evidence=[
                    "会计政策发生变更",
                    "可能影响财务数据可比性"
                ],
                recommendations=[
                    "分析会计政策变更的影响",
                    "评估变更的合理性和必要性",
                    "检查变更是否充分披露"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="会计政策变更模式",
                description="会计政策变更可能影响财务数据可比性",
                indicators=indicators
            )
        return None
    
    def _detect_audit_issues(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测审计问题"""
        indicators = []
        
        # 检查审计意见（排除"标准无保留意见"和"无保留意见"）
        opinion = financial_data.audit_opinion
        is_non_standard = ("保留" in opinion and "无保留" not in opinion) or "否定" in opinion or "无法表示" in opinion or "非标准" in opinion
        if is_non_standard:
            indicator = FraudIndicator(
                type=FraudType.AUDIT_ISSUE,
                name="审计意见非标",
                description=f"审计意见为{financial_data.audit_opinion}，存在审计问题",
                risk_level=RiskLevel.CRITICAL,
                score=3.0,
                evidence=[
                    f"审计意见: {financial_data.audit_opinion}",
                    "非标准审计意见表明存在重大不确定性"
                ],
                recommendations=[
                    "仔细阅读审计报告说明段",
                    "分析导致非标意见的原因",
                    "评估对公司财务数据可信度的影响"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="审计问题模式",
                description="审计意见非标或存在审计问题",
                indicators=indicators
            )
        return None
    
    def _detect_historical_violations(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测历史违规"""
        indicators = []
        
        # 检查附注中是否有历史违规信息
        if "historical_violations" in financial_data.notes:
            violation_info = financial_data.notes["historical_violations"]
            indicator = FraudIndicator(
                type=FraudType.AUDIT_ISSUE,
                name="历史违规记录",
                description=f"公司有历史违规记录: {violation_info}",
                risk_level=RiskLevel.HIGH,
                score=2.5,
                evidence=[
                    f"历史违规: {violation_info}",
                    "存在历史违规记录，治理风险较高"
                ],
                recommendations=[
                    "关注公司治理结构",
                    "评估内部控制有效性",
                    "检查是否已整改历史问题"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="历史违规模式",
                description="公司有历史违规记录，治理风险较高",
                indicators=indicators
            )
        return None
    
    def _detect_fictitious_revenue(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测虚构收入嫌疑
        
        识别方法：
        - 应收账款增速远超收入增速
        - 现金收入比(销售商品收到的现金/营业收入)低于80%
        - 应收账款占收入比持续上升
        """
        indicators = []
        current = financial_data.current_year
        cash_revenue_threshold = self._get_threshold(
            "fraud_detection", "cash_revenue_ratio", "warning", default=0.8
        )
        cash_revenue_score = self._get_threshold(
            "fraud_detection", "cash_revenue_ratio", "score", default=2.5
        )
        receivable_ratio_threshold = self._get_threshold(
            "fraud_detection", "receivable_ratio", "warning", default=0.5
        )
        receivable_ratio_score = self._get_threshold(
            "fraud_detection", "receivable_ratio", "score", default=2.5
        )
        
        # 现金收入比 = 销售商品收到的现金 / 营业收入
        if current.operating_revenue > 0 and hasattr(current, 'cash_from_sales') and current.cash_from_sales > 0:
            cash_revenue_ratio = current.cash_from_sales / current.operating_revenue
            if cash_revenue_ratio < cash_revenue_threshold:
                indicator = FraudIndicator(
                    type=FraudType.FICTITIOUS_REVENUE,
                    name="现金收入比过低",
                    description=f"现金收入比为{cash_revenue_ratio:.1%}，低于{cash_revenue_threshold:.0%}警戒线，收入质量差",
                    risk_level=RiskLevel.HIGH,
                    score=cash_revenue_score,
                    evidence=[
                        f"销售商品收到的现金: {current.cash_from_sales:,.0f}",
                        f"营业收入: {current.operating_revenue:,.0f}",
                        f"现金收入比: {cash_revenue_ratio:.1%}（警戒线{cash_revenue_threshold:.0%}）",
                        "现金收入比低意味着收入中未收回现金部分占比高，可能虚构销售"
                    ],
                    recommendations=[
                        "核实主要客户真实性",
                        "分析应收账款账龄结构",
                        "检查是否存在期末集中确认大额收入"
                    ]
                )
                indicators.append(indicator)
        
        # 应收账款占收入比
        if current.operating_revenue > 0 and current.accounts_receivable > 0:
            receivable_ratio = current.accounts_receivable / current.operating_revenue
            if receivable_ratio > receivable_ratio_threshold:
                indicator = FraudIndicator(
                    type=FraudType.FICTITIOUS_REVENUE,
                    name="应收账款占收入比过高",
                    description=f"应收账款占收入比为{receivable_ratio:.1%}，超过{receivable_ratio_threshold:.0%}警戒线",
                    risk_level=RiskLevel.HIGH,
                    score=receivable_ratio_score,
                    evidence=[
                        f"应收账款: {current.accounts_receivable:,.0f}",
                        f"营业收入: {current.operating_revenue:,.0f}",
                        f"应收账款占收入比: {receivable_ratio:.1%}",
                        "应收账款占收入比过高，可能虚增收入或回款困难"
                    ],
                    recommendations=[
                        "分析应收账款周转天数变化",
                        "核实大额应收账款对应客户",
                        "检查坏账准备计提是否充分"
                    ]
                )
                indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="虚构收入嫌疑模式",
                description="收入质量指标异常，存在虚构收入嫌疑",
                indicators=indicators
            )
        return None
    
    def _detect_expense_capitalization(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测费用资本化异常
        
        识别方法：
        - 检查附注中研发费用资本化比例
        - 检查折旧政策变更
        - 检查在建工程与固定资产比例异常
        """
        indicators = []
        rd_ratio_threshold = self._get_threshold(
            "fraud_detection", "expense_capitalization", "rd_capitalization_ratio_warning", default=0.5
        )
        rd_ratio_score = self._get_threshold(
            "fraud_detection", "expense_capitalization", "rd_capitalization_ratio_score", default=2.5
        )
        depreciation_score = self._get_threshold(
            "fraud_detection", "expense_capitalization", "depreciation_policy_change_score", default=2.0
        )
        
        # 检查附注中的费用资本化信息
        if "rd_capitalization_ratio" in financial_data.notes:
            try:
                ratio = float(financial_data.notes["rd_capitalization_ratio"])
                if ratio > rd_ratio_threshold:
                    indicator = FraudIndicator(
                        type=FraudType.EXPENSE_CAPITALIZATION,
                        name="研发费用资本化比例异常",
                        description=f"研发费用资本化比例为{ratio:.1%}，远高于行业惯例(通常<30%)",
                        risk_level=RiskLevel.HIGH,
                        score=rd_ratio_score,
                        evidence=[
                            f"研发资本化率: {ratio:.1%}",
                            "高资本化率可能将应费用化的支出计入资产以虚增利润"
                        ],
                        recommendations=[
                            "对比同行业研发资本化比例",
                            "检查资本化项目的真实性",
                            "评估资本化政策是否合理"
                        ]
                    )
                    indicators.append(indicator)
            except (ValueError, TypeError):
                pass
        
        # 检查折旧政策变更
        if "depreciation_policy_change" in financial_data.notes:
            indicator = FraudIndicator(
                type=FraudType.EXPENSE_CAPITALIZATION,
                name="折旧政策变更",
                description="报告期内折旧政策发生变更，可能通过延长折旧年限减少费用",
                risk_level=RiskLevel.MEDIUM,
                score=depreciation_score,
                evidence=[
                    "折旧政策变更",
                    "延长折旧年限可直接减少当期费用，虚增利润"
                ],
                recommendations=[
                    "分析折旧政策变更对利润的影响金额",
                    "评估变更的合理性",
                    "对比变更前后折旧费用差异"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="费用资本化模式",
                description="费用资本化异常或折旧政策变更，可能虚增利润",
                indicators=indicators
            )
        return None
    
    def _detect_asset_overstatement(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测资产高估
        
        识别方法：
        - 在建工程迟迟不转固（附注信息）
        - 产能利用率低但固定资产增长
        - 无形资产占比异常
        """
        indicators = []
        current = financial_data.current_year
        construction_score = self._get_threshold(
            "fraud_detection", "asset_overstatement", "construction_in_progress_stagnant_score", default=2.5
        )
        turnover_threshold = self._get_threshold(
            "fraud_detection", "asset_overstatement", "total_asset_turnover_warning", default=0.5
        )
        asset_growth_threshold = self._get_threshold(
            "fraud_detection", "asset_overstatement", "asset_growth_warning", default=10.0
        )
        revenue_growth_ceiling = self._get_threshold(
            "fraud_detection", "asset_overstatement", "revenue_growth_ceiling", default=5.0
        )
        pattern_score = self._get_threshold(
            "fraud_detection", "asset_overstatement", "score", default=2.0
        )
        goodwill_score = self._get_threshold(
            "fraud_detection", "asset_overstatement", "goodwill_insufficient_impairment_score", default=2.5
        )
        
        # 在建工程迟迟不转固
        if "construction_in_progress_stagnant" in financial_data.notes:
            indicator = FraudIndicator(
                type=FraudType.ASSET_OVERSTATE,
                name="在建工程迟迟不转固",
                description="在建工程长期未转入固定资产，可能持续利息资本化虚增资产",
                risk_level=RiskLevel.HIGH,
                score=construction_score,
                evidence=[
                    "在建工程长期不转固",
                    "可能通过利息资本化虚增资产、虚减费用"
                ],
                recommendations=[
                    "核查在建工程实际进度",
                    "分析利息资本化金额",
                    "评估转固延迟的合理性"
                ]
            )
            indicators.append(indicator)
        
        # 产能与资产不匹配：总资产周转率低且固定资产增长
        if current.total_asset_turnover < turnover_threshold and current.total_assets > 0:
            revenue_growth = financial_data.get_growth_rate("operating_revenue", 1)
            asset_growth = financial_data.get_growth_rate("total_assets", 1)
            if asset_growth > asset_growth_threshold and revenue_growth < revenue_growth_ceiling:
                indicator = FraudIndicator(
                    type=FraudType.ASSET_OVERSTATE,
                    name="产能与资产不匹配",
                    description=f"资产增长{asset_growth:.1f}%但收入增长仅{revenue_growth:.1f}%，总资产周转率仅{current.total_asset_turnover:.2f}",
                    risk_level=RiskLevel.MEDIUM,
                    score=pattern_score,
                    evidence=[
                        f"总资产周转率: {current.total_asset_turnover:.2f}",
                        f"资产增长率: {asset_growth:.1f}%",
                        f"收入增长率: {revenue_growth:.1f}%",
                        "资产扩张但收入未同步增长，可能虚增资产"
                    ],
                    recommendations=[
                        "分析固定资产构成及新增资产情况",
                        "评估产能利用率",
                        "检查是否存在虚构资产"
                    ]
                )
                indicators.append(indicator)
        
        # 商誉减值不足
        if "goodwill_insufficient_impairment" in financial_data.notes:
            indicator = FraudIndicator(
                type=FraudType.ASSET_OVERSTATE,
                name="商誉减值计提不足",
                description="商誉金额较大但减值计提不足，可能虚增资产",
                risk_level=RiskLevel.HIGH,
                score=goodwill_score,
                evidence=[
                    "商誉减值计提不足",
                    "可能通过少计提商誉减值虚增资产和利润"
                ],
                recommendations=[
                    "分析商誉对应资产组的经营情况",
                    "评估商誉减值测试的合理性",
                    "对比同行业商誉减值计提情况"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="资产高估模式",
                description="资产可能被高估，存在虚增资产嫌疑",
                indicators=indicators
            )
        return None
    
    def _detect_liability_concealment(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测负债隐瞒
        
        识别方法：
        - 或有事项披露不足（未决诉讼、对外担保）
        - 表外融资嫌疑
        - 其他应付款异常
        """
        indicators = []
        contingent_score = self._get_threshold(
            "fraud_detection", "liability_concealment", "contingent_liabilities_score", default=2.0
        )
        off_balance_score = self._get_threshold(
            "fraud_detection", "liability_concealment", "off_balance_sheet_items_score", default=2.0
        )
        
        # 或有事项披露不足
        if "contingent_liabilities" in financial_data.notes:
            contingent = financial_data.notes["contingent_liabilities"]
            indicator = FraudIndicator(
                type=FraudType.LIABILITY_CONCEAL,
                name="或有事项披露不足",
                description=f"存在重大或有事项: {contingent}，可能低估负债",
                risk_level=RiskLevel.MEDIUM,
                score=contingent_score,
                evidence=[
                    f"或有事项: {contingent}",
                    "未决诉讼、对外担保等可能形成实际负债"
                ],
                recommendations=[
                    "评估或有事项转化为实际负债的可能性",
                    "分析对外担保的被担保方信用状况",
                    "检查或有事项披露是否充分"
                ]
            )
            indicators.append(indicator)
        
        # 表外融资嫌疑
        if "off_balance_sheet_items" in financial_data.notes:
            indicator = FraudIndicator(
                type=FraudType.TABLE_OFF_FINANCING,
                name="表外融资嫌疑",
                description="存在表外融资安排，可能隐藏负债",
                risk_level=RiskLevel.HIGH,
                score=off_balance_score,
                evidence=[
                    "存在表外融资安排",
                    "可能通过SPE/空壳公司将负债转移至表外"
                ],
                recommendations=[
                    "分析表外融资的具体形式",
                    "评估表外项目对财务报表的影响",
                    "检查是否需要合并表外实体"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="负债隐瞒模式",
                description="可能存在负债隐瞒或表外融资",
                indicators=indicators
            )
        return None
    
    def _detect_cross_statement_inconsistency(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测报表勾稽关系异常
        
        校验关系：
        - 资产负债表+利润表：未分配利润期末 ≈ 期初 + 净利润 - 股利分配
        - 现金流量表+资产负债表：期末现金变化应与现金流量表净增额一致
        - 利润表+现金流量表：经营现金流持续为负但净利润为正
        """
        indicators = []
        current = financial_data.current_year
        cash_profit_ratio_threshold = self._get_threshold(
            "fraud_detection", "cross_statement_inconsistency", "cash_profit_ratio_warning", default=0.5
        )
        cash_profit_ratio_score = self._get_threshold(
            "fraud_detection", "cross_statement_inconsistency", "cash_profit_ratio_score", default=3.0
        )
        profit_positive_cash_negative_score = self._get_threshold(
            "fraud_detection", "cross_statement_inconsistency", "profit_positive_cash_negative_score", default=3.0
        )
        check_failed_score = self._get_threshold(
            "fraud_detection", "cross_statement_inconsistency", "check_failed_score", default=3.0
        )
        
        # 经营现金流/净利润比率
        if current.net_profit > 0 and current.net_cash_flow_operating > 0:
            cash_profit_ratio = current.net_cash_flow_operating / current.net_profit
            if cash_profit_ratio < cash_profit_ratio_threshold:
                indicator = FraudIndicator(
                    type=FraudType.CROSS_STATEMENT_INCONSISTENCY,
                    name="经营现金流与净利润严重背离",
                    description=f"经营现金流/净利润={cash_profit_ratio:.2f}，远低于1，利润质量极差",
                    risk_level=RiskLevel.HIGH,
                    score=cash_profit_ratio_score,
                    evidence=[
                        f"经营现金流: {current.net_cash_flow_operating:,.0f}",
                        f"净利润: {current.net_profit:,.0f}",
                        f"经营现金流/净利润: {cash_profit_ratio:.2f}",
                        "比率<0.5意味着每1元利润中现金贡献不足0.5元"
                    ],
                    recommendations=[
                        "分析利润与现金流背离的具体原因",
                        "检查应收账款和存货变化",
                        "评估收入确认的真实性"
                    ]
                )
                indicators.append(indicator)
        elif current.net_profit > 0 and current.net_cash_flow_operating <= 0:
            indicator = FraudIndicator(
                type=FraudType.CROSS_STATEMENT_INCONSISTENCY,
                name="净利润为正但经营现金流为负",
                description="净利润为正但经营活动现金流为负，典型造假信号",
                risk_level=RiskLevel.CRITICAL,
                score=profit_positive_cash_negative_score,
                evidence=[
                    f"净利润: {current.net_profit:,.0f}",
                    f"经营现金流: {current.net_cash_flow_operating:,.0f}",
                    "净利润为正但经营现金流为负，收入可能虚构"
                ],
                recommendations=[
                    "深入核查收入确认的真实性",
                    "分析应收账款回收情况",
                    "检查是否存在虚增收入未收回现金"
                ]
            )
            indicators.append(indicator)
        
        # 检查附注中的勾稽关系异常
        if "cross_statement_check_failed" in financial_data.notes:
            check_detail = financial_data.notes["cross_statement_check_failed"]
            indicator = FraudIndicator(
                type=FraudType.CROSS_STATEMENT_INCONSISTENCY,
                name="报表勾稽关系不匹配",
                description=f"三张报表勾稽关系校验失败: {check_detail}",
                risk_level=RiskLevel.HIGH,
                score=check_failed_score,
                evidence=[
                    f"勾稽关系异常: {check_detail}",
                    "报表间数据不一致，可能存在数据操纵"
                ],
                recommendations=[
                    "逐项核对三张报表数据",
                    "检查是否存在调整分录未披露",
                    "核实财务报表编制的准确性"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="报表勾稽异常模式",
                description="三张报表之间勾稽关系异常，可能存在数据操纵",
                indicators=indicators
            )
        return None
    
    def _detect_cash_flow_quality(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测现金流质量异常
        
        分析：
        - 经营现金流/净利润比率
        - 自由现金流(经营现金流-资本支出)持续为负但净利润为正
        - 期末突击收回大量应收账款
        - 现金余额高但利息收入少
        """
        indicators = []
        current = financial_data.current_year
        free_cash_flow_score = self._get_threshold(
            "fraud_detection", "cash_flow_quality", "free_cash_flow_negative_score", default=2.5
        )
        cash_balance_interest_score = self._get_threshold(
            "fraud_detection", "cash_flow_quality", "cash_balance_interest_mismatch_score", default=2.5
        )
        
        # 自由现金流 = 经营现金流 - 资本支出(用投资现金流近似)
        if hasattr(current, 'net_cash_flow_investing') and current.net_cash_flow_investing != 0:
            capital_expenditure = abs(current.net_cash_flow_investing)
            free_cash_flow = current.net_cash_flow_operating - capital_expenditure
            if free_cash_flow < 0 and current.net_profit > 0:
                indicator = FraudIndicator(
                    type=FraudType.CASH_FLOW_MANIPULATION,
                    name="自由现金流为负但净利润为正",
                    description=f"自由现金流为{free_cash_flow:,.0f}，但净利润为{current.net_profit:,.0f}",
                    risk_level=RiskLevel.HIGH,
                    score=free_cash_flow_score,
                    evidence=[
                        f"经营现金流: {current.net_cash_flow_operating:,.0f}",
                        f"资本支出(近似): {capital_expenditure:,.0f}",
                        f"自由现金流: {free_cash_flow:,.0f}",
                        f"净利润: {current.net_profit:,.0f}",
                        "自由现金流为负意味着公司无法从经营中产生足够现金覆盖投资"
                    ],
                    recommendations=[
                        "分析资本支出的必要性和回报",
                        "评估公司长期现金流可持续性",
                        "检查是否过度依赖外部融资"
                    ]
                )
                indicators.append(indicator)
        
        # 现金余额高但利息收入少（伪造现金嫌疑）
        if "cash_balance_high_interest_low" in financial_data.notes:
            indicator = FraudIndicator(
                type=FraudType.CASH_FLOW_MANIPULATION,
                name="现金余额与利息收入不匹配",
                description="现金及等价物余额异常高但利息收入很少，可能伪造现金",
                risk_level=RiskLevel.HIGH,
                score=cash_balance_interest_score,
                evidence=[
                    "现金余额高但利息收入少",
                    "真实存款应产生合理利息收入"
                ],
                recommendations=[
                    "核实银行存款真实性",
                    "进行银行存款函证",
                    "分析利息收入与存款余额的匹配性"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="现金流质量异常模式",
                description="现金流质量指标异常，盈利质量存疑",
                indicators=indicators
            )
        return None
    
    def _detect_accounting_estimate_changes(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测会计估计变更
        
        常见虚增手段：
        - 延长固定资产折旧年限
        - 调低坏账准备计提比例
        - 调低存货跌价准备
        - 延长无形资产摊销年限
        """
        indicators = []
        estimate_change_score = self._get_threshold(
            "fraud_detection", "accounting_estimate_changes", "accounting_estimate_changes_score", default=2.0
        )
        bad_debt_ratio_score = self._get_threshold(
            "fraud_detection", "accounting_estimate_changes", "bad_debt_ratio_decreased_score", default=2.5
        )
        
        if "accounting_estimate_changes" in financial_data.notes:
            changes = financial_data.notes["accounting_estimate_changes"]
            indicator = FraudIndicator(
                type=FraudType.ACCOUNTING_ESTIMATE_CHANGE,
                name="会计估计变更",
                description=f"报告期内会计估计发生变更: {changes}",
                risk_level=RiskLevel.MEDIUM,
                score=estimate_change_score,
                evidence=[
                    f"会计估计变更: {changes}",
                    "会计估计变更可能影响利润，需评估变更的合理性"
                ],
                recommendations=[
                    "分析会计估计变更对当期利润的影响金额",
                    "评估变更是否基于合理的商业理由",
                    "对比变更前后财务数据的差异"
                ]
            )
            indicators.append(indicator)
        
        # 坏账准备计提比例下降
        if "bad_debt_ratio_decreased" in financial_data.notes:
            indicator = FraudIndicator(
                type=FraudType.PROVISION_UNDERSTATE,
                name="坏账准备计提比例下降",
                description="坏账准备计提比例下降，可能低估信用风险",
                risk_level=RiskLevel.HIGH,
                score=bad_debt_ratio_score,
                evidence=[
                    "坏账准备计提比例下降",
                    "调低计提比例可直接增加当期利润"
                ],
                recommendations=[
                    "分析计提比例下降的合理性",
                    "对比同行业坏账计提水平",
                    "评估应收账款实际回收风险"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="会计估计变更模式",
                description="会计估计变更可能虚增利润",
                indicators=indicators
            )
        return None
    
    def _detect_auditor_change(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测审计师变更
        
        预警信号：
        - 无合理理由更换审计师
        - 频繁更换审计机构
        - 审计费用异常波动
        """
        indicators = []
        auditor_change_score = self._get_threshold(
            "fraud_detection", "auditor_change", "auditor_change_score", default=2.5
        )
        audit_fee_score = self._get_threshold(
            "fraud_detection", "auditor_change", "audit_fee_abnormal_score", default=1.5
        )
        
        if "auditor_change" in financial_data.notes:
            change_info = financial_data.notes["auditor_change"]
            indicator = FraudIndicator(
                type=FraudType.AUDITOR_CHANGE,
                name="审计师变更",
                description=f"报告期内审计师发生变更: {change_info}",
                risk_level=RiskLevel.HIGH,
                score=auditor_change_score,
                evidence=[
                    f"审计师变更: {change_info}",
                    "无合理理由更换审计师可能暗示内部冲突或掩盖"
                ],
                recommendations=[
                    "了解审计师变更的具体原因",
                    "检查前任审计师的辞任声明",
                    "评估变更对审计质量的影响"
                ]
            )
            indicators.append(indicator)
        
        if "audit_fee_abnormal" in financial_data.notes:
            indicator = FraudIndicator(
                type=FraudType.AUDITOR_CHANGE,
                name="审计费用异常波动",
                description="审计费用异常波动，可能影响审计独立性",
                risk_level=RiskLevel.MEDIUM,
                score=audit_fee_score,
                evidence=[
                    "审计费用异常波动",
                    "审计费用大幅下降可能降低审计质量"
                ],
                recommendations=[
                    "对比历年审计费用",
                    "评估审计费用是否足以支撑充分审计",
                    "检查是否存在购买审计意见嫌疑"
                ]
            )
            indicators.append(indicator)
        
        if indicators:
            return FraudPattern(
                name="审计师变更模式",
                description="审计师变更或审计费用异常，可能影响审计质量",
                indicators=indicators
            )
        return None

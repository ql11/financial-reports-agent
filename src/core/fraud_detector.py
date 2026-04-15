"""
造假检测器
"""

from typing import Dict, List, Optional, Any
from ..models.financial_data import FinancialData
from ..models.fraud_indicators import FraudIndicator, FraudPattern, FRAUD_INDICATORS, RiskLevel, FraudType


class FraudDetector:
    """财报造假检测器"""
    
    def __init__(self):
        self.indicators = FRAUD_INDICATORS.copy()
    
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
        
        return patterns
    
    def _detect_revenue_profit_divergence(self, financial_data: FinancialData) -> Optional[FraudPattern]:
        """检测收入利润背离"""
        indicators = []
        
        # 获取增长率
        revenue_growth = financial_data.get_growth_rate("operating_revenue", 1)
        profit_growth = financial_data.get_growth_rate("net_profit", 1)
        
        # 收入下降但利润增长
        if revenue_growth < 0 and profit_growth > 0:
            indicator = FraudIndicator(
                type=FraudType.REVENUE_MANIPULATION,
                name="收入利润背离",
                description=f"营业收入下降{abs(revenue_growth):.2f}%，但净利润增长{profit_growth:.2f}%，可能存在利润调节",
                risk_level=RiskLevel.HIGH,
                score=2.5,
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
        
        # 获取增长率
        profit_growth = financial_data.get_growth_rate("net_profit", 1)
        cash_flow_growth = financial_data.get_growth_rate("net_cash_flow_operating", 1)
        
        # 利润增长但现金流下降
        if profit_growth > 0 and cash_flow_growth < -20:  # 现金流下降超过20%
            indicator = FraudIndicator(
                type=FraudType.CASH_FLOW_MANIPULATION,
                name="现金流利润背离",
                description=f"净利润增长{profit_growth:.2f}%，但经营活动现金流下降{abs(cash_flow_growth):.2f}%",
                risk_level=RiskLevel.HIGH,
                score=3.0,
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
        
        # 获取增长率
        revenue_growth = financial_data.get_growth_rate("operating_revenue", 1)
        receivables_growth = financial_data.get_growth_rate("accounts_receivable", 1)
        
        # 应收账款增长率超过收入增长率
        if receivables_growth > revenue_growth + 10:  # 超过10个百分点
            indicator = FraudIndicator(
                type=FraudType.RECEIVABLES_MANIPULATION,
                name="应收账款异常增长",
                description=f"应收账款增长{receivables_growth:.2f}%，超过收入增长{revenue_growth:.2f}%",
                risk_level=RiskLevel.MEDIUM,
                score=2.0,
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
        
        # 获取增长率
        revenue_growth = financial_data.get_growth_rate("operating_revenue", 1)
        inventory_growth = financial_data.get_growth_rate("inventory", 1)
        
        # 存货增长率超过收入增长率
        if inventory_growth > revenue_growth + 15:  # 超过15个百分点
            indicator = FraudIndicator(
                type=FraudType.INVENTORY_MANIPULATION,
                name="存货异常增长",
                description=f"存货增长{inventory_growth:.2f}%，超过收入增长{revenue_growth:.2f}%",
                risk_level=RiskLevel.MEDIUM,
                score=2.0,
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
        
        # 固定资产周转率下降
        if financial_data.current_year.total_asset_turnover < 0.5:  # 假设阈值
            indicator = FraudIndicator(
                type=FraudType.ASSET_MANIPULATION,
                name="产能利用率下降",
                description="固定资产周转率较低，产能利用率可能不足",
                risk_level=RiskLevel.MEDIUM,
                score=1.5,
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
        
        # 检查附注中的关联交易信息
        if "related_party_transactions" in financial_data.notes:
            transaction_percent = financial_data.notes["related_party_transactions"]
            # 尝试解析百分比
            try:
                percent = float(transaction_percent.strip('%'))
                if percent > 20:  # 关联交易超过20%
                    indicator = FraudIndicator(
                        type=FraudType.RELATED_PARTY_TRANSACTION,
                        name="关联交易比例过高",
                        description=f"关联交易占收入比例{percent:.1f}%，可能影响交易公允性",
                        risk_level=RiskLevel.HIGH,
                        score=2.0,
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
        
        # 检查审计意见
        if "非标准" in financial_data.audit_opinion or "保留" in financial_data.audit_opinion:
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
        
        # 这里可以根据公司名称或股票代码检查历史违规记录
        # 在实际应用中，可以连接数据库或API查询
        
        # 示例：英洛华有历史违规记录
        if "英洛华" in financial_data.company_name:
            indicator = FraudIndicator(
                type=FraudType.AUDIT_ISSUE,
                name="历史违规记录",
                description="公司有历史违规记录，2021年被浙江证监局警示",
                risk_level=RiskLevel.HIGH,
                score=2.5,
                evidence=[
                    "2021年被浙江证监局出具警示函",
                    "存在历史违规记录"
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
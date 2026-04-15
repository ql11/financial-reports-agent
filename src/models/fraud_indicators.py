"""
造假指标模型
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    CRITICAL = "极高"


class FraudType(Enum):
    """造假类型"""
    REVENUE_MANIPULATION = "收入操纵"
    EXPENSE_MANIPULATION = "费用操纵"
    ASSET_MANIPULATION = "资产操纵"
    LIABILITY_MANIPULATION = "负债操纵"
    CASH_FLOW_MANIPULATION = "现金流操纵"
    RELATED_PARTY_TRANSACTION = "关联交易"
    ACCOUNTING_POLICY_CHANGE = "会计政策变更"
    AUDIT_ISSUE = "审计问题"
    GOVERNMENT_SUBSIDY = "政府补助操纵"
    INVENTORY_MANIPULATION = "存货操纵"
    RECEIVABLES_MANIPULATION = "应收账款操纵"
    FICTITIOUS_REVENUE = "虚构收入"
    EXPENSE_CAPITALIZATION = "费用资本化"
    ASSET_OVERSTATE = "资产高估"
    LIABILITY_CONCEAL = "负债隐瞒"
    PROVISION_UNDERSTATE = "准备低估"
    TABLE_OFF_FINANCING = "表外融资"
    ACCOUNTING_ESTIMATE_CHANGE = "会计估计变更"
    AUDITOR_CHANGE = "审计师变更"
    CROSS_STATEMENT_INCONSISTENCY = "报表勾稽异常"


@dataclass
class FraudIndicator:
    """造假指标"""
    
    type: FraudType
    name: str
    description: str
    risk_level: RiskLevel
    score: float  # 0-10分
    evidence: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "score": self.score,
            "evidence": self.evidence,
            "recommendations": self.recommendations
        }


@dataclass
class FraudPattern:
    """造假模式"""
    
    name: str
    description: str
    indicators: List[FraudIndicator]
    total_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    
    def calculate_score(self):
        """计算总分和风险等级"""
        if not self.indicators:
            return
        
        self.total_score = sum(indicator.score for indicator in self.indicators)
        
        # 根据指标的最高风险等级确定模式风险等级
        max_risk = RiskLevel.LOW
        for indicator in self.indicators:
            if indicator.risk_level == RiskLevel.CRITICAL:
                max_risk = RiskLevel.CRITICAL
                break
            elif indicator.risk_level == RiskLevel.HIGH and max_risk != RiskLevel.CRITICAL:
                max_risk = RiskLevel.HIGH
            elif indicator.risk_level == RiskLevel.MEDIUM and max_risk not in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                max_risk = RiskLevel.MEDIUM
        
        self.risk_level = max_risk
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        self.calculate_score()
        return {
            "name": self.name,
            "description": self.description,
            "indicators": [indicator.to_dict() for indicator in self.indicators],
            "total_score": self.total_score,
            "risk_level": self.risk_level.value
        }


# 预定义的造假指标
FRAUD_INDICATORS = {
    # 业绩背离指标
    "revenue_profit_divergence": FraudIndicator(
        type=FraudType.REVENUE_MANIPULATION,
        name="收入利润背离",
        description="营业收入下降但净利润增长，可能存在利润调节",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    "cash_flow_profit_divergence": FraudIndicator(
        type=FraudType.CASH_FLOW_MANIPULATION,
        name="现金流利润背离",
        description="净利润增长但经营活动现金流大幅下降",
        risk_level=RiskLevel.HIGH,
        score=3.0
    ),
    
    # 应收账款异常
    "receivables_growth_abnormal": FraudIndicator(
        type=FraudType.RECEIVABLES_MANIPULATION,
        name="应收账款异常增长",
        description="应收账款增长率超过收入增长率",
        risk_level=RiskLevel.MEDIUM,
        score=2.0
    ),
    
    "bad_debt_provision_decrease": FraudIndicator(
        type=FraudType.RECEIVABLES_MANIPULATION,
        name="坏账准备减少",
        description="应收账款增长但坏账准备减少",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    # 存货异常
    "inventory_growth_abnormal": FraudIndicator(
        type=FraudType.INVENTORY_MANIPULATION,
        name="存货异常增长",
        description="存货增长率超过收入增长率",
        risk_level=RiskLevel.MEDIUM,
        score=2.0
    ),
    
    "inventory_provision_decrease": FraudIndicator(
        type=FraudType.INVENTORY_MANIPULATION,
        name="存货跌价准备减少",
        description="存货增长但跌价准备减少",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    # 政府补助操纵
    "gov_subsidy_abnormal_growth": FraudIndicator(
        type=FraudType.GOVERNMENT_SUBSIDY,
        name="政府补助异常增长",
        description="政府补助大幅增长",
        risk_level=RiskLevel.MEDIUM,
        score=1.5
    ),
    
    "deferred_income_abnormal": FraudIndicator(
        type=FraudType.GOVERNMENT_SUBSIDY,
        name="递延收益摊销异常",
        description="递延收益摊销大幅增长",
        risk_level=RiskLevel.HIGH,
        score=2.0
    ),
    
    # 产能与投资异常
    "capacity_utilization_decline": FraudIndicator(
        type=FraudType.ASSET_MANIPULATION,
        name="产能利用率下降",
        description="固定资产周转率持续下降",
        risk_level=RiskLevel.MEDIUM,
        score=1.5
    ),
    
    "construction_in_progress_growth": FraudIndicator(
        type=FraudType.ASSET_MANIPULATION,
        name="在建工程异常增长",
        description="产能利用率下降但在建工程大幅增长",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    # 关联交易
    "related_party_transaction_high": FraudIndicator(
        type=FraudType.RELATED_PARTY_TRANSACTION,
        name="关联交易比例过高",
        description="关联交易占收入比例过高",
        risk_level=RiskLevel.HIGH,
        score=2.0
    ),
    
    # 会计政策变更
    "accounting_policy_change": FraudIndicator(
        type=FraudType.ACCOUNTING_POLICY_CHANGE,
        name="会计政策变更",
        description="报告期内会计政策变更",
        risk_level=RiskLevel.MEDIUM,
        score=1.0
    ),
    
    # 审计问题
    "audit_qualification": FraudIndicator(
        type=FraudType.AUDIT_ISSUE,
        name="审计意见非标",
        description="审计意见为非标准无保留意见",
        risk_level=RiskLevel.CRITICAL,
        score=3.0
    ),
    
    # 历史违规
    "historical_violation": FraudIndicator(
        type=FraudType.AUDIT_ISSUE,
        name="历史违规记录",
        description="公司有历史违规记录",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    # 现金流异常
    "operating_cash_flow_negative": FraudIndicator(
        type=FraudType.CASH_FLOW_MANIPULATION,
        name="经营活动现金流为负",
        description="经营活动现金流量净额为负",
        risk_level=RiskLevel.HIGH,
        score=2.0
    ),
    
    # 负债异常
    "debt_ratio_high": FraudIndicator(
        type=FraudType.LIABILITY_MANIPULATION,
        name="资产负债率过高",
        description="资产负债率超过行业平均水平",
        risk_level=RiskLevel.MEDIUM,
        score=1.5
    ),
    
    # 盈利能力异常
    "profit_margin_decline": FraudIndicator(
        type=FraudType.REVENUE_MANIPULATION,
        name="利润率持续下降",
        description="毛利率或净利率持续下降",
        risk_level=RiskLevel.MEDIUM,
        score=1.5
    ),
    
    # ===== 新增：来自专业造假识别文档的指标 =====
    
    # 虚构收入
    "fictitious_revenue": FraudIndicator(
        type=FraudType.FICTITIOUS_REVENUE,
        name="虚构收入嫌疑",
        description="应收账款增速远超收入增速，现金收入比低，可能虚构销售",
        risk_level=RiskLevel.HIGH,
        score=3.0
    ),
    
    "cash_revenue_ratio_low": FraudIndicator(
        type=FraudType.FICTITIOUS_REVENUE,
        name="现金收入比过低",
        description="销售商品收到的现金/营业收入长期低于80%，收入质量差",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    "q4_revenue_concentration": FraudIndicator(
        type=FraudType.FICTITIOUS_REVENUE,
        name="年末收入集中确认",
        description="第四季度收入占比异常高，可能年底虚增收入",
        risk_level=RiskLevel.MEDIUM,
        score=2.0
    ),
    
    # 费用资本化
    "expense_capitalization_abnormal": FraudIndicator(
        type=FraudType.EXPENSE_CAPITALIZATION,
        name="费用资本化异常",
        description="研发费用或营销费用资本化比例远高于行业惯例",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    "depreciation_policy_change": FraudIndicator(
        type=FraudType.EXPENSE_CAPITALIZATION,
        name="折旧政策变更",
        description="延长折旧年限或变更折旧方法以减少费用",
        risk_level=RiskLevel.MEDIUM,
        score=2.0
    ),
    
    # 资产高估
    "asset_overstate": FraudIndicator(
        type=FraudType.ASSET_OVERSTATE,
        name="资产高估嫌疑",
        description="固定资产/无形资产频繁重估增值，或虚构应收账款和存货",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    "construction_delay": FraudIndicator(
        type=FraudType.ASSET_OVERSTATE,
        name="在建工程迟迟不转固",
        description="在建工程长期不转入固定资产，可能持续利息资本化虚增资产",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    "capacity_asset_mismatch": FraudIndicator(
        type=FraudType.ASSET_OVERSTATE,
        name="产能与资产不匹配",
        description="产能利用率低但固定资产大幅增长",
        risk_level=RiskLevel.MEDIUM,
        score=2.0
    ),
    
    # 负债隐瞒
    "liability_conceal": FraudIndicator(
        type=FraudType.LIABILITY_CONCEAL,
        name="负债隐瞒嫌疑",
        description="将应计入负债的项目计入权益或表外，低估负债率",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    # 准备低估
    "provision_understate": FraudIndicator(
        type=FraudType.PROVISION_UNDERSTATE,
        name="减值准备计提不足",
        description="坏账准备、存货跌价准备、资产减值准备计提比例异常偏低",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    # 表外融资
    "table_off_financing": FraudIndicator(
        type=FraudType.TABLE_OFF_FINANCING,
        name="表外融资嫌疑",
        description="通过SPE/空壳公司将负债转移至表外",
        risk_level=RiskLevel.HIGH,
        score=2.0
    ),
    
    # 会计估计变更
    "accounting_estimate_change": FraudIndicator(
        type=FraudType.ACCOUNTING_ESTIMATE_CHANGE,
        name="会计估计变更",
        description="延长折旧年限、调低坏账计提比例、调低存货跌价准备等",
        risk_level=RiskLevel.MEDIUM,
        score=2.0
    ),
    
    # 审计师变更
    "auditor_change": FraudIndicator(
        type=FraudType.AUDITOR_CHANGE,
        name="审计师变更",
        description="无合理理由更换审计师，可能暗示内部冲突或掩盖",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    # 报表勾稽异常
    "cross_statement_inconsistency": FraudIndicator(
        type=FraudType.CROSS_STATEMENT_INCONSISTENCY,
        name="报表勾稽关系异常",
        description="三张报表之间勾稽关系不匹配，可能存在数据操纵",
        risk_level=RiskLevel.HIGH,
        score=3.0
    ),
    
    # 现金流比率异常
    "cash_flow_to_profit_low": FraudIndicator(
        type=FraudType.CASH_FLOW_MANIPULATION,
        name="经营现金流/净利润比率过低",
        description="经营现金流/净利润持续低于0.5，盈利质量极差",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    "free_cash_flow_negative": FraudIndicator(
        type=FraudType.CASH_FLOW_MANIPULATION,
        name="自由现金流持续为负",
        description="自由现金流(经营现金流-资本支出)持续为负但净利润为正",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    # 毛利率异常
    "gross_margin_abnormal_high": FraudIndicator(
        type=FraudType.REVENUE_MANIPULATION,
        name="毛利率异常偏高",
        description="毛利率显著高于行业龙头或与同业差异>15%",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    "gross_margin_too_smooth": FraudIndicator(
        type=FraudType.REVENUE_MANIPULATION,
        name="毛利率异常平滑",
        description="毛利率波动异常平滑，可能人为调节",
        risk_level=RiskLevel.MEDIUM,
        score=1.5
    ),
    
    # 关联交易深化
    "related_party_conceal": FraudIndicator(
        type=FraudType.RELATED_PARTY_TRANSACTION,
        name="关联交易披露不完整",
        description="关联交易披露不完整或隐性关联方未识别",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    "related_party_pricing_abnormal": FraudIndicator(
        type=FraudType.RELATED_PARTY_TRANSACTION,
        name="关联交易定价异常",
        description="关联交易定价显著偏离市场价",
        risk_level=RiskLevel.HIGH,
        score=2.5
    ),
    
    # 或有事项
    "contingent_liability_conceal": FraudIndicator(
        type=FraudType.LIABILITY_CONCEAL,
        name="或有事项披露不足",
        description="未决诉讼、对外担保等或有事项披露不充分",
        risk_level=RiskLevel.MEDIUM,
        score=2.0
    )
}
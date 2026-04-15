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
        
        # 根据总分确定风险等级
        if self.total_score >= 8:
            self.risk_level = RiskLevel.CRITICAL
        elif self.total_score >= 6:
            self.risk_level = RiskLevel.HIGH
        elif self.total_score >= 4:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.LOW
    
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
    )
}
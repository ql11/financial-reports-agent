"""
风险评估器
"""

from typing import Dict, List, Optional, Any
from ..models.financial_data import FinancialData
from ..models.fraud_indicators import FraudPattern, RiskLevel
from ..models.report_model import RiskAssessment


class RiskAssessor:
    """风险评估器"""
    
    def __init__(self):
        self.risk_weights = {
            "revenue_profit_divergence": 1.2,
            "cash_flow_divergence": 1.5,
            "receivables_anomalies": 1.0,
            "inventory_anomalies": 1.0,
            "subsidy_manipulation": 0.8,
            "capacity_anomalies": 0.7,
            "related_party_issues": 1.3,
            "accounting_changes": 0.5,
            "audit_issues": 2.0,
            "historical_violations": 1.8
        }
    
    def assess_risk(self, fraud_patterns: List[FraudPattern], financial_data: FinancialData) -> RiskAssessment:
        """评估风险
        
        Args:
            fraud_patterns: 检测到的造假模式列表
            financial_data: 财务数据
            
        Returns:
            RiskAssessment: 风险评估结果
        """
        risk_assessment = RiskAssessment()
        risk_assessment.fraud_patterns = fraud_patterns
        
        # 计算每个模式的风险评分
        for pattern in fraud_patterns:
            pattern.calculate_score()
        
        # 计算总风险评分
        total_score = sum(pattern.total_score for pattern in fraud_patterns)
        
        # 应用权重调整
        weighted_score = self._apply_weights(total_score, fraud_patterns)
        risk_assessment.total_score = weighted_score
        
        # 确定风险等级
        risk_assessment.risk_level = self._determine_risk_level(weighted_score)
        
        # 生成关键风险点
        risk_assessment.key_risks = self._extract_key_risks(fraud_patterns)
        
        # 生成建议
        risk_assessment.recommendations = self._generate_recommendations(
            fraud_patterns, financial_data, risk_assessment.risk_level
        )
        
        return risk_assessment
    
    def _apply_weights(self, base_score: float, fraud_patterns: List[FraudPattern]) -> float:
        """应用权重调整"""
        weighted_score = 0.0

        # 对每个模式的分数分别乘以对应权重，然后求和
        for pattern in fraud_patterns:
            pattern_score = pattern.total_score
            pattern_name = pattern.name
            if "业绩背离" in pattern_name:
                weighted_score += pattern_score * self.risk_weights["revenue_profit_divergence"]
            elif "现金流" in pattern_name:
                weighted_score += pattern_score * self.risk_weights["cash_flow_divergence"]
            elif "应收账款" in pattern_name:
                weighted_score += pattern_score * self.risk_weights["receivables_anomalies"]
            elif "存货" in pattern_name:
                weighted_score += pattern_score * self.risk_weights["inventory_anomalies"]
            elif "政府补助" in pattern_name:
                weighted_score += pattern_score * self.risk_weights["subsidy_manipulation"]
            elif "产能" in pattern_name:
                weighted_score += pattern_score * self.risk_weights["capacity_anomalies"]
            elif "关联交易" in pattern_name:
                weighted_score += pattern_score * self.risk_weights["related_party_issues"]
            elif "会计政策" in pattern_name:
                weighted_score += pattern_score * self.risk_weights["accounting_changes"]
            elif "审计" in pattern_name:
                weighted_score += pattern_score * self.risk_weights["audit_issues"]
            elif "历史违规" in pattern_name:
                weighted_score += pattern_score * self.risk_weights["historical_violations"]
            else:
                weighted_score += pattern_score

        return min(weighted_score, 50.0)  # 最高50分
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """确定风险等级"""
        if score >= 30:
            return RiskLevel.CRITICAL
        elif score >= 20:
            return RiskLevel.HIGH
        elif score >= 10:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _extract_key_risks(self, fraud_patterns: List[FraudPattern]) -> List[str]:
        """提取关键风险点"""
        key_risks = []
        
        for pattern in fraud_patterns:
            if pattern.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                for indicator in pattern.indicators:
                    if indicator.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                        key_risks.append(f"{pattern.name}: {indicator.name}")
        
        # 如果没有高风险，则选择中等风险
        if not key_risks:
            for pattern in fraud_patterns:
                if pattern.risk_level == RiskLevel.MEDIUM:
                    for indicator in pattern.indicators:
                        if indicator.risk_level == RiskLevel.MEDIUM:
                            key_risks.append(f"{pattern.name}: {indicator.name}")
        
        # 限制最多5个关键风险点
        return key_risks[:5]
    
    def _generate_recommendations(self, fraud_patterns: List[FraudPattern], 
                                 financial_data: FinancialData, 
                                 risk_level: RiskLevel) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 根据风险等级生成总体建议
        if risk_level == RiskLevel.CRITICAL:
            recommendations.append("**极高风险**：建议立即停止投资，深入调查公司财务状况")
            recommendations.append("重点关注现金流异常和审计问题")
        elif risk_level == RiskLevel.HIGH:
            recommendations.append("**高风险**：建议谨慎投资，需要进一步调查")
            recommendations.append("关注业绩背离和应收账款异常")
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.append("**中等风险**：建议关注风险点，适当调整投资策略")
            recommendations.append("关注存货异常和政府补助操纵")
        else:
            recommendations.append("**低风险**：可以继续持有，但需定期监控")
            recommendations.append("关注财务指标变化趋势")
        
        # 根据具体问题生成建议
        for pattern in fraud_patterns:
            if pattern.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                # 收集所有高风险指标的建议
                for indicator in pattern.indicators:
                    if indicator.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                        recommendations.extend(indicator.recommendations)
        
        # 去重并限制数量
        unique_recommendations = []
        seen = set()
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:10]  # 最多10条建议
    
    def generate_investment_recommendation(self, risk_assessment: RiskAssessment) -> str:
        """生成投资建议
        
        Args:
            risk_assessment: 风险评估结果
            
        Returns:
            str: 投资建议
        """
        risk_level = risk_assessment.risk_level
        total_score = risk_assessment.total_score
        
        if risk_level == RiskLevel.CRITICAL:
            return (
                f"**强烈建议暂停投资**。风险评分{total_score:.1f}/50，风险等级{risk_level.value}。"
                f"发现{len(risk_assessment.fraud_patterns)}个造假模式，"
                f"其中{sum(1 for p in risk_assessment.fraud_patterns if p.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL])}个为高风险。"
                f"建议深入调查公司财务状况，确认无重大风险后再考虑投资。"
            )
        elif risk_level == RiskLevel.HIGH:
            return (
                f"**建议谨慎投资**。风险评分{total_score:.1f}/50，风险等级{risk_level.value}。"
                f"发现{len(risk_assessment.fraud_patterns)}个造假模式。"
                f"建议进一步调查关键风险点，控制投资仓位，设置严格止损。"
            )
        elif risk_level == RiskLevel.MEDIUM:
            return (
                f"**可以适度投资**。风险评分{total_score:.1f}/50，风险等级{risk_level.value}。"
                f"发现{len(risk_assessment.fraud_patterns)}个造假模式。"
                f"建议关注风险点，分散投资，定期监控公司财务状况。"
            )
        else:
            return (
                f"**可以继续持有或适度增持**。风险评分{total_score:.1f}/50，风险等级{risk_level.value}。"
                f"发现{len(risk_assessment.fraud_patterns)}个造假模式。"
                f"建议定期监控财务指标，关注行业变化。"
            )
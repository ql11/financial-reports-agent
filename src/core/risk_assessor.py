"""
风险评估器

采用风险密度模型，解决"模式多但分数被稀释"的问题：
- 不再用"触发分数/50"的绝对比例
- 而是综合：高风险模式占比、最高风险等级、风险集中度、加权分数
- 确保多个高风险模式不会被低估
"""

from typing import Dict, List, Optional, Any
from ..models.financial_data import FinancialData
from ..models.fraud_indicators import FraudPattern, RiskLevel
from ..models.report_model import RiskAssessment


class RiskAssessor:
    """风险评估器"""
    
    def __init__(self):
        # 模式权重：不同模式对风险的贡献不同
        self.pattern_weights = {
            "业绩背离": 1.3,
            "现金流异常": 1.5,
            "现金流质量": 1.4,
            "应收账款": 1.1,
            "虚构收入": 1.4,
            "存货": 1.0,
            "政府补助": 0.8,
            "产能": 0.7,
            "关联交易": 1.3,
            "会计政策": 0.6,
            "会计估计": 0.7,
            "审计问题": 2.0,
            "审计师变更": 1.8,
            "历史违规": 1.8,
            "费用资本化": 1.2,
            "资产高估": 1.2,
            "负债隐瞒": 1.3,
            "报表勾稽": 1.6,
        }
        
        # 风险等级对应的分值
        self.level_scores = {
            RiskLevel.LOW: 1.0,
            RiskLevel.MEDIUM: 3.0,
            RiskLevel.HIGH: 6.0,
            RiskLevel.CRITICAL: 10.0,
        }
    
    def assess_risk(self, fraud_patterns: List[FraudPattern], financial_data: FinancialData) -> RiskAssessment:
        """评估风险
        
        采用多维度综合评估：
        1. 加权分数：每个模式的分数 × 权重
        2. 风险密度：高风险模式占比
        3. 最高风险等级：是否存在CRITICAL
        4. 风险集中度：高风险指标在总指标中的占比
        """
        risk_assessment = RiskAssessment()
        risk_assessment.fraud_patterns = fraud_patterns
        
        # 计算每个模式的风险评分
        for pattern in fraud_patterns:
            pattern.calculate_score()
        
        if not fraud_patterns:
            risk_assessment.total_score = 0.0
            risk_assessment.risk_level = RiskLevel.LOW
            return risk_assessment
        
        # === 维度1：加权分数 ===
        weighted_score = self._calc_weighted_score(fraud_patterns)
        
        # === 维度2：风险密度（高风险模式占比） ===
        high_critical_count = sum(
            1 for p in fraud_patterns 
            if p.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        risk_density = high_critical_count / len(fraud_patterns)
        
        # === 维度3：最高风险等级 ===
        max_risk = RiskLevel.LOW
        for pattern in fraud_patterns:
            if pattern.risk_level == RiskLevel.CRITICAL:
                max_risk = RiskLevel.CRITICAL
                break
            elif pattern.risk_level == RiskLevel.HIGH and max_risk != RiskLevel.CRITICAL:
                max_risk = RiskLevel.HIGH
            elif pattern.risk_level == RiskLevel.MEDIUM and max_risk not in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                max_risk = RiskLevel.MEDIUM
        
        # === 维度4：风险集中度（高风险指标数/总指标数） ===
        total_indicators = 0
        high_critical_indicators = 0
        for pattern in fraud_patterns:
            for indicator in pattern.indicators:
                total_indicators += 1
                if indicator.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    high_critical_indicators += 1
        risk_concentration = high_critical_indicators / total_indicators if total_indicators > 0 else 0
        
        # === 综合评分 ===
        # 基础分：加权分数（上限25分）
        base_score = min(weighted_score, 25.0)
        
        # 风险密度加分：高风险模式占比越高，加分越多
        # density=0.5 → +5, density=0.75 → +10, density=1.0 → +15
        density_bonus = risk_density * 15.0
        
        # 风险集中度加分：高风险指标占比
        # concentration=0.5 → +5, concentration=0.75 → +7.5, concentration=1.0 → +10
        concentration_bonus = risk_concentration * 10.0
        
        # 最高风险等级加分
        max_risk_bonus = {
            RiskLevel.CRITICAL: 10.0,
            RiskLevel.HIGH: 5.0,
            RiskLevel.MEDIUM: 0.0,
            RiskLevel.LOW: 0.0,
        }[max_risk]
        
        # 综合得分（上限50）
        total_score = min(base_score + density_bonus + concentration_bonus + max_risk_bonus, 50.0)
        
        risk_assessment.total_score = round(total_score, 1)
        
        # 确定风险等级
        risk_assessment.risk_level = self._determine_risk_level(total_score, max_risk, risk_density)
        
        # 生成关键风险点
        risk_assessment.key_risks = self._extract_key_risks(fraud_patterns)
        
        # 生成建议
        risk_assessment.recommendations = self._generate_recommendations(
            fraud_patterns, financial_data, risk_assessment.risk_level
        )
        
        return risk_assessment
    
    def _calc_weighted_score(self, fraud_patterns: List[FraudPattern]) -> float:
        """计算加权分数"""
        weighted_score = 0.0
        
        for pattern in fraud_patterns:
            pattern_score = pattern.total_score
            pattern_name = pattern.name
            
            # 匹配权重
            weight = 1.0
            for key, w in self.pattern_weights.items():
                if key in pattern_name:
                    weight = w
                    break
            
            weighted_score += pattern_score * weight
        
        return weighted_score
    
    def _determine_risk_level(self, score: float, max_risk: RiskLevel, risk_density: float) -> RiskLevel:
        """确定风险等级
        
        综合考虑分数、最高风险等级和风险密度：
        - 存在CRITICAL模式 → 至少HIGH
        - 高风险密度(>60%) + 分数>15 → 至少HIGH
        - 分数阈值适当降低，因为分数不再被稀释
        """
        # 如果存在CRITICAL级别模式，至少是HIGH
        if max_risk == RiskLevel.CRITICAL:
            if score >= 30 or risk_density >= 0.5:
                return RiskLevel.CRITICAL
            return RiskLevel.HIGH
        
        # 高风险密度：超过60%的模式是高风险
        if risk_density >= 0.6 and score >= 15:
            return RiskLevel.HIGH
        
        # 常规分数阈值
        if score >= 35:
            return RiskLevel.CRITICAL
        elif score >= 22:
            return RiskLevel.HIGH
        elif score >= 12:
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
        """生成投资建议"""
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

"""
风险评估器

采用多维度差异化评分模型，确保不同风险程度的企业有明确区分：

评分维度：
1. 模式严重度（按风险等级计分，非线性）：HIGH=8, MEDIUM=3, CRITICAL=15
2. 财务严重度（亏损、收入暴跌等极端情况的额外加分）
3. 风险密度（高风险模式占比，用平方放大差异）
4. 风险广度（触发模式数量，越多越危险）
5. 风险集中度（高风险指标占比）
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
        
        # 风险等级 → 基础分（非线性，拉开差距）
        self.level_base_scores = {
            RiskLevel.CRITICAL: 8.0,
            RiskLevel.HIGH: 4.5,
            RiskLevel.MEDIUM: 1.5,
            RiskLevel.LOW: 0.3,
        }
    
    def assess_risk(self, fraud_patterns: List[FraudPattern], financial_data: FinancialData) -> RiskAssessment:
        """评估风险"""
        risk_assessment = RiskAssessment()
        risk_assessment.fraud_patterns = fraud_patterns
        
        for pattern in fraud_patterns:
            pattern.calculate_score()
        
        if not fraud_patterns:
            risk_assessment.total_score = 0.0
            risk_assessment.risk_level = RiskLevel.LOW
            return risk_assessment
        
        # === 维度1：模式严重度（核心区分维度）===
        severity_score = self._calc_severity_score(fraud_patterns)
        
        # === 维度2：财务严重度（极端财务状况加分）===
        financial_severity = self._calc_financial_severity(financial_data)
        
        # === 维度3：风险密度（高风险模式占比，平方放大差异）===
        high_critical_count = sum(
            1 for p in fraud_patterns 
            if p.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        risk_density = high_critical_count / len(fraud_patterns)
        # 用1.5次方放大差异：0.5→0.35, 0.62→0.49, 0.83→0.76
        density_score = (risk_density ** 1.5) * 8.0
        
        # === 维度4：风险广度（模式数量加分）===
        # 3个模式→1.5, 6个→3.0, 8个→4.0, 10个→5.0
        breadth_score = min(len(fraud_patterns) * 0.5, 5.0)
        
        # === 维度5：风险集中度 ===
        total_indicators = 0
        high_critical_indicators = 0
        for pattern in fraud_patterns:
            for indicator in pattern.indicators:
                total_indicators += 1
                if indicator.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    high_critical_indicators += 1
        risk_concentration = high_critical_indicators / total_indicators if total_indicators > 0 else 0
        concentration_score = (risk_concentration ** 1.3) * 4.0
        
        # === 最高风险等级 ===
        max_risk = RiskLevel.LOW
        for pattern in fraud_patterns:
            if pattern.risk_level == RiskLevel.CRITICAL:
                max_risk = RiskLevel.CRITICAL
                break
            elif pattern.risk_level == RiskLevel.HIGH and max_risk != RiskLevel.CRITICAL:
                max_risk = RiskLevel.HIGH
            elif pattern.risk_level == RiskLevel.MEDIUM and max_risk not in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                max_risk = RiskLevel.MEDIUM
        
        max_risk_bonus = {
            RiskLevel.CRITICAL: 5.0,
            RiskLevel.HIGH: 2.0,
            RiskLevel.MEDIUM: 0.0,
            RiskLevel.LOW: 0.0,
        }[max_risk]
        
        # === 综合评分 ===
        total_score = min(
            severity_score + financial_severity + density_score + breadth_score + concentration_score + max_risk_bonus,
            50.0
        )
        
        risk_assessment.total_score = round(total_score, 1)
        risk_assessment.risk_level = self._determine_risk_level(total_score, max_risk, risk_density)
        risk_assessment.key_risks = self._extract_key_risks(fraud_patterns)
        risk_assessment.recommendations = self._generate_recommendations(
            fraud_patterns, financial_data, risk_assessment.risk_level
        )
        
        return risk_assessment
    
    def _calc_severity_score(self, fraud_patterns: List[FraudPattern]) -> float:
        """计算模式严重度
        
        每个模式按风险等级给基础分，再乘以权重。
        用等级基础分而非indicator小分数，拉开差距。
        """
        total = 0.0
        for pattern in fraud_patterns:
            # 按风险等级给基础分
            base = self.level_base_scores.get(pattern.risk_level, 1.0)
            
            # 匹配权重
            weight = 1.0
            for key, w in self.pattern_weights.items():
                if key in pattern.name:
                    weight = w
                    break
            
            total += base * weight
        
        return total
    
    def _calc_financial_severity(self, financial_data: FinancialData) -> float:
        """计算财务严重度
        
        对极端财务状况额外加分，这些是比"指标异常"更严重的信号：
        - 净利润为负（亏损）：+5
        - 收入同比下降超过20%：+3
        - 经营现金流为负：+4
        - 资产负债率超过70%：+2
        """
        bonus = 0.0
        current = financial_data.current_year
        
        # 净利润为负（亏损）—— 比利润下降严重得多
        if current.net_profit < 0:
            bonus += 3.0
            # 亏损金额越大越严重
            if current.operating_revenue > 0:
                loss_ratio = abs(current.net_profit) / current.operating_revenue
                if loss_ratio > 0.05:  # 亏损超过收入5%
                    bonus += 1.5
        
        # 收入大幅下降
        revenue_growth = financial_data.get_growth_rate("operating_revenue", 1)
        if revenue_growth < -20:
            bonus += 2.0
        elif revenue_growth < -10:
            bonus += 1.0
        
        # 经营现金流为负
        if current.net_cash_flow_operating < 0:
            bonus += 2.5
        
        # 资产负债率过高
        if current.debt_ratio > 70:
            bonus += 1.5
        elif current.debt_ratio > 60:
            bonus += 0.5
        
        return bonus
    
    def _determine_risk_level(self, score: float, max_risk: RiskLevel, risk_density: float) -> RiskLevel:
        """确定风险等级"""
        # CRITICAL模式 → 至少HIGH，分数够高则CRITICAL
        if max_risk == RiskLevel.CRITICAL:
            if score >= 35 or risk_density >= 0.5:
                return RiskLevel.CRITICAL
            return RiskLevel.HIGH
        
        # 高风险密度 + 分数够高 → CRITICAL
        if risk_density >= 0.6 and score >= 30:
            return RiskLevel.CRITICAL
        
        # 常规分数阈值
        if score >= 38:
            return RiskLevel.CRITICAL
        elif score >= 25:
            return RiskLevel.HIGH
        elif score >= 14:
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
        
        if not key_risks:
            for pattern in fraud_patterns:
                if pattern.risk_level == RiskLevel.MEDIUM:
                    for indicator in pattern.indicators:
                        if indicator.risk_level == RiskLevel.MEDIUM:
                            key_risks.append(f"{pattern.name}: {indicator.name}")
        
        return key_risks[:5]
    
    def _generate_recommendations(self, fraud_patterns: List[FraudPattern], 
                                 financial_data: FinancialData, 
                                 risk_level: RiskLevel) -> List[str]:
        """生成建议"""
        recommendations = []
        
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
        
        for pattern in fraud_patterns:
            if pattern.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                for indicator in pattern.indicators:
                    if indicator.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                        recommendations.extend(indicator.recommendations)
        
        unique_recommendations = []
        seen = set()
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:10]
    
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

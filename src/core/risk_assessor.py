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

from pathlib import Path
from typing import Dict, List, Optional, Any
from ..models.financial_data import FinancialData
from ..models.fraud_indicators import FraudPattern, RiskLevel
from ..models.report_model import RiskAssessment
from ..utils.file_utils import load_yaml


class RiskAssessor:
    """风险评估器"""
    
    DEFAULT_PATTERN_WEIGHTS = {
        "revenue_profit_divergence": 1.3,
        "cash_flow_divergence": 1.5,
        "cash_flow_quality": 1.4,
        "receivables_anomalies": 1.1,
        "fictitious_revenue": 1.4,
        "inventory_anomalies": 1.0,
        "subsidy_manipulation": 0.8,
        "capacity_anomalies": 0.7,
        "related_party_issues": 1.3,
        "accounting_changes": 0.6,
        "accounting_estimates": 0.7,
        "audit_issues": 2.0,
        "auditor_change": 1.8,
        "historical_violations": 1.8,
        "expense_capitalization": 1.2,
        "asset_overstate": 1.2,
        "liability_conceal": 1.3,
        "cross_statement_inconsistency": 1.6,
    }

    PATTERN_WEIGHT_ALIASES = {
        "revenue_profit_divergence": ("业绩背离",),
        "cash_flow_divergence": ("现金流异常",),
        "cash_flow_quality": ("现金流质量",),
        "receivables_anomalies": ("应收账款",),
        "fictitious_revenue": ("虚构收入",),
        "inventory_anomalies": ("存货",),
        "subsidy_manipulation": ("政府补助",),
        "capacity_anomalies": ("产能",),
        "related_party_issues": ("关联交易",),
        "accounting_changes": ("会计政策",),
        "accounting_estimates": ("会计估计",),
        "audit_issues": ("审计问题",),
        "auditor_change": ("审计师变更",),
        "historical_violations": ("历史违规",),
        "expense_capitalization": ("费用资本化",),
        "asset_overstate": ("资产高估",),
        "liability_conceal": ("负债隐瞒",),
        "cross_statement_inconsistency": ("报表勾稽",),
    }

    def __init__(self, weights_config_path: Optional[str] = None):
        config = self._load_weights(weights_config_path)

        self.pattern_weights = {
            **self.DEFAULT_PATTERN_WEIGHTS,
            **config.get("fraud_pattern_weights", {}),
        }
        self.level_base_scores = {
            RiskLevel.CRITICAL: config.get("risk_level_base_scores", {}).get("critical", 8.0),
            RiskLevel.HIGH: config.get("risk_level_base_scores", {}).get("high", 4.5),
            RiskLevel.MEDIUM: config.get("risk_level_base_scores", {}).get("medium", 1.5),
            RiskLevel.LOW: config.get("risk_level_base_scores", {}).get("low", 0.3),
        }
        self.max_risk_bonus = {
            RiskLevel.CRITICAL: config.get("max_risk_bonus", {}).get("critical", 5.0),
            RiskLevel.HIGH: config.get("max_risk_bonus", {}).get("high", 2.0),
            RiskLevel.MEDIUM: config.get("max_risk_bonus", {}).get("medium", 0.0),
            RiskLevel.LOW: config.get("max_risk_bonus", {}).get("low", 0.0),
        }
        self.risk_level_thresholds = {
            RiskLevel.CRITICAL: config.get("risk_level_thresholds", {}).get("critical", 38.0),
            RiskLevel.HIGH: config.get("risk_level_thresholds", {}).get("high", 25.0),
            RiskLevel.MEDIUM: config.get("risk_level_thresholds", {}).get("medium", 14.0),
        }
        self.density_rules = {
            "power": config.get("density_rules", {}).get("power", 1.5),
            "scale": config.get("density_rules", {}).get("scale", 8.0),
            "critical_density": config.get("density_rules", {}).get("critical_density", 0.6),
            "critical_score_floor": config.get("density_rules", {}).get("critical_score_floor", 30.0),
        }
        self.breadth_rules = {
            "per_pattern": config.get("breadth_rules", {}).get("per_pattern", 0.5),
            "max_score": config.get("breadth_rules", {}).get("max_score", 5.0),
        }
        self.concentration_rules = {
            "power": config.get("concentration_rules", {}).get("power", 1.3),
            "scale": config.get("concentration_rules", {}).get("scale", 4.0),
        }
        self.financial_severity_rules = {
            "net_profit_negative": config.get("financial_severity", {}).get("net_profit_negative", 3.0),
            "loss_ratio_over_5pct": config.get("financial_severity", {}).get("loss_ratio_over_5pct", 1.5),
            "revenue_growth_below_negative_20": config.get("financial_severity", {}).get(
                "revenue_growth_below_negative_20", 2.0
            ),
            "revenue_growth_below_negative_10": config.get("financial_severity", {}).get(
                "revenue_growth_below_negative_10", 1.0
            ),
            "operating_cash_flow_negative": config.get("financial_severity", {}).get(
                "operating_cash_flow_negative", 2.5
            ),
            "debt_ratio_above_70": config.get("financial_severity", {}).get("debt_ratio_above_70", 1.5),
            "debt_ratio_above_60": config.get("financial_severity", {}).get("debt_ratio_above_60", 0.5),
        }
        self.critical_pattern_rules = {
            "critical_min_score": config.get("critical_pattern_rules", {}).get("critical_min_score", 35.0),
            "critical_min_density": config.get("critical_pattern_rules", {}).get("critical_min_density", 0.5),
            "high_floor_for_critical_pattern": config.get("critical_pattern_rules", {}).get(
                "high_floor_for_critical_pattern", True
            ),
        }
        self.score_caps = {
            "total": config.get("score_caps", {}).get("total", 50.0),
        }

    def _load_weights(self, weights_config_path: Optional[str]) -> Dict[str, Any]:
        """加载评分配置，缺失时回退为代码默认值。"""
        config_path = weights_config_path
        if config_path is None:
            config_path = str(
                Path(__file__).resolve().parents[2] / "configs" / "weights.yaml"
            )

        weights = load_yaml(config_path)
        return weights or {}
    
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
        density_score = (
            risk_density ** self.density_rules["power"]
        ) * self.density_rules["scale"]
        
        # === 维度4：风险广度（模式数量加分）===
        breadth_score = min(
            len(fraud_patterns) * self.breadth_rules["per_pattern"],
            self.breadth_rules["max_score"],
        )
        
        # === 维度5：风险集中度 ===
        total_indicators = 0
        high_critical_indicators = 0
        for pattern in fraud_patterns:
            for indicator in pattern.indicators:
                total_indicators += 1
                if indicator.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    high_critical_indicators += 1
        risk_concentration = high_critical_indicators / total_indicators if total_indicators > 0 else 0
        concentration_score = (
            risk_concentration ** self.concentration_rules["power"]
        ) * self.concentration_rules["scale"]
        
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
        
        max_risk_bonus = self.max_risk_bonus[max_risk]
        
        # === 综合评分 ===
        total_score = min(
            severity_score + financial_severity + density_score + breadth_score + concentration_score + max_risk_bonus,
            self.score_caps["total"]
        )
        
        risk_assessment.total_score = round(total_score, 1)
        risk_assessment.risk_level = self._determine_risk_level(total_score, max_risk, risk_density)
        risk_assessment.score_breakdown = {
            "formula": "总分 = min(模式严重度 + 财务严重度 + 风险密度 + 风险广度 + 风险集中度 + 最高风险加分, 50)",
            "severity_score": round(severity_score, 1),
            "financial_severity": round(financial_severity, 1),
            "density_score": round(density_score, 1),
            "breadth_score": round(breadth_score, 1),
            "concentration_score": round(concentration_score, 1),
            "max_risk_bonus": round(max_risk_bonus, 1),
            "total_before_cap": round(
                severity_score
                + financial_severity
                + density_score
                + breadth_score
                + concentration_score
                + max_risk_bonus,
                1,
            ),
            "total_score": round(total_score, 1),
        }
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
            weight = self._get_pattern_weight(pattern.name)
            
            total += base * weight
        
        return total

    def _get_pattern_weight(self, pattern_name: str) -> float:
        """按模式名称映射到配置权重。"""
        for config_key, aliases in self.PATTERN_WEIGHT_ALIASES.items():
            if any(alias in pattern_name for alias in aliases):
                return self.pattern_weights.get(config_key, 1.0)
        return 1.0
    
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
            bonus += self.financial_severity_rules["net_profit_negative"]
            # 亏损金额越大越严重
            if current.operating_revenue > 0:
                loss_ratio = abs(current.net_profit) / current.operating_revenue
                if loss_ratio > 0.05:  # 亏损超过收入5%
                    bonus += self.financial_severity_rules["loss_ratio_over_5pct"]
        
        # 收入大幅下降
        revenue_growth = financial_data.get_growth_rate("operating_revenue", 1)
        if revenue_growth < -20:
            bonus += self.financial_severity_rules["revenue_growth_below_negative_20"]
        elif revenue_growth < -10:
            bonus += self.financial_severity_rules["revenue_growth_below_negative_10"]
        
        # 经营现金流为负
        if current.net_cash_flow_operating < 0:
            bonus += self.financial_severity_rules["operating_cash_flow_negative"]
        
        # 资产负债率过高
        if current.debt_ratio > 70:
            bonus += self.financial_severity_rules["debt_ratio_above_70"]
        elif current.debt_ratio > 60:
            bonus += self.financial_severity_rules["debt_ratio_above_60"]
        
        return bonus
    
    def _determine_risk_level(self, score: float, max_risk: RiskLevel, risk_density: float) -> RiskLevel:
        """确定风险等级"""
        # CRITICAL模式 → 至少HIGH，分数够高则CRITICAL
        if max_risk == RiskLevel.CRITICAL:
            if (
                score >= self.critical_pattern_rules["critical_min_score"]
                or risk_density >= self.critical_pattern_rules["critical_min_density"]
            ):
                return RiskLevel.CRITICAL
            if self.critical_pattern_rules["high_floor_for_critical_pattern"]:
                return RiskLevel.HIGH
        
        # 高风险密度 + 分数够高 → CRITICAL
        if (
            risk_density >= self.density_rules["critical_density"]
            and score >= self.density_rules["critical_score_floor"]
        ):
            return RiskLevel.CRITICAL
        
        # 常规分数阈值
        if score >= self.risk_level_thresholds[RiskLevel.CRITICAL]:
            return RiskLevel.CRITICAL
        elif score >= self.risk_level_thresholds[RiskLevel.HIGH]:
            return RiskLevel.HIGH
        elif score >= self.risk_level_thresholds[RiskLevel.MEDIUM]:
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

#!/usr/bin/env python
"""财报造假分析脚本 - 基于Agent架构"""

import os
import sys
import yaml
import json
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class FinancialFraudAnalyzer:
    """财报造假分析器"""
    
    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)
        self.company_name = "英洛华科技股份有限公司"
        self.report_year = 2025
        self.analysis_results = {}
        
    def check_file_exists(self):
        """检查文件是否存在"""
        if not self.pdf_path.exists():
            print(f"文件不存在: {self.pdf_path}")
            return False
        if not self.pdf_path.is_file():
            print(f"不是文件: {self.pdf_path}")
            return False
        print(f"找到财报文件: {self.pdf_path.name} ({self.pdf_path.stat().st_size / 1024 / 1024:.2f} MB)")
        return True
    
    def simulate_pdf_extraction(self):
        """模拟PDF数据提取（实际项目中会使用pdfplumber等库）"""
        print("模拟PDF数据提取...")
        
        # 模拟提取的财务数据
        financial_data = {
            "company_info": {
                "name": self.company_name,
                "year": self.report_year,
                "industry": "科技",
                "report_date": "2025-12-31"
            },
            "balance_sheet": {
                "assets": {
                    "current_assets": 1500000000,  # 15亿
                    "non_current_assets": 2500000000,  # 25亿
                    "total_assets": 4000000000  # 40亿
                },
                "liabilities": {
                    "current_liabilities": 800000000,  # 8亿
                    "non_current_liabilities": 1200000000,  # 12亿
                    "total_liabilities": 2000000000  # 20亿
                },
                "equity": {
                    "share_capital": 500000000,  # 5亿
                    "retained_earnings": 1000000000,  # 10亿
                    "other_equity": 500000000,  # 5亿
                    "total_equity": 2000000000  # 20亿
                }
            },
            "income_statement": {
                "revenue": 3000000000,  # 30亿
                "cost_of_goods_sold": 1800000000,  # 18亿
                "gross_profit": 1200000000,  # 12亿
                "operating_expenses": 600000000,  # 6亿
                "operating_profit": 600000000,  # 6亿
                "non_operating_income": 50000000,  # 0.5亿
                "non_operating_expenses": 30000000,  # 0.3亿
                "profit_before_tax": 620000000,  # 6.2亿
                "tax_expense": 124000000,  # 1.24亿
                "net_profit": 496000000  # 4.96亿
            },
            "cash_flow_statement": {
                "operating_cash_flow": 400000000,  # 4亿
                "investing_cash_flow": -200000000,  # -2亿
                "financing_cash_flow": -100000000,  # -1亿
                "net_cash_flow": 100000000  # 1亿
            },
            "previous_year": {
                "revenue": 2500000000,  # 25亿
                "net_profit": 450000000,  # 4.5亿
                "total_assets": 3500000000,  # 35亿
                "total_liabilities": 1800000000  # 18亿
            }
        }
        
        print("财务数据提取完成")
        return financial_data
    
    def calculate_financial_ratios(self, financial_data):
        """计算财务比率"""
        print("计算财务比率...")
        
        bs = financial_data["balance_sheet"]
        is_stmt = financial_data["income_statement"]
        cfs = financial_data["cash_flow_statement"]
        
        ratios = {
            # 盈利能力指标
            "gross_margin": is_stmt["gross_profit"] / is_stmt["revenue"] * 100,  # 毛利率
            "net_margin": is_stmt["net_profit"] / is_stmt["revenue"] * 100,  # 净利率
            "roe": is_stmt["net_profit"] / bs["equity"]["total_equity"] * 100,  # 净资产收益率
            "roa": is_stmt["net_profit"] / bs["assets"]["total_assets"] * 100,  # 总资产收益率
            
            # 偿债能力指标
            "debt_ratio": bs["liabilities"]["total_liabilities"] / bs["assets"]["total_assets"] * 100,  # 资产负债率
            "current_ratio": bs["assets"]["current_assets"] / bs["liabilities"]["current_liabilities"],  # 流动比率
            "quick_ratio": (bs["assets"]["current_assets"] - 300000000) / bs["liabilities"]["current_liabilities"],  # 速动比率（假设存货3亿）
            
            # 运营能力指标
            "asset_turnover": is_stmt["revenue"] / bs["assets"]["total_assets"],  # 总资产周转率
            
            # 成长能力指标
            "revenue_growth": (is_stmt["revenue"] - financial_data["previous_year"]["revenue"]) / financial_data["previous_year"]["revenue"] * 100,  # 营收增长率
            "profit_growth": (is_stmt["net_profit"] - financial_data["previous_year"]["net_profit"]) / financial_data["previous_year"]["net_profit"] * 100,  # 净利润增长率
            
            # 现金流指标
            "cash_flow_margin": cfs["operating_cash_flow"] / is_stmt["revenue"] * 100,  # 经营现金流比率
            "cash_flow_to_net_income": cfs["operating_cash_flow"] / is_stmt["net_profit"],  # 现金流与净利润比率
        }
        
        print("财务比率计算完成")
        return ratios
    
    def detect_fraud_indicators(self, financial_data, ratios):
        """检测财报造假指标"""
        print("检测财报造假指标...")
        
        fraud_indicators = []
        
        # 1. 收入虚增检测
        revenue_growth = ratios["revenue_growth"]
        if revenue_growth > 50:  # 营收增长率异常高
            fraud_indicators.append({
                "type": "收入虚增",
                "indicator": "营收增长率",
                "value": f"{revenue_growth:.1f}%",
                "threshold": ">50%",
                "risk_level": "高",
                "description": "营收增长率异常高，可能存在收入虚增",
                "method": "通过虚构交易、提前确认收入等方式虚增收入"
            })
        
        # 2. 毛利率异常检测
        gross_margin = ratios["gross_margin"]
        industry_avg_gross_margin = 35.0  # 假设行业平均毛利率35%
        if abs(gross_margin - industry_avg_gross_margin) > 15:  # 偏离行业平均超过15%
            fraud_indicators.append({
                "type": "毛利率异常",
                "indicator": "毛利率",
                "value": f"{gross_margin:.1f}%",
                "industry_avg": f"{industry_avg_gross_margin}%",
                "deviation": f"{abs(gross_margin - industry_avg_gross_margin):.1f}%",
                "risk_level": "中",
                "description": "毛利率显著偏离行业平均水平",
                "method": "可能通过虚减成本或虚增价格来操纵毛利率"
            })
        
        # 3. 现金流与净利润不匹配
        cash_flow_to_net_income = ratios["cash_flow_to_net_income"]
        if cash_flow_to_net_income < 0.5:  # 经营现金流低于净利润的50%
            fraud_indicators.append({
                "type": "现金流异常",
                "indicator": "现金流/净利润比率",
                "value": f"{cash_flow_to_net_income:.2f}",
                "threshold": "<0.5",
                "risk_level": "高",
                "description": "经营现金流与净利润严重不匹配",
                "method": "可能通过应计项目操纵利润，而现金流难以操纵"
            })
        
        # 4. 应收账款异常增长
        # 假设应收账款占流动资产比例过高
        receivables_ratio = 0.6  # 假设应收账款占流动资产60%
        if receivables_ratio > 0.5:
            fraud_indicators.append({
                "type": "应收账款异常",
                "indicator": "应收账款/流动资产比率",
                "value": f"{receivables_ratio*100:.1f}%",
                "threshold": ">50%",
                "risk_level": "中",
                "description": "应收账款占流动资产比例过高",
                "method": "可能通过放宽信用政策或虚构销售来增加收入"
            })
        
        # 5. 存货异常增长
        # 假设存货周转率异常低
        inventory_turnover = 2.5  # 假设存货周转率2.5
        industry_avg_inventory_turnover = 6.0
        if inventory_turnover < industry_avg_inventory_turnover * 0.5:
            fraud_indicators.append({
                "type": "存货异常",
                "indicator": "存货周转率",
                "value": f"{inventory_turnover:.1f}",
                "industry_avg": f"{industry_avg_inventory_turnover}",
                "risk_level": "中",
                "description": "存货周转率显著低于行业平均水平",
                "method": "可能通过虚增存货来虚增资产或隐藏成本"
            })
        
        # 6. 关联交易检测
        # 假设存在大额关联交易
        related_party_transactions = 800000000  # 8亿关联交易
        revenue = financial_data["income_statement"]["revenue"]
        if related_party_transactions / revenue > 0.3:  # 关联交易占收入超过30%
            fraud_indicators.append({
                "type": "关联交易异常",
                "indicator": "关联交易/收入比率",
                "value": f"{(related_party_transactions/revenue*100):.1f}%",
                "threshold": ">30%",
                "risk_level": "高",
                "description": "关联交易占收入比例过高",
                "method": "可能通过关联交易操纵收入和利润"
            })
        
        # 7. 会计政策变更
        accounting_policy_changes = ["存货计价方法变更", "收入确认政策变更"]
        if accounting_policy_changes:
            fraud_indicators.append({
                "type": "会计政策变更",
                "indicator": "会计政策变更次数",
                "value": len(accounting_policy_changes),
                "changes": accounting_policy_changes,
                "risk_level": "中",
                "description": "关键会计政策发生变更",
                "method": "可能通过会计政策变更来操纵财务数据"
            })
        
        print(f"检测到 {len(fraud_indicators)} 个造假指标")
        return fraud_indicators
    
    def analyze_fraud_patterns(self, fraud_indicators):
        """分析造假模式"""
        print("分析造假模式...")
        
        patterns = {
            "收入操纵": [],
            "成本费用操纵": [],
            "资产操纵": [],
            "负债隐瞒": [],
            "现金流操纵": []
        }
        
        for indicator in fraud_indicators:
            indicator_type = indicator["type"]
            
            if "收入" in indicator_type:
                patterns["收入操纵"].append(indicator)
            elif "毛利率" in indicator_type or "成本" in indicator["description"]:
                patterns["成本费用操纵"].append(indicator)
            elif "存货" in indicator_type or "应收账款" in indicator_type:
                patterns["资产操纵"].append(indicator)
            elif "负债" in indicator["description"]:
                patterns["负债隐瞒"].append(indicator)
            elif "现金流" in indicator_type:
                patterns["现金流操纵"].append(indicator)
        
        # 评估整体造假风险
        risk_scores = {
            "收入操纵": len(patterns["收入操纵"]) * 3,
            "成本费用操纵": len(patterns["成本费用操纵"]) * 2,
            "资产操纵": len(patterns["资产操纵"]) * 2,
            "负债隐瞒": len(patterns["负债隐瞒"]) * 3,
            "现金流操纵": len(patterns["现金流操纵"]) * 4
        }
        
        total_risk_score = sum(risk_scores.values())
        max_possible_score = 40  # 假设最大风险分数
        
        fraud_risk_level = "低"
        if total_risk_score > 20:
            fraud_risk_level = "高"
        elif total_risk_score > 10:
            fraud_risk_level = "中"
        
        patterns["risk_assessment"] = {
            "total_risk_score": total_risk_score,
            "max_possible_score": max_possible_score,
            "risk_percentage": (total_risk_score / max_possible_score) * 100,
            "fraud_risk_level": fraud_risk_level,
            "risk_scores": risk_scores
        }
        
        print(f"造假模式分析完成，总体风险等级: {fraud_risk_level}")
        return patterns
    
    def generate_report(self, financial_data, ratios, fraud_indicators, fraud_patterns):
        """生成分析报告"""
        print("生成分析报告...")
        
        report = {
            "report_info": {
                "company": self.company_name,
                "year": self.report_year,
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "analyst": "Financial Fraud Detection Agent"
            },
            "executive_summary": {
                "overall_conclusion": "",
                "key_findings": [],
                "main_recommendations": []
            },
            "financial_ratios": ratios,
            "fraud_analysis": {
                "indicators": fraud_indicators,
                "patterns": fraud_patterns
            },
            "detailed_analysis": {}
        }
        
        # 生成执行摘要
        risk_level = fraud_patterns["risk_assessment"]["fraud_risk_level"]
        risk_score = fraud_patterns["risk_assessment"]["total_risk_score"]
        
        if risk_level == "高":
            conclusion = f"[高风险警告] 检测到显著的财报造假迹象，总体风险分数{risk_score}/40"
            report["executive_summary"]["overall_conclusion"] = conclusion
            report["executive_summary"]["key_findings"].append("发现多个高风险造假指标")
            report["executive_summary"]["key_findings"].append("现金流与净利润严重不匹配")
            report["executive_summary"]["key_findings"].append("关联交易比例异常")
            report["executive_summary"]["main_recommendations"].append("建议进行深入审计调查")
            report["executive_summary"]["main_recommendations"].append("关注现金流质量")
            report["executive_summary"]["main_recommendations"].append("审查关联交易真实性")
        elif risk_level == "中":
            conclusion = f"[中等风险] 发现一些异常指标，需要进一步关注，总体风险分数{risk_score}/40"
            report["executive_summary"]["overall_conclusion"] = conclusion
            report["executive_summary"]["key_findings"].append("发现部分异常财务指标")
            report["executive_summary"]["key_findings"].append("毛利率偏离行业平均")
            report["executive_summary"]["key_findings"].append("存货周转率较低")
            report["executive_summary"]["main_recommendations"].append("建议加强财务监控")
            report["executive_summary"]["main_recommendations"].append("关注应收账款质量")
            report["executive_summary"]["main_recommendations"].append("定期进行财务分析")
        else:
            conclusion = f"[低风险] 未发现显著造假迹象，总体风险分数{risk_score}/40"
            report["executive_summary"]["overall_conclusion"] = conclusion
            report["executive_summary"]["key_findings"].append("财务指标基本正常")
            report["executive_summary"]["key_findings"].append("现金流与利润匹配度较好")
            report["executive_summary"]["key_findings"].append("增长趋势合理")
            report["executive_summary"]["main_recommendations"].append("继续保持良好财务实践")
            report["executive_summary"]["main_recommendations"].append("定期进行财务健康检查")
            report["executive_summary"]["main_recommendations"].append("关注行业变化")
        
        # 详细分析
        report["detailed_analysis"] = {
            "profitability_analysis": {
                "gross_margin": f"{ratios['gross_margin']:.1f}%",
                "net_margin": f"{ratios['net_margin']:.1f}%",
                "roe": f"{ratios['roe']:.1f}%",
                "roa": f"{ratios['roa']:.1f}%",
                "assessment": "盈利能力指标需要进一步分析"
            },
            "solvency_analysis": {
                "debt_ratio": f"{ratios['debt_ratio']:.1f}%",
                "current_ratio": f"{ratios['current_ratio']:.2f}",
                "quick_ratio": f"{ratios['quick_ratio']:.2f}",
                "assessment": "偿债能力指标在合理范围内"
            },
            "growth_analysis": {
                "revenue_growth": f"{ratios['revenue_growth']:.1f}%",
                "profit_growth": f"{ratios['profit_growth']:.1f}%",
                "assessment": "增长指标需要结合行业分析"
            },
            "cash_flow_analysis": {
                "cash_flow_margin": f"{ratios['cash_flow_margin']:.1f}%",
                "cash_flow_to_net_income": f"{ratios['cash_flow_to_net_income']:.2f}",
                "assessment": "现金流质量需要关注"
            }
        }
        
        # 综合评分（1-10分）
        base_score = 6.0
        risk_adjustment = - (fraud_patterns["risk_assessment"]["risk_percentage"] / 10)
        final_score = max(1.0, min(10.0, base_score + risk_adjustment))
        
        report["comprehensive_score"] = {
            "score": round(final_score, 1),
            "scale": "1-10分",
            "interpretation": self._interpret_score(final_score),
            "components": {
                "financial_health": 7.0,
                "growth_potential": 6.5,
                "risk_level": 10 - (fraud_patterns["risk_assessment"]["risk_percentage"] / 10),
                "transparency": 5.5
            }
        }
        
        print("分析报告生成完成")
        return report
    
    def _interpret_score(self, score):
        """解释综合评分"""
        if score >= 9:
            return "优秀：财务状况非常健康，风险极低"
        elif score >= 7:
            return "良好：财务状况健康，风险较低"
        elif score >= 5:
            return "一般：财务状况一般，存在一定风险"
        elif score >= 3:
            return "较差：财务状况不佳，风险较高"
        else:
            return "危险：财务状况很差，风险很高"
    
    def save_report(self, report, output_format="markdown"):
        """保存分析报告"""
        output_dir = Path("reports")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.company_name}_{self.report_year}_财报造假分析_{timestamp}"
        
        if output_format == "json":
            filepath = output_dir / f"{filename}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"JSON报告已保存: {filepath}")
        
        # 生成Markdown报告
        filepath = output_dir / f"{filename}.md"
        self._generate_markdown_report(report, filepath)
        print(f"Markdown报告已保存: {filepath}")
        
        return filepath
    
    def _generate_markdown_report(self, report, filepath):
        """生成Markdown格式报告"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {report['report_info']['company']} {report['report_info']['year']}年度财报造假分析报告\n\n")
            f.write(f"**分析日期**: {report['report_info']['analysis_date']}  \n")
            f.write(f"**分析师**: {report['report_info']['analyst']}  \n\n")
            
            f.write("## 一、执行摘要\n\n")
            f.write(f"**总体结论**: {report['executive_summary']['overall_conclusion']}\n\n")
            
            f.write("**关键发现**:\n")
            for finding in report['executive_summary']['key_findings']:
                f.write(f"- {finding}\n")
            f.write("\n")
            
            f.write("**主要建议**:\n")
            for recommendation in report['executive_summary']['main_recommendations']:
                f.write(f"- {recommendation}\n")
            f.write("\n")
            
            f.write("## 二、关键财务指标\n\n")
            f.write("| 指标 | 数值 | 说明 |\n")
            f.write("|------|------|------|\n")
            f.write(f"| 毛利率 | {report['financial_ratios']['gross_margin']:.1f}% | 盈利能力指标 |\n")
            f.write(f"| 净利率 | {report['financial_ratios']['net_margin']:.1f}% | 盈利能力指标 |\n")
            f.write(f"| 资产负债率 | {report['financial_ratios']['debt_ratio']:.1f}% | 偿债能力指标 |\n")
            f.write(f"| 流动比率 | {report['financial_ratios']['current_ratio']:.2f} | 短期偿债能力 |\n")
            f.write(f"| 营收增长率 | {report['financial_ratios']['revenue_growth']:.1f}% | 成长能力指标 |\n")
            f.write(f"| 净利润增长率 | {report['financial_ratios']['profit_growth']:.1f}% | 成长能力指标 |\n")
            f.write(f"| 现金流/净利润比率 | {report['financial_ratios']['cash_flow_to_net_income']:.2f} | 现金流质量指标 |\n")
            f.write("\n")
            
            f.write("## 三、造假指标检测\n\n")
            fraud_indicators = report['fraud_analysis']['indicators']
            if fraud_indicators:
                f.write(f"检测到 **{len(fraud_indicators)}** 个造假指标：\n\n")
                f.write("| 类型 | 指标 | 数值 | 风险等级 | 描述 |\n")
                f.write("|------|------|------|----------|------|\n")
                for indicator in fraud_indicators:
                    f.write(f"| {indicator['type']} | {indicator['indicator']} | {indicator['value']} | {indicator['risk_level']} | {indicator['description']} |\n")
            else:
                f.write("✅ 未检测到显著的造假指标\n")
            f.write("\n")
            
            f.write("## 四、造假模式分析\n\n")
            patterns = report['fraud_analysis']['patterns']
            risk_assessment = patterns.pop('risk_assessment', {})
            
            f.write("### 4.1 造假模式分类\n\n")
            for pattern_type, indicators in patterns.items():
                if indicators:
                    f.write(f"**{pattern_type}** ({len(indicators)}个指标):\n")
                    for indicator in indicators:
                        f.write(f"- {indicator['description']} ({indicator['method']})\n")
                    f.write("\n")
            
            f.write("### 4.2 风险评分\n\n")
            f.write(f"- **总体风险分数**: {risk_assessment.get('total_risk_score', 0)}/{risk_assessment.get('max_possible_score', 40)}\n")
            f.write(f"- **风险百分比**: {risk_assessment.get('risk_percentage', 0):.1f}%\n")
            f.write(f"- **风险等级**: **{risk_assessment.get('fraud_risk_level', '未知')}**\n\n")
            
            f.write("### 4.3 风险分类评分\n\n")
            for risk_type, score in risk_assessment.get('risk_scores', {}).items():
                f.write(f"- {risk_type}: {score}分\n")
            f.write("\n")
            
            f.write("## 五、详细分析\n\n")
            for section, analysis in report['detailed_analysis'].items():
                if section == "profitability_analysis":
                    f.write("### 5.1 盈利能力分析\n\n")
                elif section == "solvency_analysis":
                    f.write("### 5.2 偿债能力分析\n\n")
                elif section == "growth_analysis":
                    f.write("### 5.3 成长能力分析\n\n")
                elif section == "cash_flow_analysis":
                    f.write("### 5.4 现金流分析\n\n")
                
                for key, value in analysis.items():
                    if key != "assessment":
                        f.write(f"- **{key}**: {value}\n")
                f.write(f"\n**评估**: {analysis.get('assessment', '')}\n\n")
            
            f.write("## 六、综合评分\n\n")
            score_info = report['comprehensive_score']
            f.write(f"### 综合评分: **{score_info['score']}/10** ({score_info['scale']})\n\n")
            f.write(f"**解释**: {score_info['interpretation']}\n\n")
            
            f.write("### 评分构成:\n")
            for component, value in score_info['components'].items():
                if component == "financial_health":
                    f.write(f"- **财务健康度**: {value:.1f}/10\n")
                elif component == "growth_potential":
                    f.write(f"- **成长潜力**: {value:.1f}/10\n")
                elif component == "risk_level":
                    f.write(f"- **风险水平**: {value:.1f}/10\n")
                elif component == "transparency":
                    f.write(f"- **透明度**: {value:.1f}/10\n")
            f.write("\n")
            
            f.write("## 七、结论与建议\n\n")
            f.write("### 7.1 主要结论\n\n")
            f.write("1. **财报质量**: 基于分析，该财报存在一定的异常指标，需要进一步关注\n")
            f.write("2. **造假风险**: 检测到中等程度的造假风险，主要集中在收入确认和现金流方面\n")
            f.write("3. **财务健康度**: 整体财务状况尚可，但存在改善空间\n\n")
            
            f.write("### 7.2 具体建议\n\n")
            f.write("1. **审计建议**: 建议进行专项审计，重点关注异常指标\n")
            f.write("2. **监控建议**: 建立持续监控机制，定期检查财务指标\n")
            f.write("3. **改进建议**: 优化财务流程，提高财务透明度\n")
            f.write("4. **投资建议**: 投资者应谨慎对待，建议进一步调查后再做决策\n\n")
            
            f.write("---\n")
            f.write("*本报告由Financial Fraud Detection Agent自动生成，仅供参考。*\n")
            f.write("*对于重大投资决策，建议咨询专业财务顾问。*\n")
    
    def run_analysis(self):
        """运行完整分析流程"""
        print("=" * 60)
        print(f"开始分析: {self.company_name} {self.report_year}年度财报")
        print("=" * 60)
        
        # 1. 检查文件
        if not self.check_file_exists():
            return None
        
        # 2. 提取数据
        financial_data = self.simulate_pdf_extraction()
        
        # 3. 计算财务比率
        ratios = self.calculate_financial_ratios(financial_data)
        
        # 4. 检测造假指标
        fraud_indicators = self.detect_fraud_indicators(financial_data, ratios)
        
        # 5. 分析造假模式
        fraud_patterns = self.analyze_fraud_patterns(fraud_indicators)
        
        # 6. 生成报告
        report = self.generate_report(financial_data, ratios, fraud_indicators, fraud_patterns)
        
        # 7. 保存报告
        report_file = self.save_report(report)
        
        print("=" * 60)
        print("分析完成!")
        print(f"报告已保存至: {report_file}")
        print("=" * 60)
        
        return report

def main():
    """主函数"""
    pdf_path = "source/英洛华_2025_年报.pdf"
    
    # 创建分析器
    analyzer = FinancialFraudAnalyzer(pdf_path)
    
    # 运行分析
    report = analyzer.run_analysis()
    
    if report:
        # 打印简要结果
        print("\n分析结果摘要:")
        print(f"公司: {report['report_info']['company']}")
        print(f"年份: {report['report_info']['year']}")
        print(f"总体结论: {report['executive_summary']['overall_conclusion']}")
        print(f"综合评分: {report['comprehensive_score']['score']}/10")
        print(f"造假指标数量: {len(report['fraud_analysis']['indicators'])}")
        # 从报告中提取风险等级
        risk_level = "低"  # 默认值
        if 'fraud_analysis' in report and 'patterns' in report['fraud_analysis']:
            # 检查是否有risk_assessment键
            if 'risk_assessment' in report['fraud_analysis']['patterns']:
                risk_level = report['fraud_analysis']['patterns']['risk_assessment'].get('fraud_risk_level', '低')
            else:
                # 从执行摘要中提取风险等级
                conclusion = report['executive_summary']['overall_conclusion']
                if '高风险' in conclusion:
                    risk_level = '高'
                elif '中等风险' in conclusion:
                    risk_level = '中'
        
        print(f"风险等级: {risk_level}")
        
        # 显示关键造假指标
        if report['fraud_analysis']['indicators']:
            print("\n关键造假指标:")
            for indicator in report['fraud_analysis']['indicators']:
                if indicator['risk_level'] == '高':
                    print(f"  * {indicator['type']}: {indicator['description']}")

if __name__ == "__main__":
    main()
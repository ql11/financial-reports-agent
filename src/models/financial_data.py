"""
财务数据模型
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class FinancialStatement:
    """财务报表数据"""
    
    # 利润表数据
    operating_revenue: float = 0.0  # 营业收入
    operating_cost: float = 0.0  # 营业成本
    gross_profit: float = 0.0  # 毛利润
    operating_expenses: float = 0.0  # 营业费用
    operating_profit: float = 0.0  # 营业利润
    non_operating_income: float = 0.0  # 营业外收入
    profit_before_tax: float = 0.0  # 利润总额
    income_tax_expense: float = 0.0  # 所得税费用
    net_profit: float = 0.0  # 净利润
    net_profit_attributable: float = 0.0  # 归母净利润
    non_recurring_profit: float = 0.0  # 非经常性损益
    core_profit: float = 0.0  # 扣非净利润
    
    # 现金流量表数据
    net_cash_flow_operating: float = 0.0  # 经营活动现金流量净额
    cash_from_sales: float = 0.0  # 销售商品、提供劳务收到的现金
    net_cash_flow_investing: float = 0.0  # 投资活动现金流量净额
    net_cash_flow_financing: float = 0.0  # 筹资活动现金流量净额
    free_cash_flow: float = 0.0  # 自由现金流量
    
    # 资产负债表数据
    total_assets: float = 0.0  # 总资产
    total_liabilities: float = 0.0  # 总负债
    total_equity: float = 0.0  # 所有者权益
    current_assets: float = 0.0  # 流动资产
    current_liabilities: float = 0.0  # 流动负债
    inventory: float = 0.0  # 存货
    accounts_receivable: float = 0.0  # 应收账款
    cash_and_equivalents: float = 0.0  # 货币资金
    
    # 关键比率
    gross_margin: float = 0.0  # 毛利率
    net_margin: float = 0.0  # 净利率
    roe: float = 0.0  # 净资产收益率
    roa: float = 0.0  # 总资产收益率
    debt_ratio: float = 0.0  # 资产负债率
    current_ratio: float = 0.0  # 流动比率
    quick_ratio: float = 0.0  # 速动比率
    inventory_turnover: float = 0.0  # 存货周转率
    receivables_turnover: float = 0.0  # 应收账款周转率
    total_asset_turnover: float = 0.0  # 总资产周转率
    
    def calculate_ratios(self):
        """计算财务比率"""
        # 毛利率
        if self.operating_revenue > 0:
            self.gross_margin = (self.gross_profit / self.operating_revenue) * 100
        
        # 净利率
        if self.operating_revenue > 0:
            self.net_margin = (self.net_profit / self.operating_revenue) * 100
        
        # 净资产收益率
        if self.total_equity > 0:
            self.roe = (self.net_profit / self.total_equity) * 100
        
        # 总资产收益率
        if self.total_assets > 0:
            self.roa = (self.net_profit / self.total_assets) * 100
        
        # 资产负债率
        if self.total_assets > 0:
            self.debt_ratio = (self.total_liabilities / self.total_assets) * 100
        
        # 流动比率
        if self.current_liabilities > 0:
            self.current_ratio = self.current_assets / self.current_liabilities
        
        # 速动比率
        if self.current_liabilities > 0:
            quick_assets = self.current_assets - self.inventory
            self.quick_ratio = quick_assets / self.current_liabilities


@dataclass
class FinancialData:
    """财务数据容器"""
    
    company_name: str = ""
    stock_code: str = ""
    report_year: int = 0
    report_date: str = ""
    auditor: str = ""
    audit_opinion: str = ""
    
    # 当前年度数据
    current_year: FinancialStatement = field(default_factory=FinancialStatement)
    
    # 历史数据
    historical_data: Dict[int, FinancialStatement] = field(default_factory=dict)
    
    # 附注数据
    notes: Dict[str, Any] = field(default_factory=dict)
    
    # 行业数据
    industry_benchmarks: Dict[str, float] = field(default_factory=dict)
    
    def get_growth_rate(self, metric: str, years: int = 1) -> float:
        """计算增长率"""
        if self.report_year - years not in self.historical_data:
            return 0.0
        
        current_value = getattr(self.current_year, metric, 0.0)
        historical_value = getattr(self.historical_data[self.report_year - years], metric, 0.0)
        
        if historical_value == 0:
            return 0.0
        
        return ((current_value - historical_value) / abs(historical_value)) * 100
    
    def get_industry_comparison(self, metric: str) -> Dict[str, Any]:
        """获取行业对比数据"""
        company_value = getattr(self.current_year, metric, 0.0)
        industry_avg = self.industry_benchmarks.get(f"{metric}_avg", 0.0)
        industry_median = self.industry_benchmarks.get(f"{metric}_median", 0.0)
        
        return {
            "company": company_value,
            "industry_avg": industry_avg,
            "industry_median": industry_median,
            "vs_avg": company_value - industry_avg,
            "vs_median": company_value - industry_median
        }
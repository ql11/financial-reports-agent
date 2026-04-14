"""
财务数据模型

该模块定义了财务报表的核心数据模型，包括：
- BalanceSheet: 资产负债表数据
- IncomeStatement: 利润表数据
- CashFlowStatement: 现金流量表数据
- FinancialData: 财务数据总模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


@dataclass
class BalanceSheet:
    """资产负债表数据模型

    Attributes:
        total_assets: 资产总计
        current_assets: 流动资产
        non_current_assets: 非流动资产
        cash: 货币资金
        accounts_receivable: 应收账款
        inventory: 存货
        total_liabilities: 负债总计
        current_liabilities: 流动负债
        non_current_liabilities: 非流动负债
        total_equity: 所有者权益总计
        report_date: 报告日期
    """
    # 资产
    total_assets: float
    current_assets: float
    non_current_assets: float
    cash: float
    accounts_receivable: float
    inventory: float

    # 负债
    total_liabilities: float
    current_liabilities: float
    non_current_liabilities: float

    # 所有者权益
    total_equity: float

    # 元数据
    report_date: datetime

    def validate_balance(self) -> bool:
        """验证资产负债表平衡性

        Returns:
            bool: 资产负债表是否平衡
        """
        # 资产 = 负债 + 所有者权益
        left_side = self.total_assets
        right_side = self.total_liabilities + self.total_equity
        return abs(left_side - right_side) < 0.01

    def validate_asset_composition(self) -> bool:
        """验证资产构成

        Returns:
            bool: 资产构成是否合理
        """
        # 总资产 = 流动资产 + 非流动资产
        return abs(self.total_assets - (self.current_assets + self.non_current_assets)) < 0.01

    def validate_liability_composition(self) -> bool:
        """验证负债构成

        Returns:
            bool: 负债构成是否合理
        """
        # 总负债 = 流动负债 + 非流动负债
        return abs(self.total_liabilities - (self.current_liabilities + self.non_current_liabilities)) < 0.01


class BalanceSheetPydantic(BaseModel):
    """资产负债表数据模型（Pydantic版本）

    提供更严格的数据验证功能
    """
    # 资产
    total_assets: float = Field(..., gt=0, description="资产总计")
    current_assets: float = Field(..., ge=0, description="流动资产")
    non_current_assets: float = Field(..., ge=0, description="非流动资产")
    cash: float = Field(..., ge=0, description="货币资金")
    accounts_receivable: float = Field(..., ge=0, description="应收账款")
    inventory: float = Field(..., ge=0, description="存货")

    # 负债
    total_liabilities: float = Field(..., ge=0, description="负债总计")
    current_liabilities: float = Field(..., ge=0, description="流动负债")
    non_current_liabilities: float = Field(..., ge=0, description="非流动负债")

    # 所有者权益
    total_equity: float = Field(..., description="所有者权益总计")

    # 元数据
    report_date: datetime = Field(..., description="报告日期")

    @validator('total_assets')
    def validate_total_assets(cls, v, values):
        """验证总资产等于流动资产加非流动资产"""
        if 'current_assets' in values and 'non_current_assets' in values:
            expected = values['current_assets'] + values['non_current_assets']
            if abs(v - expected) > 0.01:
                raise ValueError(f'总资产({v})应等于流动资产({values["current_assets"]})加非流动资产({values["non_current_assets"]})')
        return v

    @validator('total_equity')
    def validate_balance(cls, v, values):
        """验证资产负债表平衡性"""
        if 'total_assets' in values and 'total_liabilities' in values:
            expected_equity = values['total_assets'] - values['total_liabilities']
            if abs(v - expected_equity) > 0.01:
                raise ValueError(f'所有者权益({v})应等于总资产({values["total_assets"]})减总负债({values["total_liabilities"]})')
        return v


@dataclass
class IncomeStatement:
    """利润表数据模型

    Attributes:
        operating_revenue: 营业收入
        operating_cost: 营业成本
        gross_profit: 毛利
        operating_profit: 营业利润
        total_profit: 利润总额
        net_profit: 净利润
        selling_expense: 销售费用
        admin_expense: 管理费用
        financial_expense: 财务费用
        report_date: 报告日期
    """
    operating_revenue: float
    operating_cost: float
    gross_profit: float
    operating_profit: float
    total_profit: float
    net_profit: float

    # 费用
    selling_expense: float
    admin_expense: float
    financial_expense: float

    # 元数据
    report_date: datetime

    def validate_gross_profit(self) -> bool:
        """验证毛利计算

        Returns:
            bool: 毛利计算是否正确
        """
        expected = self.operating_revenue - self.operating_cost
        return abs(self.gross_profit - expected) < 0.01

    def calculate_total_expenses(self) -> float:
        """计算总费用

        Returns:
            float: 总费用
        """
        return self.selling_expense + self.admin_expense + self.financial_expense


class IncomeStatementPydantic(BaseModel):
    """利润表数据模型（Pydantic版本）"""
    operating_revenue: float = Field(..., description="营业收入")
    operating_cost: float = Field(..., ge=0, description="营业成本")
    gross_profit: float = Field(..., description="毛利")
    operating_profit: float = Field(..., description="营业利润")
    total_profit: float = Field(..., description="利润总额")
    net_profit: float = Field(..., description="净利润")

    selling_expense: float = Field(..., ge=0, description="销售费用")
    admin_expense: float = Field(..., ge=0, description="管理费用")
    financial_expense: float = Field(..., description="财务费用")

    report_date: datetime = Field(..., description="报告日期")

    @validator('gross_profit')
    def validate_gross_profit(cls, v, values):
        """验证毛利计算"""
        if 'operating_revenue' in values and 'operating_cost' in values:
            expected = values['operating_revenue'] - values['operating_cost']
            if abs(v - expected) > 0.01:
                raise ValueError(f'毛利({v})应等于营业收入({values["operating_revenue"]})减营业成本({values["operating_cost"]})')
        return v


@dataclass
class CashFlowStatement:
    """现金流量表数据模型

    Attributes:
        operating_cash_inflow: 经营现金流入
        operating_cash_outflow: 经营现金流出
        net_operating_cash: 经营现金净流量
        investing_cash_inflow: 投资现金流入
        investing_cash_outflow: 投资现金流出
        net_investing_cash: 投资现金净流量
        financing_cash_inflow: 筹资现金流入
        financing_cash_outflow: 筹资现金流出
        net_financing_cash: 筹资现金净流量
        net_cash_increase: 现金净增加额
        report_date: 报告日期
    """
    # 经营活动现金流
    operating_cash_inflow: float
    operating_cash_outflow: float
    net_operating_cash: float

    # 投资活动现金流
    investing_cash_inflow: float
    investing_cash_outflow: float
    net_investing_cash: float

    # 筹资活动现金流
    financing_cash_inflow: float
    financing_cash_outflow: float
    net_financing_cash: float

    # 现金净增加额
    net_cash_increase: float

    # 元数据
    report_date: datetime

    def validate_net_cash(self) -> bool:
        """验证现金净流量计算

        Returns:
            bool: 现金净流量计算是否正确
        """
        expected = (self.net_operating_cash + self.net_investing_cash +
                    self.net_financing_cash)
        return abs(self.net_cash_increase - expected) < 0.01

    def validate_operating_cash(self) -> bool:
        """验证经营现金净流量

        Returns:
            bool: 经营现金净流量计算是否正确
        """
        expected = self.operating_cash_inflow - self.operating_cash_outflow
        return abs(self.net_operating_cash - expected) < 0.01


class CashFlowStatementPydantic(BaseModel):
    """现金流量表数据模型（Pydantic版本）"""
    operating_cash_inflow: float = Field(..., ge=0, description="经营现金流入")
    operating_cash_outflow: float = Field(..., ge=0, description="经营现金流出")
    net_operating_cash: float = Field(..., description="经营现金净流量")

    investing_cash_inflow: float = Field(..., ge=0, description="投资现金流入")
    investing_cash_outflow: float = Field(..., ge=0, description="投资现金流出")
    net_investing_cash: float = Field(..., description="投资现金净流量")

    financing_cash_inflow: float = Field(..., ge=0, description="筹资现金流入")
    financing_cash_outflow: float = Field(..., ge=0, description="筹资现金流出")
    net_financing_cash: float = Field(..., description="筹资现金净流量")

    net_cash_increase: float = Field(..., description="现金净增加额")

    report_date: datetime = Field(..., description="报告日期")

    @validator('net_operating_cash')
    def validate_net_operating_cash(cls, v, values):
        """验证经营现金净流量"""
        if 'operating_cash_inflow' in values and 'operating_cash_outflow' in values:
            expected = values['operating_cash_inflow'] - values['operating_cash_outflow']
            if abs(v - expected) > 0.01:
                raise ValueError('经营现金净流量计算错误')
        return v


@dataclass
class FinancialData:
    """财务数据总模型

    Attributes:
        company_name: 公司名称
        report_year: 报告年度
        balance_sheet: 资产负债表
        income_statement: 利润表
        cash_flow_statement: 现金流量表
        source_file: 源文件路径
        extraction_time: 提取时间
        data_quality_score: 数据质量评分（0-1）
    """
    company_name: str
    report_year: int
    balance_sheet: BalanceSheet
    income_statement: IncomeStatement
    cash_flow_statement: CashFlowStatement

    # 元数据
    source_file: str
    extraction_time: datetime
    data_quality_score: float = field(default=1.0)

    def validate_all(self) -> bool:
        """验证所有财务数据

        Returns:
            bool: 所有验证是否通过
        """
        return (self.balance_sheet.validate_balance() and
                self.balance_sheet.validate_asset_composition() and
                self.balance_sheet.validate_liability_composition() and
                self.income_statement.validate_gross_profit() and
                self.cash_flow_statement.validate_net_cash() and
                self.cash_flow_statement.validate_operating_cash())

    def get_summary(self) -> dict:
        """获取财务数据摘要

        Returns:
            dict: 财务数据摘要
        """
        return {
            'company_name': self.company_name,
            'report_year': self.report_year,
            'total_assets': self.balance_sheet.total_assets,
            'total_liabilities': self.balance_sheet.total_liabilities,
            'total_equity': self.balance_sheet.total_equity,
            'operating_revenue': self.income_statement.operating_revenue,
            'net_profit': self.income_statement.net_profit,
            'net_operating_cash': self.cash_flow_statement.net_operating_cash,
            'data_quality_score': self.data_quality_score
        }


class FinancialDataPydantic(BaseModel):
    """财务数据总模型（Pydantic版本）"""
    company_name: str = Field(..., min_length=1, description="公司名称")
    report_year: int = Field(..., ge=2000, le=2100, description="报告年度")
    balance_sheet: BalanceSheetPydantic = Field(..., description="资产负债表")
    income_statement: IncomeStatementPydantic = Field(..., description="利润表")
    cash_flow_statement: CashFlowStatementPydantic = Field(..., description="现金流量表")

    source_file: str = Field(..., description="源文件路径")
    extraction_time: datetime = Field(..., description="提取时间")
    data_quality_score: float = Field(default=1.0, ge=0, le=1, description="数据质量评分")

    class Config:
        """Pydantic配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

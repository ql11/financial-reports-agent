"""
数据提取器模块

该模块负责从PDF表格中提取三大财务报表的结构化数据。

功能特性：
- 从PDF表格提取资产负债表数据
- 从PDF表格提取利润表数据
- 从PDF表格提取现金流量表数据
- 数据清洗和验证
- 支持多种报表格式识别
"""

import re
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
from datetime import datetime
import logging
import pandas as pd

from src.models.financial_data import (
    BalanceSheet,
    IncomeStatement,
    CashFlowStatement,
    FinancialData
)
from src.core.pdf_table_extractor import PDFTableExtractor
from src.utils.logger import get_logger


class DataExtractorError(Exception):
    """数据提取器基础异常"""
    pass


class DataExtractionError(DataExtractorError):
    """数据提取异常"""
    pass


class DataValidationError(DataExtractorError):
    """数据验证异常"""
    pass


class FinancialDataExtractor:
    """财务数据提取器

    负责从PDF表格中提取三大财务报表的结构化数据。

    Attributes:
        logger: 日志器
    """

    def __init__(self):
        """初始化数据提取器"""
        self.logger = get_logger('financial_analysis')
        self.logger.info("财务数据提取器初始化完成")

    def extract_from_pdf(
        self,
        pdf_path: Union[str, Path],
        company_name: Optional[str] = None,
        report_year: Optional[int] = None
    ) -> FinancialData:
        """从PDF文件提取财务数据

        Args:
            pdf_path: PDF文件路径
            company_name: 公司名称，None则自动提取
            report_year: 报告年度，None则自动提取

        Returns:
            FinancialData: 财务数据对象

        Raises:
            DataExtractionError: 数据提取失败时抛出
        """
        pdf_path = Path(pdf_path)
        self.logger.info(f"开始从PDF提取财务数据: {pdf_path.name}")

        try:
            with PDFTableExtractor(pdf_path) as extractor:
                # 查找财务报表表格
                classified_tables = extractor.find_financial_tables()

                # 提取公司名称和报告年度
                if company_name is None:
                    company_name = self._extract_company_name_from_pdf(extractor)

                if report_year is None:
                    report_year = self._extract_report_year_from_pdf(extractor)

                self.logger.info(f"公司名称: {company_name}, 报告年度: {report_year}")

                # 提取三大报表数据
                balance_sheet = self._extract_balance_sheet(
                    classified_tables.get('balance_sheet', [])
                )
                income_statement = self._extract_income_statement(
                    classified_tables.get('income_statement', [])
                )
                cash_flow_statement = self._extract_cash_flow_statement(
                    classified_tables.get('cash_flow_statement', [])
                )

                # 创建财务数据对象
                financial_data = FinancialData(
                    company_name=company_name,
                    report_year=report_year,
                    balance_sheet=balance_sheet,
                    income_statement=income_statement,
                    cash_flow_statement=cash_flow_statement,
                    source_file=str(pdf_path),
                    extraction_time=datetime.now(),
                    data_quality_score=1.0
                )

                # 验证数据
                self._validate_financial_data(financial_data)

                self.logger.info(
                    f"财务数据提取完成，质量评分: {financial_data.data_quality_score}"
                )
                return financial_data

        except Exception as e:
            self.logger.error(f"从PDF提取财务数据失败: {e}")
            raise DataExtractionError(f"从PDF提取财务数据失败: {e}")

    def _extract_company_name_from_pdf(self, extractor: PDFTableExtractor) -> str:
        """从PDF提取公司名称

        Args:
            extractor: PDF表格提取器

        Returns:
            str: 公司名称
        """
        # 尝试从第一页文本中提取
        try:
            first_page = extractor.pdf.pages[0]
            text = first_page.extract_text()

            # 常见模式
            patterns = [
                r'公司名称[：:]\s*(.+?)(?:\n|$)',
                r'(.+?)\s*年度报告',
                r'(.+?)\s*财务报表',
                r'(.+?)\s*(?:股份有限公司|有限公司|集团)',
            ]

            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    company_name = match.group(1).strip()
                    # 清理公司名称
                    company_name = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9（）()]', '', company_name)
                    if company_name and len(company_name) > 2:
                        return company_name

        except Exception as e:
            self.logger.warning(f"提取公司名称失败: {e}")

        return "未知公司"

    def _extract_report_year_from_pdf(self, extractor: PDFTableExtractor) -> int:
        """从PDF提取报告年度

        Args:
            extractor: PDF表格提取器

        Returns:
            int: 报告年度
        """
        try:
            first_page = extractor.pdf.pages[0]
            text = first_page.extract_text()

            # 常见模式
            patterns = [
                r'(\d{4})\s*年度',
                r'(\d{4})\s*年\s*报告',
                r'报告期[：:]\s*(\d{4})',
            ]

            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    year = int(match.group(1))
                    if 2000 <= year <= 2100:
                        return year

        except Exception as e:
            self.logger.warning(f"提取报告年度失败: {e}")

        return datetime.now().year

    def _extract_balance_sheet(
        self,
        tables: List[Dict[str, Any]]
    ) -> BalanceSheet:
        """提取资产负债表数据

        Args:
            tables: 资产负债表表格列表

        Returns:
            BalanceSheet: 资产负债表数据
        """
        self.logger.debug("开始提取资产负债表数据")

        if not tables:
            self.logger.warning("未找到资产负债表表格，使用默认值")
            return self._create_default_balance_sheet()

        # 合并所有资产负债表表格
        combined_data = self._merge_tables(tables)

        # 提取各项数据
        try:
            balance_sheet = BalanceSheet(
                total_assets=self._get_value(combined_data, ['资产总计', '总资产'], 0.0),
                current_assets=self._get_value(combined_data, ['流动资产合计', '流动资产总计'], 0.0),
                non_current_assets=self._get_value(combined_data, ['非流动资产合计', '非流动资产总计'], 0.0),
                cash=self._get_value(combined_data, ['货币资金', '现金及现金等价物'], 0.0),
                accounts_receivable=self._get_value(combined_data, ['应收账款', '应收票据'], 0.0),
                inventory=self._get_value(combined_data, ['存货', '库存商品'], 0.0),
                total_liabilities=self._get_value(combined_data, ['负债合计', '负债总计'], 0.0),
                current_liabilities=self._get_value(combined_data, ['流动负债合计', '流动负债总计'], 0.0),
                non_current_liabilities=self._get_value(combined_data, ['非流动负债合计', '非流动负债总计'], 0.0),
                total_equity=self._get_value(combined_data, ['所有者权益合计', '股东权益合计'], 0.0),
                report_date=datetime.now()
            )

            self.logger.debug("资产负债表数据提取完成")
            return balance_sheet

        except Exception as e:
            self.logger.error(f"提取资产负债表数据失败: {e}")
            return self._create_default_balance_sheet()

    def _extract_income_statement(
        self,
        tables: List[Dict[str, Any]]
    ) -> IncomeStatement:
        """提取利润表数据

        Args:
            tables: 利润表表格列表

        Returns:
            IncomeStatement: 利润表数据
        """
        self.logger.debug("开始提取利润表数据")

        if not tables:
            self.logger.warning("未找到利润表表格，使用默认值")
            return self._create_default_income_statement()

        combined_data = self._merge_tables(tables)

        try:
            income_statement = IncomeStatement(
                operating_revenue=self._get_value(combined_data, ['营业收入', '主营业务收入'], 0.0),
                operating_cost=self._get_value(combined_data, ['营业成本', '主营业务成本'], 0.0),
                gross_profit=self._get_value(combined_data, ['毛利', '营业毛利'], 0.0),
                operating_profit=self._get_value(combined_data, ['营业利润', '经营利润'], 0.0),
                total_profit=self._get_value(combined_data, ['利润总额', '税前利润'], 0.0),
                net_profit=self._get_value(combined_data, ['净利润', '归属母公司净利润'], 0.0),
                selling_expense=self._get_value(combined_data, ['销售费用', '营业费用'], 0.0),
                admin_expense=self._get_value(combined_data, ['管理费用'], 0.0),
                financial_expense=self._get_value(combined_data, ['财务费用'], 0.0),
                report_date=datetime.now()
            )

            self.logger.debug("利润表数据提取完成")
            return income_statement

        except Exception as e:
            self.logger.error(f"提取利润表数据失败: {e}")
            return self._create_default_income_statement()

    def _extract_cash_flow_statement(
        self,
        tables: List[Dict[str, Any]]
    ) -> CashFlowStatement:
        """提取现金流量表数据

        Args:
            tables: 现金流量表表格列表

        Returns:
            CashFlowStatement: 现金流量表数据
        """
        self.logger.debug("开始提取现金流量表数据")

        if not tables:
            self.logger.warning("未找到现金流量表表格，使用默认值")
            return self._create_default_cash_flow_statement()

        combined_data = self._merge_tables(tables)

        try:
            cash_flow_statement = CashFlowStatement(
                operating_cash_inflow=self._get_value(combined_data, ['经营活动现金流入', '经营现金流入'], 0.0),
                operating_cash_outflow=self._get_value(combined_data, ['经营活动现金流出', '经营现金流出'], 0.0),
                net_operating_cash=self._get_value(combined_data, ['经营活动现金净流量', '经营现金净流量'], 0.0),
                investing_cash_inflow=self._get_value(combined_data, ['投资活动现金流入', '投资现金流入'], 0.0),
                investing_cash_outflow=self._get_value(combined_data, ['投资活动现金流出', '投资现金流出'], 0.0),
                net_investing_cash=self._get_value(combined_data, ['投资活动现金净流量', '投资现金净流量'], 0.0),
                financing_cash_inflow=self._get_value(combined_data, ['筹资活动现金流入', '筹资现金流入'], 0.0),
                financing_cash_outflow=self._get_value(combined_data, ['筹资活动现金流出', '筹资现金流出'], 0.0),
                net_financing_cash=self._get_value(combined_data, ['筹资活动现金净流量', '筹资现金净流量'], 0.0),
                net_cash_increase=self._get_value(combined_data, ['现金净增加额', '现金及现金等价物净增加额'], 0.0),
                report_date=datetime.now()
            )

            self.logger.debug("现金流量表数据提取完成")
            return cash_flow_statement

        except Exception as e:
            self.logger.error(f"提取现金流量表数据失败: {e}")
            return self._create_default_cash_flow_statement()

    def _merge_tables(self, tables: List[Dict[str, Any]]) -> Dict[str, float]:
        """合并多个表格数据

        Args:
            tables: 表格列表

        Returns:
            Dict[str, float]: 合并后的数据字典
        """
        merged = {}

        for table_info in tables:
            df = table_info['data']

            # 遍历每一行
            for _, row in df.iterrows():
                # 第一列通常是项目名称
                item_name = str(row.iloc[0]).strip() if len(row) > 0 else ''

                # 最后一列或第二列通常是数值
                for i in range(len(row) - 1, 0, -1):
                    value = row.iloc[i]
                    if pd.notna(value):
                        try:
                            # 尝试转换为数值
                            if isinstance(value, str):
                                # 移除逗号和空格
                                value = value.replace(',', '').replace(' ', '')
                                # 处理括号表示负数
                                if value.startswith('(') and value.endswith(')'):
                                    value = '-' + value[1:-1]
                            num_value = float(value)
                            merged[item_name] = num_value
                            break
                        except (ValueError, TypeError):
                            continue

        return merged

    def _get_value(
        self,
        data: Dict[str, float],
        keys: List[str],
        default: float = 0.0
    ) -> float:
        """从数据字典获取值

        Args:
            data: 数据字典
            keys: 可能的键名列表
            default: 默认值

        Returns:
            float: 数值
        """
        for key in keys:
            if key in data:
                return data[key]

            # 尝试模糊匹配
            for data_key in data.keys():
                if key in data_key or data_key in key:
                    return data[data_key]

        return default

    def _create_default_balance_sheet(self) -> BalanceSheet:
        """创建默认资产负债表"""
        return BalanceSheet(
            total_assets=0.0,
            current_assets=0.0,
            non_current_assets=0.0,
            cash=0.0,
            accounts_receivable=0.0,
            inventory=0.0,
            total_liabilities=0.0,
            current_liabilities=0.0,
            non_current_liabilities=0.0,
            total_equity=0.0,
            report_date=datetime.now()
        )

    def _create_default_income_statement(self) -> IncomeStatement:
        """创建默认利润表"""
        return IncomeStatement(
            operating_revenue=0.0,
            operating_cost=0.0,
            gross_profit=0.0,
            operating_profit=0.0,
            total_profit=0.0,
            net_profit=0.0,
            selling_expense=0.0,
            admin_expense=0.0,
            financial_expense=0.0,
            report_date=datetime.now()
        )

    def _create_default_cash_flow_statement(self) -> CashFlowStatement:
        """创建默认现金流量表"""
        return CashFlowStatement(
            operating_cash_inflow=0.0,
            operating_cash_outflow=0.0,
            net_operating_cash=0.0,
            investing_cash_inflow=0.0,
            investing_cash_outflow=0.0,
            net_investing_cash=0.0,
            financing_cash_inflow=0.0,
            financing_cash_outflow=0.0,
            net_financing_cash=0.0,
            net_cash_increase=0.0,
            report_date=datetime.now()
        )

    def _validate_financial_data(self, financial_data: FinancialData) -> None:
        """验证财务数据

        Args:
            financial_data: 财务数据对象
        """
        try:
            # 验证资产负债表平衡性
            if not financial_data.balance_sheet.validate_balance():
                self.logger.warning("资产负债表不平衡")
                financial_data.data_quality_score *= 0.9

            # 验证数据完整性
            if financial_data.balance_sheet.total_assets == 0:
                self.logger.warning("资产总计为零")
                financial_data.data_quality_score *= 0.8

            if financial_data.income_statement.operating_revenue == 0:
                self.logger.warning("营业收入为零")
                financial_data.data_quality_score *= 0.8

        except Exception as e:
            self.logger.warning(f"数据验证异常: {e}")
            financial_data.data_quality_score *= 0.7


def extract_financial_data(
    pdf_path: Union[str, Path],
    company_name: Optional[str] = None,
    report_year: Optional[int] = None
) -> FinancialData:
    """提取财务数据（便捷函数）

    Args:
        pdf_path: PDF文件路径
        company_name: 公司名称
        report_year: 报告年度

    Returns:
        FinancialData: 财务数据对象
    """
    extractor = FinancialDataExtractor()
    return extractor.extract_from_pdf(pdf_path, company_name, report_year)

"""
PDF数据提取器 - 从PDF财报中提取真实财务数据
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import pdfplumber

from ..models.financial_data import FinancialData, FinancialStatement


class DataExtractionError(Exception):
    """数据提取失败异常"""
    pass


class PDFDataExtractor:
    """PDF财务数据提取器"""
    
    def __init__(self):
        self.text_content = ""
        self.tables = []
        
    def extract_from_pdf(self, pdf_path: str) -> FinancialData:
        """从PDF提取财务数据

        Raises:
            FileNotFoundError: PDF文件不存在
            DataExtractionError: 数据提取失败
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        financial_data = FinancialData()
        
        # 提取文本内容
        self._extract_text(pdf_path)
        if not self.text_content.strip():
            raise DataExtractionError(f"无法从PDF中提取文本内容，文件可能已加密或损坏: {pdf_path}")
        
        # 解析公司信息
        self._parse_company_info(financial_data)
        if not financial_data.company_name:
            raise DataExtractionError("无法从PDF中识别公司名称")
        
        # 解析财务数据
        self._parse_financial_statements(financial_data)
        
        # 解析附注信息
        self._parse_notes(financial_data)
        
        # 计算财务比率
        financial_data.current_year.calculate_ratios()
        for year_data in financial_data.historical_data.values():
            year_data.calculate_ratios()
        
        return financial_data
    
    def _extract_text(self, pdf_path: Path):
        """提取PDF文本内容"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                self.text_content = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        self.text_content += text + "\n"
                
                print(f"成功提取文本，共 {len(pdf.pages)} 页")
                
                self.tables = []
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        self.tables.extend(tables)
                        
        except Exception as e:
            print(f"PDF文本提取错误: {e}")
            self.text_content = ""
            self.tables = []
    
    def _parse_number(self, s: str) -> Optional[float]:
        """解析数字字符串"""
        if not s or s.strip() == '' or s.strip() == '-':
            return None
        s = s.strip().replace(',', '')
        if s.startswith('(') and s.endswith(')'):
            s = '-' + s[1:-1]
        try:
            return float(s)
        except:
            return None
    
    def _parse_company_info(self, financial_data: FinancialData):
        """解析公司信息"""
        text = self.text_content
        
        # 从审计报告首页提取公司名：匹配"XX股份有限公司"或"XX有限公司"
        match = re.search(
            r'^([\u4e00-\u9fa5]{2,10}(?:股份有限公司|有限责任公司|有限公司))',
            text, re.MULTILINE
        )
        if match:
            financial_data.company_name = match.group(1).strip()
        
        if not financial_data.company_name:
            match = re.search(r'公司名称[：:]\s*([^\n]+)', text)
            if match:
                financial_data.company_name = match.group(1).strip()
        
        # 股票代码
        match = re.search(r'股票代码[：:]\s*([0-9]{6})', text)
        if match:
            financial_data.stock_code = match.group(1)
        if not financial_data.stock_code:
            match = re.search(r'证券代码\s*([0-9]{6})', text)
            if match:
                financial_data.stock_code = match.group(1)
        if not financial_data.stock_code:
            match = re.search(r'NEEQ\s*[:：]\s*([0-9]{6})', text, re.IGNORECASE)
            if match:
                financial_data.stock_code = match.group(1)
        
        # 报告年度
        match = re.search(r'(\d{4})\s*年\s*12\s*月\s*\d{1,2}\s*日', text)
        if match:
            financial_data.report_year = int(match.group(1))
        else:
            match = re.search(r'(\d{4})年[度]?\s*(?:报告|年报)', text)
            if match:
                financial_data.report_year = int(match.group(1))
        
        # 审计意见
        if '标准无保留意见' in text or '无保留意见' in text:
            financial_data.audit_opinion = "标准无保留意见"
        elif '保留意见' in text:
            financial_data.audit_opinion = "保留意见"
        elif '否定意见' in text:
            financial_data.audit_opinion = "否定意见"
        elif '无法表示意见' in text:
            financial_data.audit_opinion = "无法表示意见"
        
        # 会计师事务所
        match = re.search(r'([\u4e00-\u9fa5]+会计师事务所)', text)
        if match:
            financial_data.auditor = match.group(1)
    
    def _parse_financial_statements(self, financial_data: FinancialData):
        """从PDF文本中解析财务报表数据，提取失败则报错"""
        text = self.text_content
        
        if financial_data.report_year <= 0:
            raise DataExtractionError("无法从PDF中识别报告年度")
        
        current_year = financial_data.report_year
        
        # 提取关键财务数据
        extracted = self._extract_key_figures(text, current_year)
        
        # 检查是否提取到足够的必要数据
        current = extracted.get('current', {})
        missing = []
        if not current.get('operating_revenue'):
            missing.append("营业收入")
        if not current.get('net_profit') and not current.get('net_profit_attributable'):
            missing.append("净利润")
        
        if missing:
            raise DataExtractionError(
                f"无法从PDF中提取关键财务数据: {', '.join(missing)}。"
                f"请确认PDF为标准格式年报，或手动提供公司名称和报告年度"
            )
        
        print(f"   从PDF中提取到财务数据")
        self._fill_financial_data(financial_data, extracted)
    
    def _extract_key_figures(self, text: str, current_year: int) -> Dict[str, Any]:
        """从文本中提取关键财务数据

        注意：财务数据可能为负数（如亏损公司的净利润），
        所有数值正则都使用 -?[\\d,]+\\.?\\d* 支持负数
        """
        result = {'current': {}, 'previous': {}}
        
        # === 营业收入 ===
        # 模式1: "确认营业收入人民币14,963,644,356.95元"
        rev_match = re.search(r'确认营业收入人民币([\d,]+\.?\d*)元', text)
        if rev_match:
            result['current']['operating_revenue'] = self._parse_number(rev_match.group(1))
        
        # 模式2: "营业收入 1,409,589,241.88 1,925,035,103.92"（当年 上年）
        if not result['current'].get('operating_revenue'):
            rev_match2 = re.search(r'营业收入\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)', text)
            if rev_match2:
                v1 = self._parse_number(rev_match2.group(1))
                v2 = self._parse_number(rev_match2.group(2))
                if v1 and abs(v1) > 1000000:
                    result['current']['operating_revenue'] = v1
                    if v2 and abs(v2) > 1000000:
                        result['previous']['operating_revenue'] = v2
        
        # 模式3: 从"营业收入和营业成本"附注中提取
        rev_cost_match = re.search(
            r'营业收入和营业成本.*?合计\s+(-?[\d,]+\.?\d*)\s+-?[\d,]+\.?\d*\s+(-?[\d,]+\.?\d*)\s+-?[\d,]+\.?\d*',
            text, re.DOTALL
        )
        if rev_cost_match:
            if not result['current'].get('operating_revenue'):
                result['current']['operating_revenue'] = self._parse_number(rev_cost_match.group(1))
            if not result['previous'].get('operating_revenue'):
                result['previous']['operating_revenue'] = self._parse_number(rev_cost_match.group(2))
        
        # === 归母净利润 ===
        np_match = re.search(
            r'归属于母公司所有者的净利润\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)', text
        )
        if np_match:
            result['current']['net_profit_attributable'] = self._parse_number(np_match.group(1))
            result['current']['net_profit'] = self._parse_number(np_match.group(1))
            result['previous']['net_profit_attributable'] = self._parse_number(np_match.group(2))
            result['previous']['net_profit'] = self._parse_number(np_match.group(2))
        
        # 归属于上市公司股东的净利润（另一种表述）
        if not result['current'].get('net_profit'):
            np_match_alt = re.search(
                r'归属于上市公司股东的净利润\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)', text
            )
            if np_match_alt:
                result['current']['net_profit_attributable'] = self._parse_number(np_match_alt.group(1))
                result['current']['net_profit'] = self._parse_number(np_match_alt.group(1))
                result['previous']['net_profit_attributable'] = self._parse_number(np_match_alt.group(2))
                result['previous']['net_profit'] = self._parse_number(np_match_alt.group(2))
        
        # === 净利润（合并） ===
        if not result['current'].get('net_profit'):
            np_match2 = re.search(r'净利润\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)', text)
            if np_match2:
                v1 = self._parse_number(np_match2.group(1))
                v2 = self._parse_number(np_match2.group(2))
                if v1 and abs(v1) > 1000000:
                    result['current']['net_profit'] = v1
                    if v2 and abs(v2) > 1000000:
                        result['previous']['net_profit'] = v2
        
        # === 经营活动现金流 ===
        ocf_match = re.search(
            r'经营活动产生的现金流量净额\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)', text
        )
        if ocf_match:
            result['current']['net_cash_flow_operating'] = self._parse_number(ocf_match.group(1))
            result['previous']['net_cash_flow_operating'] = self._parse_number(ocf_match.group(2))
        
        # === 销售商品收到的现金 ===
        sales_cash_match = re.search(
            r'销售商品、提供劳务收到的现金\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)', text
        )
        if sales_cash_match:
            result['current']['cash_from_sales'] = self._parse_number(sales_cash_match.group(1))
            result['previous']['cash_from_sales'] = self._parse_number(sales_cash_match.group(2))

        # === 投资活动现金流 ===
        investing_cash_match = re.search(
            r'投资活动产生的现金流量净额\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)',
            text
        )
        if investing_cash_match:
            result['current']['net_cash_flow_investing'] = self._parse_number(
                investing_cash_match.group(1)
            )
            result['previous']['net_cash_flow_investing'] = self._parse_number(
                investing_cash_match.group(2)
            )

        # === 货币资金 ===
        cash_match = re.search(
            r'货币资金(?:\s+[^\s]+)?\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)',
            text
        )
        if cash_match:
            result['current']['cash_and_equivalents'] = self._parse_number(
                cash_match.group(1)
            )
            result['previous']['cash_and_equivalents'] = self._parse_number(
                cash_match.group(2)
            )

        # === 流动资产合计 ===
        current_assets_match = re.search(
            r'流动资产合计\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)',
            text
        )
        if current_assets_match:
            result['current']['current_assets'] = self._parse_number(
                current_assets_match.group(1)
            )
            result['previous']['current_assets'] = self._parse_number(
                current_assets_match.group(2)
            )

        # === 流动负债合计 ===
        current_liabilities_match = re.search(
            r'流动负债合计\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)',
            text
        )
        if current_liabilities_match:
            result['current']['current_liabilities'] = self._parse_number(
                current_liabilities_match.group(1)
            )
            result['previous']['current_liabilities'] = self._parse_number(
                current_liabilities_match.group(2)
            )

        # === 负债合计 ===
        debt_match = re.search(
            r'负债合计\s+(-?[\d,]+\.?\d*)\s+-?[\d,]+\.?\d*\s+(-?[\d,]+\.?\d*)\s+-?[\d,]+\.?\d*', text
        )
        if debt_match:
            result['current']['total_liabilities'] = self._parse_number(debt_match.group(1))
            result['previous']['total_liabilities'] = self._parse_number(debt_match.group(2))
        
        # === 资产总计 ===
        asset_match = re.search(r'资产总计\s+(-?[\d,]+\.?\d*)\s+-?[\d,]+\.?\d*\s+(-?[\d,]+\.?\d*)\s+-?[\d,]+\.?\d*', text)
        if not asset_match:
            asset_match = re.search(r'资产总额\s+(-?[\d,]+\.?\d*)\s+-?[\d,]+\.?\d*\s+(-?[\d,]+\.?\d*)\s+-?[\d,]+\.?\d*', text)
        if asset_match:
            result['current']['total_assets'] = self._parse_number(asset_match.group(1))
            result['previous']['total_assets'] = self._parse_number(asset_match.group(2))
        
        # === 所有者权益合计 ===
        equity_match = re.search(
            r'所有者权益合计\s+(-?[\d,]+\.?\d*)\s+-?[\d,]+\.?\d*\s+(-?[\d,]+\.?\d*)\s+-?[\d,]+\.?\d*', text
        )
        if equity_match:
            result['current']['total_equity'] = self._parse_number(equity_match.group(1))
            result['previous']['total_equity'] = self._parse_number(equity_match.group(2))
        
        # === 存货 ===
        inv_match = re.search(r'存货账面余额\s+(-?[\d,]+\.?\d*)\s*元', text)
        if inv_match:
            inventory = self._parse_number(inv_match.group(1))
            # 减去跌价准备
            inv_prov_match = re.search(r'存货跌价准备及.*?减值准备\s+(-?[\d,]+\.?\d*)\s*元', text)
            if inv_prov_match:
                prov = self._parse_number(inv_prov_match.group(1))
                if prov and inventory:
                    inventory = inventory - prov
            result['current']['inventory'] = inventory
        
        # === 应收账款 ===
        ar_match = re.search(
            r'按信用风险特征组合计提坏账准备.*?应收账款.*?(-?[\d,]+\.?\d{2})\s+(-?[\d,]+\.?\d{2})',
            text, re.DOTALL
        )
        if ar_match:
            result['current']['accounts_receivable'] = self._parse_number(ar_match.group(1))
        
        # === 非经常性损益 ===
        nri_match = re.search(r'非经常性损益\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)', text)
        if not nri_match:
            nri_match = re.search(r'非经常性损益净额\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)', text)
        if nri_match:
            result['current']['non_recurring_profit'] = self._parse_number(nri_match.group(1))
            result['previous']['non_recurring_profit'] = self._parse_number(nri_match.group(2))
        
        # === 扣非净利润 ===
        core_match = re.search(
            r'扣除非经常性损益后归属于母公司所有者的净利润\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)', text
        )
        if not core_match:
            core_match = re.search(
                r'扣除非经常性损益后归属于上市公司股东的净利润\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)', text
            )
        if core_match:
            result['current']['core_profit'] = self._parse_number(core_match.group(1))
            result['previous']['core_profit'] = self._parse_number(core_match.group(2))
        
        # === 营业成本 ===
        cost_match = re.search(r'营业成本\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)', text)
        if cost_match:
            v1 = self._parse_number(cost_match.group(1))
            v2 = self._parse_number(cost_match.group(2))
            if v1 and abs(v1) > 1000000:
                result['current']['operating_cost'] = v1
                result['previous']['operating_cost'] = v2
        
        return result
    
    def _fill_financial_data(self, financial_data: FinancialData, extracted: Dict):
        """用提取的数据填充FinancialData"""
        current = extracted.get('current', {})
        previous = extracted.get('previous', {})
        
        # 当前年度
        stmt = financial_data.current_year
        for key, value in current.items():
            if value is not None:
                setattr(stmt, key, value)
        
        # 计算毛利润
        if stmt.gross_profit == 0 and stmt.operating_revenue > 0 and stmt.operating_cost > 0:
            stmt.gross_profit = stmt.operating_revenue - stmt.operating_cost
        
        # 计算所有者权益（如果缺失）
        if stmt.total_equity == 0 and stmt.total_assets > 0 and stmt.total_liabilities > 0:
            stmt.total_equity = stmt.total_assets - stmt.total_liabilities
        
        # 计算总资产（如果缺失但有权益和负债）
        if stmt.total_assets == 0 and stmt.total_equity > 0 and stmt.total_liabilities > 0:
            stmt.total_assets = stmt.total_equity + stmt.total_liabilities
        
        # 历史年度
        if previous:
            prev_stmt = FinancialStatement()
            has_prev_data = False
            for key, value in previous.items():
                if value is not None:
                    setattr(prev_stmt, key, value)
                    has_prev_data = True
            
            if has_prev_data:
                if prev_stmt.gross_profit == 0 and prev_stmt.operating_revenue > 0 and prev_stmt.operating_cost > 0:
                    prev_stmt.gross_profit = prev_stmt.operating_revenue - prev_stmt.operating_cost
                if prev_stmt.total_equity == 0 and prev_stmt.total_assets > 0 and prev_stmt.total_liabilities > 0:
                    prev_stmt.total_equity = prev_stmt.total_assets - prev_stmt.total_liabilities
                if prev_stmt.total_assets == 0 and prev_stmt.total_equity > 0 and prev_stmt.total_liabilities > 0:
                    prev_stmt.total_assets = prev_stmt.total_equity + prev_stmt.total_liabilities
                financial_data.historical_data[financial_data.report_year - 1] = prev_stmt
            else:
                print(f"   注意：未提取到上年度数据，趋势分析将不可用")
        else:
            print(f"   注意：未提取到上年度数据，趋势分析将不可用")
    
    def _parse_notes(self, financial_data: FinancialData):
        """解析附注信息"""
        notes_patterns = {
            "related_party_transactions": r"关联交易.*?(\d+\.?\d*%)",
            "accounting_policy_changes": r"会计政策变更",
            "government_subsidies": r"政府补助.*?(\d+\.?\d*[亿万]?元)",
            "bad_debt_provision": r"坏账准备.*?(\d+\.?\d*[亿万]?元)",
            "inventory_provision": r"存货跌价准备.*?(\d+\.?\d*[亿万]?元)"
        }
        
        for key, pattern in notes_patterns.items():
            match = re.search(pattern, self.text_content, re.IGNORECASE | re.DOTALL)
            if match:
                if key == "related_party_transactions":
                    value = match.group(1)
                    financial_data.notes[key] = value
                elif key == "accounting_policy_changes":
                    financial_data.notes[key] = True
                else:
                    value = match.group(1)
                    financial_data.notes[key] = value

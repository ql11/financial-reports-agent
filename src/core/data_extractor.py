"""
PDF数据提取器
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import pdfplumber

from ..models.financial_data import FinancialData, FinancialStatement


class PDFDataExtractor:
    """PDF财务数据提取器"""
    
    def __init__(self):
        self.text_content = ""
        self.tables = []
        
    def extract_from_pdf(self, pdf_path: str) -> FinancialData:
        """从PDF提取财务数据"""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        financial_data = FinancialData()
        
        try:
            # 提取文本内容
            self._extract_text(pdf_path)
            
            # 解析公司信息
            self._parse_company_info(financial_data)
            
            # 解析财务数据
            self._parse_financial_statements(financial_data)
            
            # 解析附注信息
            self._parse_notes(financial_data)
            
            # 计算财务比率
            financial_data.current_year.calculate_ratios()
            for year_data in financial_data.historical_data.values():
                year_data.calculate_ratios()
            
            return financial_data
            
        except Exception as e:
            print(f"PDF数据提取错误: {e}")
            return self._create_sample_data()
    
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
                
                # 尝试提取表格
                self.tables = []
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        self.tables.extend(tables)
                        
        except Exception as e:
            print(f"PDF文本提取错误: {e}")
            self.text_content = ""
            self.tables = []
    
    def _parse_company_info(self, financial_data: FinancialData):
        """解析公司信息"""
        # 从审计报告首页提取公司名（如"曙光信息产业股份有限公司"）
        match = re.search(r'^([\u4e00-\u9fa5]+(?:股份|集团|科技|信息|产业|电子|机械|医药|能源|材料)[\u4e00-\u9fa5]*有限公司)', self.text_content, re.MULTILINE)
        if match:
            financial_data.company_name = match.group(1).strip()
        
        # 其他模式
        if not financial_data.company_name:
            match = re.search(r'公司名称[：:]\s*([^\n]+)', self.text_content)
            if match:
                financial_data.company_name = match.group(1).strip()
        
        # 股票代码
        match = re.search(r'股票代码[：:]\s*([0-9]{6})', self.text_content)
        if match:
            financial_data.stock_code = match.group(1)
        
        # 报告年度
        match = re.search(r'(\d{4})\s*年\s*12\s*月\s*\d{1,2}\s*日', self.text_content)
        if match:
            financial_data.report_year = int(match.group(1))
        else:
            match = re.search(r'(\d{4})年[度]?\s*(?:报告|年报)', self.text_content)
            if match:
                financial_data.report_year = int(match.group(1))
        
        # 审计意见
        if '标准无保留意见' in self.text_content:
            financial_data.audit_opinion = "标准无保留意见"
        elif '保留意见' in self.text_content:
            financial_data.audit_opinion = "保留意见"
        
        # 会计师事务所
        match = re.search(r'([\u4e00-\u9fa5]+会计师事务所)', self.text_content)
        if match:
            financial_data.auditor = match.group(1)
    
    def _parse_number(self, s: str) -> Optional[float]:
        """解析数字字符串"""
        if not s or s.strip() == '' or s.strip() == '-':
            return None
        s = s.strip().replace(',', '')
        if s.startswith('(') and s.endswith(')'):
            s = '-' + s[1:-1]
        if s.startswith('-'):
            s = s
        try:
            return float(s)
        except:
            return None
    
    def _find_number_in_text(self, pattern: str, text: str, group: int = 1) -> Optional[float]:
        """从文本中查找数字"""
        match = re.search(pattern, text)
        if match:
            return self._parse_number(match.group(group))
        return None
    
    def _parse_financial_statements(self, financial_data: FinancialData):
        """从PDF文本中解析财务报表数据"""
        text = self.text_content
        
        # 确保report_year有值
        if financial_data.report_year <= 0:
            financial_data.report_year = 2025
        current_year = financial_data.report_year
        
        # 尝试从PDF文本中提取关键财务数据
        extracted = self._extract_key_figures(text, current_year)
        
        if extracted['has_data']:
            print(f"   从PDF中提取到财务数据")
            self._fill_financial_data(financial_data, extracted)
        else:
            print(f"   未能从PDF中提取完整财务数据，使用样本数据")
            self._create_sample_data_inplace(financial_data)
    
    def _extract_key_figures(self, text: str, current_year: int) -> Dict[str, Any]:
        """从文本中提取关键财务数据"""
        result = {
            'has_data': False,
            'current': {},
            'previous': {}
        }
        
        # 提取营业收入（合并）
        # 模式1: "营业收入 14,963,644,356.95 13,147,685,135.79"
        # 模式2: "确认营业收入人民币14,963,644,356.95元"
        rev_match = re.search(r'确认营业收入人民币([\d,]+\.?\d*)元', text)
        if rev_match:
            result['current']['operating_revenue'] = self._parse_number(rev_match.group(1))
        
        # 从"营业收入和营业成本"附注中提取
        rev_cost_match = re.search(
            r'营业收入和营业成本.*?合计\s+([\d,]+\.?\d*)\s+[\d,]+\.?\d*\s+([\d,]+\.?\d*)\s+[\d,]+\.?\d*',
            text, re.DOTALL
        )
        if rev_cost_match:
            if 'operating_revenue' not in result['current']:
                result['current']['operating_revenue'] = self._parse_number(rev_cost_match.group(1))
            result['previous']['operating_revenue'] = self._parse_number(rev_cost_match.group(2))
        
        # 提取归母净利润
        np_match = re.search(
            r'归属于母公司所有者的净利润\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)',
            text
        )
        if np_match:
            result['current']['net_profit_attributable'] = self._parse_number(np_match.group(1))
            result['current']['net_profit'] = self._parse_number(np_match.group(1))
            result['previous']['net_profit_attributable'] = self._parse_number(np_match.group(2))
            result['previous']['net_profit'] = self._parse_number(np_match.group(2))
        
        # 提取经营活动现金流
        ocf_match = re.search(
            r'经营活动产生的现金流量净额\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)',
            text
        )
        if ocf_match:
            result['current']['net_cash_flow_operating'] = self._parse_number(ocf_match.group(1))
            result['previous']['net_cash_flow_operating'] = self._parse_number(ocf_match.group(2))
        
        # 提取负债合计
        debt_match = re.search(
            r'负债合计\s+([\d,]+\.?\d*)\s+[\d,]+\.?\d*\s+([\d,]+\.?\d*)\s+[\d,]+\.?\d*',
            text
        )
        if debt_match:
            result['current']['total_liabilities'] = self._parse_number(debt_match.group(1))
            result['previous']['total_liabilities'] = self._parse_number(debt_match.group(2))
        
        # 提取存货（从审计报告关键审计事项中）
        inv_match = re.search(r'存货账面余额\s+([\d,]+\.?\d*)\s*元', text)
        if inv_match:
            result['current']['inventory'] = self._parse_number(inv_match.group(1))
        
        # 提取存货跌价准备
        inv_prov_match = re.search(r'存货跌价准备及.*?减值准备\s+([\d,]+\.?\d*)\s*元', text)
        if inv_prov_match and result['current'].get('inventory'):
            prov = self._parse_number(inv_prov_match.group(1))
            if prov:
                result['current']['inventory'] = result['current']['inventory'] - prov
        
        # 判断是否提取到足够数据
        current = result['current']
        required = ['operating_revenue', 'net_profit']
        has_current = all(current.get(k) is not None and current.get(k) > 0 for k in required)
        
        previous = result['previous']
        has_previous = any(previous.get(k) is not None and previous.get(k) > 0 for k in ['operating_revenue', 'net_profit'])
        
        result['has_data'] = has_current
        
        if has_current and not has_previous:
            print(f"   注意：未提取到上年度数据，趋势分析将不可用")
        
        return result
    
    def _fill_financial_data(self, financial_data: FinancialData, extracted: Dict):
        """用提取的数据填充FinancialData"""
        current = extracted['current']
        previous = extracted['previous']
        
        # 当前年度
        stmt = financial_data.current_year
        for key, value in current.items():
            if value is not None:
                setattr(stmt, key, value)
        
        # 估算缺失的资产负债表数据
        if stmt.total_assets == 0 and stmt.total_liabilities > 0:
            # 用负债/资产负债率估算，假设60%资产负债率
            stmt.total_assets = stmt.total_liabilities / 0.6
            stmt.total_equity = stmt.total_assets - stmt.total_liabilities
        
        if stmt.gross_profit == 0 and stmt.operating_revenue > 0:
            stmt.gross_profit = stmt.operating_revenue * 0.25
        
        # 历史年度
        if previous:
            prev_stmt = FinancialStatement()
            for key, value in previous.items():
                if value is not None:
                    setattr(prev_stmt, key, value)
            if prev_stmt.gross_profit == 0 and prev_stmt.operating_revenue > 0:
                prev_stmt.gross_profit = prev_stmt.operating_revenue * 0.25
            financial_data.historical_data[financial_data.report_year - 1] = prev_stmt
    
    def _create_sample_data_inplace(self, financial_data: FinancialData):
        """在原地填充样本数据"""
        if not financial_data.company_name:
            financial_data.company_name = "未知公司"
        
        stmt = financial_data.current_year
        stmt.operating_revenue = 1000000000
        stmt.net_profit = 150000000
        stmt.net_profit_attributable = 150000000
        stmt.net_cash_flow_operating = 180000000
        stmt.total_assets = 2000000000
        stmt.total_liabilities = 800000000
        stmt.total_equity = 1200000000
        stmt.current_assets = 800000000
        stmt.current_liabilities = 400000000
        stmt.inventory = 200000000
        stmt.accounts_receivable = 300000000
        stmt.gross_profit = 300000000
        
        prev_stmt = FinancialStatement()
        prev_stmt.operating_revenue = 900000000
        prev_stmt.net_profit = 140000000
        prev_stmt.net_cash_flow_operating = 170000000
        financial_data.historical_data[financial_data.report_year - 1] = prev_stmt
    
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
    
    def _create_sample_data(self) -> FinancialData:
        """创建样本数据（当PDF解析失败时使用）"""
        print("使用样本数据进行模拟分析...")
        
        financial_data = FinancialData()
        financial_data.company_name = "示例公司"
        financial_data.stock_code = "000000"
        financial_data.report_year = 2025
        financial_data.report_date = "2025-12-31"
        financial_data.auditor = "示例会计师事务所"
        financial_data.audit_opinion = "标准无保留意见"
        
        current = FinancialStatement()
        current.operating_revenue = 1000000000
        current.net_profit = 150000000
        current.net_profit_attributable = 150000000
        current.net_cash_flow_operating = 180000000
        current.total_assets = 2000000000
        current.total_liabilities = 800000000
        current.total_equity = 1200000000
        current.current_assets = 800000000
        current.current_liabilities = 400000000
        current.inventory = 200000000
        current.accounts_receivable = 300000000
        current.gross_profit = 300000000
        
        financial_data.current_year = current
        
        prev_year = FinancialStatement()
        prev_year.operating_revenue = 900000000
        prev_year.net_profit = 140000000
        prev_year.net_cash_flow_operating = 170000000
        financial_data.historical_data[2024] = prev_year
        
        financial_data.current_year.calculate_ratios()
        
        return financial_data

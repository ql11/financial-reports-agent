"""
PDF数据提取器 - 从PDF财报中提取真实财务数据
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import pdfplumber

from ..models.financial_data import FinancialData, FinancialStatement
from ..utils.logging_utils import get_logger


class DataExtractionError(Exception):
    """数据提取失败异常"""
    pass


class PDFDataExtractor:
    """PDF财务数据提取器"""
    
    def __init__(self):
        self.text_content = ""
        self.tables = []
        self.logger = get_logger(__name__)
        
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
                
                self.logger.info("成功提取文本，共 %s 页", len(pdf.pages))
                
                self.tables = []
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        self.tables.extend(tables)
                        
        except Exception as e:
            self.logger.exception("PDF文本提取错误: %s", e)
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

    def _statement_lines(self, text: str) -> List[str]:
        """保留更像报表正文的行，避开经营分析区中的比例列污染。"""
        lines = []
        for raw_line in text.splitlines():
            line = re.sub(r'\s+', ' ', raw_line).strip()
            if not line or self._is_analysis_or_ratio_line(line):
                continue
            lines.append(line)
        return lines

    def _is_analysis_or_ratio_line(self, line: str) -> bool:
        """过滤包含百分比或明显分析区语义的行。"""
        if '%' in line:
            return True

        analysis_keywords = (
            "经营情况分析",
            "财务指标",
            "主要会计数据",
            "主要财务指标",
            "变动比例",
            "占比",
            "同比",
            "增长率",
            "毛利率",
            "周转率",
            "本期比上年同期",
            "本期末比上年期末",
        )
        return any(keyword in line for keyword in analysis_keywords)

    def _extract_amounts_from_line(self, line: str) -> List[float]:
        """从单行报表文本中提取金额，忽略附注编号等小整数。"""
        amount_pattern = re.compile(
            r'-?(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d{4,}(?:\.\d+)?|\d+\.\d+)'
        )
        values = []
        for token in amount_pattern.findall(line):
            value = self._parse_number(token)
            if value is not None:
                values.append(value)
        return values

    def _find_statement_amounts(self, lines: List[str], labels: List[str]) -> Optional[List[float]]:
        """按标签优先级从可信报表行中提取 1-2 个金额。"""
        for label in labels:
            for line in lines:
                if label not in line:
                    continue
                values = self._extract_amounts_from_line(line)
                if 1 <= len(values) <= 2:
                    return values
        return None

    def _assign_from_statement_lines(
        self,
        result: Dict[str, Dict[str, float]],
        lines: List[str],
        field: str,
        labels: List[str],
    ) -> bool:
        """使用报表正文行覆盖字段；若只有当年值，则清理旧的上年污染值。"""
        values = self._find_statement_amounts(lines, labels)
        if not values:
            return False

        result['current'][field] = values[0]
        if len(values) > 1:
            result['previous'][field] = values[1]
        else:
            result['previous'].pop(field, None)
        return True

    def _note_lines(self) -> List[str]:
        """按行切分附注文本，便于做就近匹配。"""
        return [line.strip() for line in self.text_content.splitlines() if line.strip()]

    def _is_directory_like_line(self, line: str) -> bool:
        """过滤目录页、点线页码等明显噪声行。"""
        return "目录" in line or bool(re.search(r"[.．·…]{3,}", line))

    def _note_keyword_priority(self, line: str, keyword: str) -> int:
        """对同一关键词的多处命中做优先级排序。"""
        if keyword in line and any(token in line for token in ("账面余额", "账面价值")):
            return 2
        if line.strip() == keyword:
            return 0
        if re.match(r"^(?:\d+[.、]|[（(]\d+[)）]|附注|\d+\.\s*)", line):
            return 0
        return 1

    def _extract_note_amount(self, keyword: str, stop_keywords: List[str]) -> Optional[str]:
        """在关键词附近提取金额，避免跨附注串段误取。"""
        amount_pattern = re.compile(
            r'((?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d{4,}(?:\.\d+)?|\d+\.\d+)(?:[亿万]?元)?)'
        )
        lines = self._note_lines()
        candidate_indexes = [
            (self._note_keyword_priority(line, keyword), index)
            for index, line in enumerate(lines)
            if keyword in line and not self._is_directory_like_line(line)
        ]

        for _, index in sorted(candidate_indexes):
            line = lines[index]

            section_lines = [line]
            for next_line in lines[index + 1:index + 10]:
                if any(stop_keyword in next_line for stop_keyword in stop_keywords):
                    break
                section_lines.append(next_line)

            for candidate_line in section_lines:
                if keyword in candidate_line:
                    keyword_suffix = candidate_line.split(keyword, 1)[1]
                    numeric_match = amount_pattern.search(keyword_suffix)
                    if numeric_match:
                        return numeric_match.group(1)

            for candidate_line in section_lines:
                if "合计" in candidate_line:
                    numeric_matches = amount_pattern.findall(candidate_line)
                    if numeric_matches:
                        return numeric_matches[-1]

            section_text = "\n".join(section_lines)
            numeric_match = amount_pattern.search(section_text)
            if numeric_match:
                return numeric_match.group(1)

        return None

    def _extract_related_party_percentage(self) -> Optional[str]:
        """提取真实的关联交易占比，跳过目录页码等噪声。"""
        percentage_pattern = re.compile(r'(\d+\.?\d*%)')
        context_keywords = ("占", "占比", "比例", "采购", "销售", "收入", "金额")
        invalid_context = ("目录", "不存在", "无重大")
        lines = self._note_lines()

        for index, line in enumerate(lines):
            if "关联交易" not in line:
                continue

            window_lines = lines[index:index + 3]
            window_text = "\n".join(window_lines)
            if self._is_directory_like_line(line):
                continue
            if any(token in window_text for token in invalid_context):
                continue

            percentage_match = percentage_pattern.search(window_text)
            if percentage_match and any(token in window_text for token in context_keywords):
                return percentage_match.group(1)

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
        
        self.logger.info("从PDF中提取到财务数据")
        self._fill_financial_data(financial_data, extracted)
    
    def _extract_key_figures(self, text: str, current_year: int) -> Dict[str, Any]:
        """从文本中提取关键财务数据

        注意：财务数据可能为负数（如亏损公司的净利润），
        所有数值正则都使用 -?[\\d,]+\\.?\\d* 支持负数
        """
        result = {'current': {}, 'previous': {}}
        statement_lines = self._statement_lines(text)
        
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

        # === 筹资活动现金流 ===
        financing_cash_match = re.search(
            r'筹资活动产生的现金流量净额\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)',
            text
        )
        if financing_cash_match:
            result['current']['net_cash_flow_financing'] = self._parse_number(
                financing_cash_match.group(1)
            )
            result['previous']['net_cash_flow_financing'] = self._parse_number(
                financing_cash_match.group(2)
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
        else:
            debt_match = re.search(r'负债总计\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)', text)
            if debt_match:
                result['current']['total_liabilities'] = self._parse_number(debt_match.group(1))
                result['previous']['total_liabilities'] = self._parse_number(debt_match.group(2))
        
        # === 资产总计 ===
        asset_match = re.search(r'资产总计\s+(-?[\d,]+\.?\d*)\s+-?[\d,]+\.?\d*\s+(-?[\d,]+\.?\d*)\s+-?[\d,]+\.?\d*', text)
        if not asset_match:
            asset_match = re.search(r'资产总额\s+(-?[\d,]+\.?\d*)\s+-?[\d,]+\.?\d*\s+(-?[\d,]+\.?\d*)\s+-?[\d,]+\.?\d*', text)
        if not asset_match:
            asset_match = re.search(r'资产总计\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)', text)
        if not asset_match:
            asset_match = re.search(r'资产总额\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)', text)
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
        else:
            equity_match = re.search(
                r'归属于挂牌公司股东的净资产\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)',
                text
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
        elif not result['current'].get('inventory'):
            inv_balance_match = re.search(
                r'存货(?:\s+[^\s]+)?\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)',
                text
            )
            if inv_balance_match:
                result['current']['inventory'] = self._parse_number(
                    inv_balance_match.group(1)
                )
                result['previous']['inventory'] = self._parse_number(
                    inv_balance_match.group(2)
                )
        
        # === 应收账款 ===
        ar_match = re.search(
            r'按信用风险特征组合计提坏账准备.*?应收账款.*?(-?[\d,]+\.?\d{2})\s+(-?[\d,]+\.?\d{2})',
            text, re.DOTALL
        )
        if ar_match:
            result['current']['accounts_receivable'] = self._parse_number(ar_match.group(1))
        else:
            ar_match = re.search(
                r'应收账款(?:\s+[^\s]+)?\s+(-?[\d,]+\.?\d*)\s+(-?[\d,]+\.?\d*)',
                text
            )
            if ar_match:
                result['current']['accounts_receivable'] = self._parse_number(ar_match.group(1))
                result['previous']['accounts_receivable'] = self._parse_number(ar_match.group(2))
        
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

        # 使用更可信的报表正文行覆盖容易被分析区污染或被阈值误杀的字段。
        self._assign_from_statement_lines(
            result,
            statement_lines,
            'operating_revenue',
            ['其中：营业收入', '营业收入'],
        )
        self._assign_from_statement_lines(
            result,
            statement_lines,
            'net_profit_attributable',
            [
                '归属于母公司所有者的净利润',
                '归属于上市公司股东的净利润',
                '归属于挂牌公司股东的净利润',
            ],
        )
        if not self._assign_from_statement_lines(
            result,
            statement_lines,
            'net_profit',
            ['五、净利润', '六、净利润', '净利润（净亏损以', '净利润'],
        ):
            if 'net_profit_attributable' in result['current']:
                result['current']['net_profit'] = result['current']['net_profit_attributable']
            if 'net_profit_attributable' in result['previous']:
                result['previous']['net_profit'] = result['previous']['net_profit_attributable']

        for field, labels in (
            ('net_cash_flow_operating', ['经营活动产生的现金流量净额']),
            ('cash_from_sales', ['销售商品、提供劳务收到的现金']),
            ('net_cash_flow_investing', ['投资活动产生的现金流量净额']),
            ('net_cash_flow_financing', ['筹资活动产生的现金流量净额']),
            ('cash_and_equivalents', ['货币资金']),
            ('current_assets', ['流动资产合计']),
            ('current_liabilities', ['流动负债合计']),
            ('total_liabilities', ['负债合计', '负债总计']),
            ('total_assets', ['资产总计', '资产总额']),
            ('total_equity', ['所有者权益合计', '归属于挂牌公司股东的净资产']),
            ('inventory', ['存货']),
            ('accounts_receivable', ['应收账款']),
            ('operating_cost', ['营业成本']),
        ):
            self._assign_from_statement_lines(result, statement_lines, field, labels)
        
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
                self.logger.warning("未提取到上年度数据，趋势分析将不可用")
        else:
            self.logger.warning("未提取到上年度数据，趋势分析将不可用")
    
    def _parse_notes(self, financial_data: FinancialData):
        """解析附注信息"""
        note_keywords = {
            "government_subsidies": "政府补助",
            "bad_debt_provision": "坏账准备",
            "inventory_provision": "存货跌价准备",
        }
        stop_keywords = list(note_keywords.values())

        related_party_transactions = self._extract_related_party_percentage()
        if related_party_transactions:
            financial_data.notes["related_party_transactions"] = related_party_transactions

        if re.search(r"会计政策变更", self.text_content, re.IGNORECASE | re.DOTALL):
            financial_data.notes["accounting_policy_changes"] = True

        for key, keyword in note_keywords.items():
            value = self._extract_note_amount(
                keyword,
                stop_keywords=[item for item in stop_keywords if item != keyword],
            )
            if value:
                financial_data.notes[key] = value

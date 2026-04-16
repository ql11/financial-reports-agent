from src.core.data_extractor import PDFDataExtractor
from src.models.financial_data import FinancialData


def test_parse_company_info_extracts_stock_code_from_neeq_annual_report():
    extractor = PDFDataExtractor()
    extractor.text_content = """
亚迪纳
NEEQ: 833301
浙江亚迪纳新材料科技股份有限公司
年度报告
2025
挂牌情况
证券简称 亚迪纳 证券代码 833301
"""
    data = FinancialData()

    extractor._parse_company_info(data)

    assert data.stock_code == "833301"


def test_extract_key_figures_parses_liquidity_fields_from_balance_sheet_text():
    extractor = PDFDataExtractor()
    text = """
营业收入 111,366,098.57 118,199,226.51
归属于母公司所有者的净利润 12,477,098.91 20,041,463.26
经营活动产生的现金流量净额 20,469,639.54 21,684,371.91
投资活动产生的现金流量净额 -2,101,191.67 -464,520.96
货币资金 五、1 35,312,377.38 12,792,378.82
存货 五、7 5,565,539.05 4,670,255.21
流动资产合计 89,265,690.89 71,044,366.54
流动负债合计 22,322,042.00 21,761,339.74
资产总计 108,675,298.50 91,739,934.59
负债合计 22,322,042.00 21,761,339.74
"""

    extracted = extractor._extract_key_figures(text, 2025)

    assert extracted["current"]["cash_and_equivalents"] == 35312377.38
    assert extracted["current"]["current_assets"] == 89265690.89
    assert extracted["current"]["current_liabilities"] == 22322042.00
    assert extracted["current"]["inventory"] == 5565539.05
    assert extracted["current"]["net_cash_flow_investing"] == -2101191.67


def test_extract_key_figures_parses_balance_sheet_and_financing_fields_from_two_column_text():
    extractor = PDFDataExtractor()
    text = """
营业收入 111,366,098.57 118,199,226.51
归属于母公司所有者的净利润 12,477,098.91 20,041,463.26
筹资活动产生的现金流量净额 490,000.00 -13,505,337.77
应收账款 五、3 28,945,017.84 30,582,101.06
资产总计 108,675,298.50 91,739,934.59
负债总计 22,322,042.00 21,761,339.74
归属于挂牌公司股东的净资产 84,964,993.51 69,812,894.60
"""

    extracted = extractor._extract_key_figures(text, 2025)

    assert extracted["current"]["net_cash_flow_financing"] == 490000.00
    assert extracted["previous"]["net_cash_flow_financing"] == -13505337.77
    assert extracted["current"]["accounts_receivable"] == 28945017.84
    assert extracted["previous"]["accounts_receivable"] == 30582101.06
    assert extracted["current"]["total_assets"] == 108675298.50
    assert extracted["previous"]["total_assets"] == 91739934.59
    assert extracted["current"]["total_liabilities"] == 22322042.00
    assert extracted["previous"]["total_liabilities"] == 21761339.74
    assert extracted["current"]["total_equity"] == 84964993.51
    assert extracted["previous"]["total_equity"] == 69812894.60


def test_extract_key_figures_parses_neeq_net_profit_without_large_amount_threshold():
    extractor = PDFDataExtractor()
    text = """
归属于挂牌公司股东的净利润 62,360.44 -1,052,619.66 105.92%
五、净利润（净亏损以“－”号填列） 62,360.44 -1,052,619.66
1.持续经营净利润（净亏损以“-”号填列） 62,360.44 -1,052,619.66
2.归属于母公司所有者的净利润（净亏损以“-”号填列） 62,360.44 -1,052,619.66
"""

    extracted = extractor._extract_key_figures(text, 2025)

    assert extracted["current"]["net_profit"] == 62360.44
    assert extracted["previous"]["net_profit"] == -1052619.66
    assert extracted["current"]["net_profit_attributable"] == 62360.44
    assert extracted["previous"]["net_profit_attributable"] == -1052619.66


def test_extract_key_figures_prefers_statement_lines_over_operating_analysis_ratios():
    extractor = PDFDataExtractor()
    text = """
经营情况分析
货币资金 55,765,666.18 42.46% 37,776,213.90 32.06% 47.62%
应收账款 21,249,889.68 16.18% 27,450,067.49 23.30% -22.59%
存货 42,824,470.62 32.61% 27,158,181.33 23.05% 57.69%
货币资金 附注五、1 55,765,666.18 37,776,213.90
应收账款 附注五、3 21,249,889.68 27,450,067.49
存货 附注五、5 42,824,470.62 27,158,181.33
流动资产合计 124,936,173.72 111,113,276.21
流动负债合计 84,389,688.60 68,706,660.22
资产总计 131,331,303.17 117,812,671.58
负债合计 84,389,688.60 68,706,660.22
其中：营业收入 附注五、22 224,861,569.31 280,589,139.19
五、净利润（净亏损以“－”号填列） 438,643.21 6,612,499.30
2.归属于母公司所有者的净利润（净亏损以“-”号填列） 659,358.66 6,668,858.15
"""

    extracted = extractor._extract_key_figures(text, 2025)

    assert extracted["current"]["cash_and_equivalents"] == 55765666.18
    assert extracted["previous"]["cash_and_equivalents"] == 37776213.90
    assert extracted["current"]["accounts_receivable"] == 21249889.68
    assert extracted["previous"]["accounts_receivable"] == 27450067.49
    assert extracted["current"]["inventory"] == 42824470.62
    assert extracted["previous"]["inventory"] == 27158181.33


def test_extract_key_figures_parses_single_year_line_with_note_reference():
    extractor = PDFDataExtractor()
    text = """
应收账款 五、（二） 23,750.00
货币资金 五、（一） 542,973.33 688,978.58
流动资产合计 612,965.65 817,386.51
流动负债合计 380,761.79 361,243.81
资产总计 902,661.95 817,386.51
负债合计 384,158.81 361,243.81
"""

    extracted = extractor._extract_key_figures(text, 2025)

    assert extracted["current"]["accounts_receivable"] == 23750.00
    assert "accounts_receivable" not in extracted["previous"]


def test_parse_notes_ignores_false_positive_single_digit_amounts():
    extractor = PDFDataExtractor()
    extractor.text_content = """
五、1 政府补助
单位：元
五、2 坏账准备
单位：元
五、3 存货跌价准备
单位：元
"""
    data = FinancialData()

    extractor._parse_notes(data)

    assert "government_subsidies" not in data.notes
    assert "bad_debt_provision" not in data.notes
    assert "inventory_provision" not in data.notes


def test_parse_notes_extracts_amounts_from_nearby_sections_only():
    extractor = PDFDataExtractor()
    extractor.text_content = """
政府补助
本期收到的政府补助情况详见其他收益附注。

坏账准备
期末坏账准备余额为123,456.78元。

存货跌价准备
期末存货跌价准备余额为234,567.89元。

其他收益
其中政府补助金额为345,678.90元。
"""
    data = FinancialData()

    extractor._parse_notes(data)

    assert data.notes["government_subsidies"] == "345,678.90元"
    assert data.notes["bad_debt_provision"] == "123,456.78元"
    assert data.notes["inventory_provision"] == "234,567.89元"


def test_parse_notes_skips_directory_style_related_party_percentages():
    extractor = PDFDataExtractor()
    extractor.text_content = """
目录
关联交易情况................................100%

报告期内不存在需要披露的重大关联交易。
"""
    data = FinancialData()

    extractor._parse_notes(data)

    assert "related_party_transactions" not in data.notes


def test_parse_notes_extracts_table_amount_without_currency_suffix():
    extractor = PDFDataExtractor()
    extractor.text_content = """
存货跌价准备
项目 2024年12月31日 本期增加 本期减少 2025年12月31日
库存商品 380,497.08 1,099,237.48 367,209.30 1,112,525.26
合计 380,497.08 367,209.30 1,112,525.26
"""
    data = FinancialData()

    extractor._parse_notes(data)

    assert data.notes["inventory_provision"] == "1,112,525.26"


def test_parse_notes_prefers_explicit_note_section_over_header_rows():
    extractor = PDFDataExtractor()
    extractor.text_content = """
账面余额 存货跌价准备 账面价值
原材料 3,374,016.39 3,374,016.39
合计 6,678,064.31 1,112,525.26 5,565,539.05

（2）存货跌价准备
项目 2024年12月31日 本期增加 本期减少 2025年12月31日
库存商品 380,497.08 1,099,237.48 367,209.30 1,112,525.26
合计 380,497.08 367,209.30 1,112,525.26
"""
    data = FinancialData()

    extractor._parse_notes(data)

    assert data.notes["inventory_provision"] == "1,112,525.26"


def test_parse_notes_skips_policy_sections_without_amount_evidence():
    extractor = PDFDataExtractor()
    extractor.text_content = """
（二十）政府补助
政府补助，是公司从政府无偿取得货币性资产或非货币性资产。
1. 与资产相关的政府补助判断依据及会计处理方法

应收账款
对于应收账款，若某一客户信用风险特征发生显著变化，本公司对该应收款项单项计提坏账准备。
"""
    data = FinancialData()

    extractor._parse_notes(data)

    assert "government_subsidies" not in data.notes
    assert "bad_debt_provision" not in data.notes


def test_parse_notes_does_not_flag_policy_or_estimate_changes_when_report_says_none():
    extractor = PDFDataExtractor()
    extractor.text_content = """
1. 重要会计政策变更
本报告期公司主要会计政策未发生变更。
2. 重要会计估计变更
本报告期公司主要会计估计未发生变更。
"""
    data = FinancialData()

    extractor._parse_notes(data)

    assert "accounting_policy_changes" not in data.notes
    assert "accounting_estimate_changes" not in data.notes


def test_parse_notes_extracts_estimate_changes_and_deferred_income_when_present():
    extractor = PDFDataExtractor()
    extractor.text_content = """
会计估计变更
固定资产折旧年限由5年变更为8年。

递延收益
项目 期初余额 本期增加 本期减少 期末余额
政府补助 800,000.00 500,000.00 65,432.10 1,234,567.90
合计 800,000.00 500,000.00 65,432.10 1,234,567.90
"""
    data = FinancialData()

    extractor._parse_notes(data)

    assert data.notes["accounting_estimate_changes"] == "固定资产折旧年限由5年变更为8年。"
    assert data.notes["deferred_income"] == "1,234,567.90"

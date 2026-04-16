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

"""
配置模型

该模块定义了系统配置相关的数据模型：
- RiskThresholds: 风险阈值配置
- AnalysisConfig: 分析配置
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


@dataclass
class RiskThresholds:
    """风险阈值配置

    定义了各类财务指标的风险阈值，用于风险识别

    Attributes:
        debt_ratio_high: 资产负债率高风险阈值
        debt_ratio_medium: 资产负债率中风险阈值
        current_ratio_low: 流动比率低风险阈值
        quick_ratio_low: 速动比率低风险阈值
        gross_margin_low: 毛利率低风险阈值
        net_margin_low: 净利率低风险阈值
        roe_low: ROE低风险阈值
        revenue_growth_low: 营收增长率低风险阈值
        profit_growth_low: 净利润增长率低风险阈值
    """
    # 偿债能力阈值
    debt_ratio_high: float = 0.7
    debt_ratio_medium: float = 0.6
    current_ratio_low: float = 1.0
    quick_ratio_low: float = 0.5

    # 盈利能力阈值
    gross_margin_low: float = 0.2
    net_margin_low: float = 0.05
    roe_low: float = 0.1

    # 成长能力阈值
    revenue_growth_low: float = -0.1
    profit_growth_low: float = -0.1

    def to_dict(self) -> Dict[str, float]:
        """转换为字典格式

        Returns:
            Dict[str, float]: 阈值配置字典
        """
        return {
            '资产负债率高风险阈值': self.debt_ratio_high,
            '资产负债率中风险阈值': self.debt_ratio_medium,
            '流动比率低风险阈值': self.current_ratio_low,
            '速动比率低风险阈值': self.quick_ratio_low,
            '毛利率低风险阈值': self.gross_margin_low,
            '净利率低风险阈值': self.net_margin_low,
            'ROE低风险阈值': self.roe_low,
            '营收增长率低风险阈值': self.revenue_growth_low,
            '净利润增长率低风险阈值': self.profit_growth_low
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'RiskThresholds':
        """从字典创建配置对象

        Args:
            data: 配置字典

        Returns:
            RiskThresholds: 配置对象
        """
        return cls(
            debt_ratio_high=data.get('debt_ratio_high', 0.7),
            debt_ratio_medium=data.get('debt_ratio_medium', 0.6),
            current_ratio_low=data.get('current_ratio_low', 1.0),
            quick_ratio_low=data.get('quick_ratio_low', 0.5),
            gross_margin_low=data.get('gross_margin_low', 0.2),
            net_margin_low=data.get('net_margin_low', 0.05),
            roe_low=data.get('roe_low', 0.1),
            revenue_growth_low=data.get('revenue_growth_low', -0.1),
            profit_growth_low=data.get('profit_growth_low', -0.1)
        )


class RiskThresholdsPydantic(BaseModel):
    """风险阈值配置（Pydantic版本）"""
    # 偿债能力阈值
    debt_ratio_high: float = Field(default=0.7, gt=0, le=1, description="资产负债率高风险阈值")
    debt_ratio_medium: float = Field(default=0.6, gt=0, le=1, description="资产负债率中风险阈值")
    current_ratio_low: float = Field(default=1.0, gt=0, description="流动比率低风险阈值")
    quick_ratio_low: float = Field(default=0.5, gt=0, description="速动比率低风险阈值")

    # 盈利能力阈值
    gross_margin_low: float = Field(default=0.2, gt=0, le=1, description="毛利率低风险阈值")
    net_margin_low: float = Field(default=0.05, gt=0, le=1, description="净利率低风险阈值")
    roe_low: float = Field(default=0.1, gt=0, le=1, description="ROE低风险阈值")

    # 成长能力阈值
    revenue_growth_low: float = Field(default=-0.1, description="营收增长率低风险阈值")
    profit_growth_low: float = Field(default=-0.1, description="净利润增长率低风险阈值")

    @validator('debt_ratio_medium')
    def validate_debt_ratio_thresholds(cls, v, values):
        """验证资产负债率阈值逻辑"""
        if 'debt_ratio_high' in values:
            if v >= values['debt_ratio_high']:
                raise ValueError('中风险阈值应小于高风险阈值')
        return v


@dataclass
class AnalysisConfig:
    """分析配置

    定义了系统运行的全局配置

    Attributes:
        source_folder: 源文件夹路径
        repository_folder: 仓库文件夹路径
        output_folder: 输出文件夹路径
        analysis_dimensions: 分析维度列表
        risk_thresholds: 风险阈值配置
        industry_benchmarks: 行业基准数据
        log_level: 日志级别
        log_folder: 日志文件夹
        batch_size: 批处理大小
        timeout: 超时时间（秒）
    """
    source_folder: str
    repository_folder: str
    output_folder: str

    # 分析维度
    analysis_dimensions: List[str] = field(default_factory=lambda: [
        '盈利能力', '偿债能力', '运营能力', '成长能力', '现金流'
    ])

    # 风险阈值
    risk_thresholds: RiskThresholds = field(default_factory=RiskThresholds)

    # 行业基准数据
    industry_benchmarks: Dict[str, Dict] = field(default_factory=dict)

    # 日志配置
    log_level: str = "INFO"
    log_folder: str = "logs"

    # 性能配置
    batch_size: int = 10
    timeout: int = 300

    def to_dict(self) -> Dict:
        """转换为字典格式

        Returns:
            Dict: 配置字典
        """
        return {
            'source_folder': self.source_folder,
            'repository_folder': self.repository_folder,
            'output_folder': self.output_folder,
            'analysis_dimensions': self.analysis_dimensions,
            'risk_thresholds': self.risk_thresholds.to_dict(),
            'industry_benchmarks': self.industry_benchmarks,
            'log_level': self.log_level,
            'log_folder': self.log_folder,
            'batch_size': self.batch_size,
            'timeout': self.timeout
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'AnalysisConfig':
        """从字典创建配置对象

        Args:
            data: 配置字典

        Returns:
            AnalysisConfig: 配置对象
        """
        risk_thresholds_data = data.get('risk_thresholds', {})
        risk_thresholds = RiskThresholds.from_dict(risk_thresholds_data)

        return cls(
            source_folder=data.get('source_folder', 'source'),
            repository_folder=data.get('repository_folder', 'repository'),
            output_folder=data.get('output_folder', 'reports'),
            analysis_dimensions=data.get('analysis_dimensions', [
                '盈利能力', '偿债能力', '运营能力', '成长能力', '现金流'
            ]),
            risk_thresholds=risk_thresholds,
            industry_benchmarks=data.get('industry_benchmarks', {}),
            log_level=data.get('log_level', 'INFO'),
            log_folder=data.get('log_folder', 'logs'),
            batch_size=data.get('batch_size', 10),
            timeout=data.get('timeout', 300)
        )

    def validate_paths(self) -> bool:
        """验证路径配置

        Returns:
            bool: 路径配置是否有效
        """
        return all([
            self.source_folder,
            self.repository_folder,
            self.output_folder,
            self.log_folder
        ])

    def get_enabled_dimensions(self) -> List[str]:
        """获取启用的分析维度

        Returns:
            List[str]: 启用的分析维度列表
        """
        return self.analysis_dimensions

    def is_dimension_enabled(self, dimension: str) -> bool:
        """检查指定分析维度是否启用

        Args:
            dimension: 分析维度名称

        Returns:
            bool: 是否启用
        """
        return dimension in self.analysis_dimensions


class AnalysisConfigPydantic(BaseModel):
    """分析配置（Pydantic版本）"""
    source_folder: str = Field(..., min_length=1, description="源文件夹路径")
    repository_folder: str = Field(..., min_length=1, description="仓库文件夹路径")
    output_folder: str = Field(..., min_length=1, description="输出文件夹路径")

    analysis_dimensions: List[str] = Field(
        default=['盈利能力', '偿债能力', '运营能力', '成长能力', '现金流'],
        description="分析维度列表"
    )

    risk_thresholds: RiskThresholdsPydantic = Field(
        default_factory=RiskThresholdsPydantic,
        description="风险阈值配置"
    )

    industry_benchmarks: Dict[str, Dict] = Field(
        default_factory=dict,
        description="行业基准数据"
    )

    log_level: str = Field(default="INFO", description="日志级别")
    log_folder: str = Field(default="logs", min_length=1, description="日志文件夹")

    batch_size: int = Field(default=10, gt=0, description="批处理大小")
    timeout: int = Field(default=300, gt=0, description="超时时间（秒）")

    @validator('log_level')
    def validate_log_level(cls, v):
        """验证日志级别"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'无效的日志级别: {v}')
        return v.upper()

    class Config:
        """Pydantic配置"""
        json_encoders = {
            RiskThresholdsPydantic: lambda v: v.dict()
        }


@dataclass
class IndustryBenchmark:
    """行业基准数据

    Attributes:
        industry_name: 行业名称
        indicators: 指标基准值
        sample_size: 样本数量
        update_time: 更新时间
    """
    industry_name: str
    indicators: Dict[str, float] = field(default_factory=dict)
    sample_size: int = 0
    update_time: str = ""

    def get_indicator(self, indicator_name: str) -> Optional[float]:
        """获取指定指标的基准值

        Args:
            indicator_name: 指标名称

        Returns:
            Optional[float]: 指标基准值，不存在则返回None
        """
        return self.indicators.get(indicator_name)

    def to_dict(self) -> Dict:
        """转换为字典格式

        Returns:
            Dict: 行业基准数据字典
        """
        return {
            '行业名称': self.industry_name,
            '指标基准': self.indicators,
            '样本数量': self.sample_size,
            '更新时间': self.update_time
        }


class IndustryBenchmarkPydantic(BaseModel):
    """行业基准数据（Pydantic版本）"""
    industry_name: str = Field(..., min_length=1, description="行业名称")
    indicators: Dict[str, float] = Field(default_factory=dict, description="指标基准值")
    sample_size: int = Field(default=0, ge=0, description="样本数量")
    update_time: str = Field(default="", description="更新时间")

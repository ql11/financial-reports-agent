"""
风险模型

该模块定义了风险识别相关的数据模型：
- RiskLevel: 风险等级枚举
- RiskType: 风险类型枚举
- Risk: 风险模型
- RiskList: 风险清单
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional

from pydantic import BaseModel, Field, validator


class RiskLevel(Enum):
    """风险等级枚举

    定义了三个风险等级：
    - HIGH: 高风险
    - MEDIUM: 中风险
    - LOW: 低风险
    """
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"

    @classmethod
    def from_value(cls, value: str) -> 'RiskLevel':
        """从字符串值创建枚举

        Args:
            value: 字符串值（"高"、"中"、"低"）

        Returns:
            RiskLevel: 对应的风险等级

        Raises:
            ValueError: 无效的风险等级值
        """
        for level in cls:
            if level.value == value:
                return level
        raise ValueError(f"无效的风险等级: {value}")

    def get_score_impact(self) -> int:
        """获取风险等级对评分的影响

        Returns:
            int: 扣分值
        """
        impact_map = {
            RiskLevel.HIGH: 3,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 1
        }
        return impact_map[self]


class RiskType(Enum):
    """风险类型枚举

    定义了三种风险类型：
    - FINANCIAL: 财务风险
    - OPERATION: 经营风险
    - WARNING: 潜在问题预警
    """
    FINANCIAL = "财务风险"
    OPERATION = "经营风险"
    WARNING = "潜在问题预警"

    @classmethod
    def from_value(cls, value: str) -> 'RiskType':
        """从字符串值创建枚举

        Args:
            value: 字符串值

        Returns:
            RiskType: 对应的风险类型

        Raises:
            ValueError: 无效的风险类型值
        """
        for risk_type in cls:
            if risk_type.value == value:
                return risk_type
        raise ValueError(f"无效的风险类型: {value}")


@dataclass
class Risk:
    """风险模型

    Attributes:
        risk_type: 风险类型
        risk_level: 风险等级
        description: 风险描述
        indicator_name: 相关指标名称
        indicator_value: 指标值
        threshold: 风险阈值
        impact: 影响说明
        recommendation: 建议措施
    """
    risk_type: RiskType
    risk_level: RiskLevel
    description: str
    indicator_name: str
    indicator_value: float
    threshold: float
    impact: str
    recommendation: str

    def to_dict(self) -> Dict:
        """转换为字典格式

        Returns:
            Dict: 风险信息字典
        """
        return {
            '风险类型': self.risk_type.value,
            '风险等级': self.risk_level.value,
            '风险描述': self.description,
            '相关指标': self.indicator_name,
            '指标值': self.indicator_value,
            '风险阈值': self.threshold,
            '影响说明': self.impact,
            '建议措施': self.recommendation
        }

    def get_severity_score(self) -> int:
        """获取风险严重程度评分

        Returns:
            int: 严重程度评分（1-10）
        """
        severity_map = {
            RiskLevel.HIGH: 8,
            RiskLevel.MEDIUM: 5,
            RiskLevel.LOW: 2
        }
        return severity_map[self.risk_level]

    def __str__(self) -> str:
        """字符串表示

        Returns:
            str: 风险的字符串表示
        """
        return (f"[{self.risk_level.value}风险] {self.description} "
                f"({self.indicator_name}: {self.indicator_value:.2f}, "
                f"阈值: {self.threshold:.2f})")


class RiskPydantic(BaseModel):
    """风险模型（Pydantic版本）"""
    risk_type: RiskType = Field(..., description="风险类型")
    risk_level: RiskLevel = Field(..., description="风险等级")
    description: str = Field(..., min_length=1, description="风险描述")
    indicator_name: str = Field(..., min_length=1, description="相关指标名称")
    indicator_value: float = Field(..., description="指标值")
    threshold: float = Field(..., description="风险阈值")
    impact: str = Field(..., min_length=1, description="影响说明")
    recommendation: str = Field(..., min_length=1, description="建议措施")

    class Config:
        """Pydantic配置"""
        use_enum_values = False


@dataclass
class RiskList:
    """风险清单

    Attributes:
        company_name: 公司名称
        report_year: 报告年度
        risks: 风险列表
        total_risks: 风险总数
        high_risks: 高风险数量
        medium_risks: 中风险数量
        low_risks: 低风险数量
        detection_time: 识别时间
    """
    company_name: str
    report_year: int
    risks: List[Risk] = field(default_factory=list)
    total_risks: int = field(default=0)
    high_risks: int = field(default=0)
    medium_risks: int = field(default=0)
    low_risks: int = field(default=0)
    detection_time: datetime = field(default_factory=datetime.now)

    def add_risk(self, risk: Risk) -> None:
        """添加风险

        Args:
            risk: 风险对象
        """
        self.risks.append(risk)
        self.total_risks += 1

        if risk.risk_level == RiskLevel.HIGH:
            self.high_risks += 1
        elif risk.risk_level == RiskLevel.MEDIUM:
            self.medium_risks += 1
        else:
            self.low_risks += 1

    def get_risks_by_level(self, level: RiskLevel) -> List[Risk]:
        """按风险等级获取风险列表

        Args:
            level: 风险等级

        Returns:
            List[Risk]: 指定等级的风险列表
        """
        return [risk for risk in self.risks if risk.risk_level == level]

    def get_risks_by_type(self, risk_type: RiskType) -> List[Risk]:
        """按风险类型获取风险列表

        Args:
            risk_type: 风险类型

        Returns:
            List[Risk]: 指定类型的风险列表
        """
        return [risk for risk in self.risks if risk.risk_type == risk_type]

    def get_total_score_impact(self) -> int:
        """获取风险对评分的总影响

        Returns:
            int: 总扣分值
        """
        return sum(risk.risk_level.get_score_impact() for risk in self.risks)

    def to_dict(self) -> Dict:
        """转换为字典格式

        Returns:
            Dict: 风险清单字典
        """
        return {
            '公司名称': self.company_name,
            '报告年度': self.report_year,
            '风险总数': self.total_risks,
            '高风险数量': self.high_risks,
            '中风险数量': self.medium_risks,
            '低风险数量': self.low_risks,
            '风险列表': [risk.to_dict() for risk in self.risks]
        }

    def get_summary(self) -> str:
        """获取风险摘要

        Returns:
            str: 风险摘要文本
        """
        summary_lines = [
            f"公司 {self.company_name} ({self.report_year}年度) 风险识别结果：",
            f"共识别出 {self.total_risks} 项风险",
            f"  - 高风险：{self.high_risks} 项",
            f"  - 中风险：{self.medium_risks} 项",
            f"  - 低风险：{self.low_risks} 项"
        ]
        return "\n".join(summary_lines)

    def has_high_risk(self) -> bool:
        """判断是否存在高风险

        Returns:
            bool: 是否存在高风险
        """
        return self.high_risks > 0

    def get_risk_level_distribution(self) -> Dict[str, float]:
        """获取风险等级分布

        Returns:
            Dict[str, float]: 风险等级分布百分比
        """
        if self.total_risks == 0:
            return {'高': 0, '中': 0, '低': 0}

        return {
            '高': self.high_risks / self.total_risks * 100,
            '中': self.medium_risks / self.total_risks * 100,
            '低': self.low_risks / self.total_risks * 100
        }


class RiskListPydantic(BaseModel):
    """风险清单（Pydantic版本）"""
    company_name: str = Field(..., min_length=1, description="公司名称")
    report_year: int = Field(..., ge=2000, le=2100, description="报告年度")
    risks: List[RiskPydantic] = Field(default_factory=list, description="风险列表")
    total_risks: int = Field(default=0, ge=0, description="风险总数")
    high_risks: int = Field(default=0, ge=0, description="高风险数量")
    medium_risks: int = Field(default=0, ge=0, description="中风险数量")
    low_risks: int = Field(default=0, ge=0, description="低风险数量")
    detection_time: datetime = Field(default_factory=datetime.now, description="识别时间")

    @validator('total_risks')
    def validate_total_risks(cls, v, values):
        """验证风险总数"""
        if 'risks' in values:
            expected = len(values['risks'])
            if v != expected:
                raise ValueError(f'风险总数({v})应等于风险列表长度({expected})')
        return v

    @validator('high_risks', 'medium_risks', 'low_risks')
    def validate_risk_counts(cls, v, values):
        """验证风险数量统计"""
        if 'risks' in values and 'total_risks' in values:
            total = values['high_risks'] + values['medium_risks'] + values['low_risks']
            if total != values['total_risks']:
                raise ValueError('风险数量统计不一致')
        return v

    class Config:
        """Pydantic配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

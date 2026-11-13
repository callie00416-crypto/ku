"""
报告领域枚举 - Report Domain Enums

【职责】
- 定义报告相关枚举类型
- 保证类型安全
- 提供业务语义

【设计原则】
- 枚举值一旦确定不再变更
- 每个枚举都有明确的工业含义
- 支持扩展但不破坏现有逻辑
"""
from enum import Enum


class ReportType(Enum):
    """报告类型"""
    TEST_RESULT = "test_result"        # 测试结果报告
    CALIBRATION = "calibration"        # 校准报告
    QUALIFICATION = "qualification"    # 资格认证报告
    COMPLIANCE = "compliance"          # 符合性报告
    DEBUG = "debug"                    # 调试报告


class ReportFormat(Enum):
    """报告格式"""
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"
    XML = "xml"
    CSV = "csv"


class ReportStatus(Enum):
    """报告状态（工业追溯状态机）
    
    【状态流转】
    draft -> generated -> archived
    
    【工业原则】
    - generated: 报告已生成，内容固定
    - archived: 报告已归档，进入长期存储
    - 禁止修改已生成的报告内容
    """
    DRAFT = "draft"          # 草稿
    GENERATED = "generated"  # 已生成
    ARCHIVED = "archived"    # 已归档


class RecordValueType(Enum):
    """记录值类型
    
    【工业测试值类型】
    - 支持工业测试的多样性
    - 为未来扩展预留空间
    """
    FLOAT = "float"          # 浮点数
    INT = "int"              # 整数
    BOOL = "bool"            # 布尔值
    STRING = "string"        # 字符串
    JSON = "json"            # JSON对象
    WAVEFORM = "waveform"    # 波形数据
    BINARY = "binary"        # 二进制数据
    TIMESTAMP = "timestamp"  # 时间戳
    IMAGE = "image"          # 图像数据
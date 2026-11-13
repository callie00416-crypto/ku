"""
报告领域异常 - Report Domain Exceptions

【职责】
- 定义报告领域特定异常
- 提供清晰的错误语义
- 支持异常分类处理

【设计原则】
- 异常层次清晰
- 错误信息明确
- 支持异常链路追踪
"""
from ..common.exceptions import DomainException


class ReportException(DomainException):
    """报告领域基础异常"""
    pass


class ReportNotFoundException(ReportException):
    """报告不存在异常"""
    
    def __init__(self, report_id: str):
        self.report_id = report_id
        super().__init__(f"报告不存在: {report_id}")


class ReportGenerationException(ReportException):
    """报告生成异常"""
    
    def __init__(self, report_id: str, reason: str):
        self.report_id = report_id
        self.reason = reason
        super().__init__(f"报告生成失败: {report_id}, 原因: {reason}")


class ReportArchiveException(ReportException):
    """报告归档异常"""
    
    def __init__(self, report_id: str, reason: str):
        self.report_id = report_id
        self.reason = reason
        super().__init__(f"报告归档失败: {report_id}, 原因: {reason}")


class ReportImmutableException(ReportException):
    """报告不可变异常（尝试修改已生成的报告）"""
    
    def __init__(self, report_id: str, operation: str):
        self.report_id = report_id
        self.operation = operation
        super().__init__(f"报告已固化不可修改: {report_id}, 操作: {operation}")


class ReportValidationException(ReportException):
    """报告验证异常"""
    
    def __init__(self, report_id: str, field: str, value: str, expected: str):
        self.report_id = report_id
        self.field = field
        self.value = value
        self.expected = expected
        super().__init__(f"报告验证失败: {report_id}, 字段: {field}, 值: {value}, 期望: {expected}")
"""
CaseResult - 测试用例结果

所属层级：TestCase 层
职责：标准测试用例结果对象

用于记录：
- 测试通过/失败
- 测试数据
- 断言结果
- 执行时间
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime


class CaseStatus(Enum):
    """用例状态"""
    IDLE = "idle"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class AssertLevel(Enum):
    """断言级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


@dataclass
class AssertResult:
    """断言结果"""
    passed: bool
    name: str
    expected: Any = None
    actual: Any = None
    message: str = ""
    level: str = AssertLevel.ERROR.value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'passed': self.passed,
            'name': self.name,
            'expected': str(self.expected),
            'actual': str(self.actual),
            'message': self.message,
            'level': self.level
        }


@dataclass
class CaseResult:
    """测试用例结果
    
    包含：
    - status: 用例状态
    - assertions: 断言结果列表
    - data: 测试数据
    - start_time/end_time: 执行时间
    - message: 结果消息
    """
    
    case_id: str = ""
    status: CaseStatus = CaseStatus.IDLE
    message: str = ""
    
    assertions: List[AssertResult] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: float = 0.0
    
    error_detail: Optional[str] = None
    stack_trace: Optional[str] = None
    
    def is_passed(self) -> bool:
        """是否通过"""
        return self.status == CaseStatus.PASSED
    
    def is_failed(self) -> bool:
        """是否失败"""
        return self.status in [CaseStatus.FAILED, CaseStatus.ERROR]
    
    def add_assertion(self, result: AssertResult):
        """添加断言结果"""
        self.assertions.append(result)
    
    def add_log(self, log: str):
        """添加日志"""
        self.logs.append(log)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取摘要"""
        total_asserts = len(self.assertions)
        passed_asserts = sum(1 for a in self.assertions if a.passed)
        failed_asserts = total_asserts - passed_asserts
        
        return {
            'case_id': self.case_id,
            'status': self.status.value,
            'message': self.message,
            'total_assertions': total_asserts,
            'passed_assertions': passed_asserts,
            'failed_assertions': failed_asserts,
            'duration': self.duration,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'case_id': self.case_id,
            'status': self.status.value,
            'message': self.message,
            'assertions': [a.to_dict() for a in self.assertions],
            'data': self.data,
            'logs': self.logs,
            'duration': self.duration,
            'error_detail': self.error_detail,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }
    
    @staticmethod
    def create_passed(case_id: str, message: str = "测试通过") -> 'CaseResult':
        """创建通过结果"""
        return CaseResult(
            case_id=case_id,
            status=CaseStatus.PASSED,
            message=message
        )
    
    @staticmethod
    def create_failed(case_id: str, message: str, error_detail: str = None) -> 'CaseResult':
        """创建失败结果"""
        return CaseResult(
            case_id=case_id,
            status=CaseStatus.FAILED,
            message=message,
            error_detail=error_detail
        )
"""
ActionResult - 动作执行结果

所属层级：Action 层
职责：标准动作结果对象

为什么重要：
- Scheduler 失败恢复
- 动作追踪
- 状态机
- 日志系统
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from enum import Enum


class ResultStatus(Enum):
    """结果状态"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    RUNNING = "running"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ActionResult:
    """动作执行结果
    
    统一结果对象，包含：
    - success: 是否成功
    - message: 结果消息
    - data: 返回数据
    - error_code: 错误码
    - duration: 执行时长
    """
    
    success: bool = True
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    error_code: Optional[str] = None
    status: ResultStatus = ResultStatus.SUCCESS
    duration: float = 0.0
    error_detail: Optional[str] = None
    
    def is_success(self) -> bool:
        """是否成功"""
        return self.success and self.status == ResultStatus.SUCCESS
    
    def is_failed(self) -> bool:
        """是否失败"""
        return not self.success or self.status in [
            ResultStatus.FAILED,
            ResultStatus.TIMEOUT,
            ResultStatus.CANCELLED
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'status': self.status.value,
            'message': self.message,
            'data': self.data,
            'error_code': self.error_code,
            'duration': self.duration,
            'error_detail': self.error_detail
        }
    
    @staticmethod
    def success(message: str = "", data: Dict = None) -> 'ActionResult':
        """创建成功结果"""
        return ActionResult(
            success=True,
            status=ResultStatus.SUCCESS,
            message=message,
            data=data or {}
        )
    
    @staticmethod
    def failed(message: str = "", error_code: str = None, 
               error_detail: str = None) -> 'ActionResult':
        """创建失败结果"""
        return ActionResult(
            success=False,
            status=ResultStatus.FAILED,
            message=message,
            error_code=error_code,
            error_detail=error_detail
        )
    
    @staticmethod
    def timeout(message: str = "执行超时") -> 'ActionResult':
        """创建超时结果"""
        return ActionResult(
            success=False,
            status=ResultStatus.TIMEOUT,
            message=message,
            error_code="TIMEOUT"
        )
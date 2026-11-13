"""
告警领域异常 - Alarm Domain Exceptions

【职责】
- 定义告警领域特定异常
- 提供清晰的错误语义
- 支持异常分类处理

【设计原则】
- 异常层次清晰
- 错误信息明确
- 支持异常链路追踪
"""
from ..common.exceptions import DomainException


class AlarmException(DomainException):
    """告警领域基础异常"""
    pass


class AlarmNotFoundException(AlarmException):
    """告警不存在异常"""
    
    def __init__(self, alarm_id: str):
        self.alarm_id = alarm_id
        super().__init__(f"告警不存在: {alarm_id}")


class AlarmStatusTransitionException(AlarmException):
    """告警状态转换异常"""
    
    def __init__(self, alarm_id: str, from_status: str, to_status: str):
        self.alarm_id = alarm_id
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(f"告警状态转换非法: {alarm_id} {from_status} -> {to_status}")


class AlarmAlreadyActiveException(AlarmException):
    """告警已激活异常"""
    
    def __init__(self, alarm_id: str):
        self.alarm_id = alarm_id
        super().__init__(f"告警已激活: {alarm_id}")


class AlarmAlreadyAcknowledgedException(AlarmException):
    """告警已确认异常"""
    
    def __init__(self, alarm_id: str):
        self.alarm_id = alarm_id
        super().__init__(f"告警已确认: {alarm_id}")


class AlarmAlreadyResolvedException(AlarmException):
    """告警已解决异常"""
    
    def __init__(self, alarm_id: str):
        self.alarm_id = alarm_id
        super().__init__(f"告警已解决: {alarm_id}")


class AlarmDeDuplicationException(AlarmException):
    """告警去重异常（同设备、同错误码、时间窗口内）"""
    
    def __init__(self, device_id: str, alarm_code: str, time_window: int):
        self.device_id = device_id
        self.alarm_code = alarm_code
        self.time_window = time_window
        super().__init__(f"告警去重: 设备{device_id} 错误码{alarm_code} 时间窗口{time_window}s")
"""
领域异常 - Domain Exceptions

【职责】
- 定义所有领域层异常
- 区分业务异常和系统异常
- 提供错误码和错误信息

【设计原则】
- 异常必须有明确语义
- 异常必须可追踪
- 异常必须可恢复
"""
from typing import Optional, Dict, Any


class DomainException(Exception):
    """领域异常基类
    
    【职责】
    - 所有业务异常的基类
    - 提供错误码和错误信息
    - 支持上下文数据
    """
    
    def __init__(self, message: str, error_code: str = None, 
                 context: Dict[str, Any] = None):
        """
        Args:
            message: 错误信息
            error_code: 错误码
            context: 上下文数据
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            异常信息字典
        """
        return {
            'error_code': self.error_code,
            'message': self.message,
            'context': self.context
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} code={self.error_code} message={self.message}>"


class TaskException(DomainException):
    """任务领域异常"""
    pass


class TaskNotFoundException(TaskException):
    """任务不存在异常"""
    
    def __init__(self, task_id: str):
        super().__init__(
            message=f"任务不存在: {task_id}",
            error_code="TASK_NOT_FOUND",
            context={'task_id': task_id}
        )


class TaskStatusTransitionException(TaskException):
    """任务状态转换异常"""
    
    def __init__(self, task_id: str, from_status: str, to_status: str):
        super().__init__(
            message=f"任务状态转换非法: {from_status} -> {to_status}",
            error_code="TASK_STATUS_TRANSITION_INVALID",
            context={
                'task_id': task_id,
                'from_status': from_status,
                'to_status': to_status
            }
        )


class TaskAlreadyRunningException(TaskException):
    """任务已在运行异常"""
    
    def __init__(self, task_id: str):
        super().__init__(
            message=f"任务已在运行: {task_id}",
            error_code="TASK_ALREADY_RUNNING",
            context={'task_id': task_id}
        )


class TaskRetryExhaustedException(TaskException):
    """任务重试次数耗尽异常"""
    
    def __init__(self, task_id: str, retry_count: int, max_retries: int):
        super().__init__(
            message=f"任务重试次数耗尽: {retry_count}/{max_retries}",
            error_code="TASK_RETRY_EXHAUSTED",
            context={
                'task_id': task_id,
                'retry_count': retry_count,
                'max_retries': max_retries
            }
        )


class StationException(DomainException):
    """工位领域异常"""
    pass


class StationNotFoundException(StationException):
    """工位不存在异常"""
    
    def __init__(self, station_id: str):
        super().__init__(
            message=f"工位不存在: {station_id}",
            error_code="STATION_NOT_FOUND",
            context={'station_id': station_id}
        )


class StationOfflineException(StationException):
    """工位离线异常"""
    
    def __init__(self, station_id: str):
        super().__init__(
            message=f"工位离线: {station_id}",
            error_code="STATION_OFFLINE",
            context={'station_id': station_id}
        )


class StationBusyException(StationException):
    """工位忙碌异常"""
    
    def __init__(self, station_id: str, current_task_id: str):
        super().__init__(
            message=f"工位忙碌: {station_id}, 当前任务: {current_task_id}",
            error_code="STATION_BUSY",
            context={
                'station_id': station_id,
                'current_task_id': current_task_id
            }
        )


class DeviceException(DomainException):
    """设备领域异常"""
    pass


class DeviceNotFoundException(DeviceException):
    """设备不存在异常"""
    
    def __init__(self, device_id: str):
        super().__init__(
            message=f"设备不存在: {device_id}",
            error_code="DEVICE_NOT_FOUND",
            context={'device_id': device_id}
        )


class DeviceNotConnectedException(DeviceException):
    """设备未连接异常"""
    
    def __init__(self, device_id: str):
        super().__init__(
            message=f"设备未连接: {device_id}",
            error_code="DEVICE_NOT_CONNECTED",
            context={'device_id': device_id}
        )


class DeviceBusyException(DeviceException):
    """设备忙碌异常"""
    
    def __init__(self, device_id: str):
        super().__init__(
            message=f"设备忙碌: {device_id}",
            error_code="DEVICE_BUSY",
            context={'device_id': device_id}
        )


class ValidationException(DomainException):
    """校验异常"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            context={'field': field, 'value': value} if field else {}
        )


class ConcurrencyException(DomainException):
    """并发异常（乐观锁冲突）"""
    
    def __init__(self, entity_type: str, entity_id: str, 
                 current_version: int, expected_version: int):
        super().__init__(
            message=f"并发冲突: {entity_type}#{entity_id} version={current_version} expected={expected_version}",
            error_code="CONCURRENCY_CONFLICT",
            context={
                'entity_type': entity_type,
                'entity_id': entity_id,
                'current_version': current_version,
                'expected_version': expected_version
            }
        )
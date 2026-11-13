"""
领域枚举 - Domain Enums

【职责】
- 定义所有领域状态枚举
- 保证类型安全
- 防止魔法值

【设计原则】
- 枚举必须有明确语义
- 状态转换必须可追踪
- 枚举值不可变
"""
from enum import Enum, auto


class TaskStatus(Enum):
    """任务状态（工业核心状态机）
    
    【状态流转】
    pending -> running -> completed/failed/aborted
    
    【禁止】
    - 禁止逆流
    - 禁止跳过状态
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    
    @classmethod
    def can_transition(cls, from_status: 'TaskStatus', to_status: 'TaskStatus') -> bool:
        """检查状态转换是否合法
        
        Args:
            from_status: 当前状态
            to_status: 目标状态
            
        Returns:
            是否允许转换
        """
        valid_transitions = {
            cls.PENDING: [cls.RUNNING, cls.ABORTED],
            cls.RUNNING: [cls.COMPLETED, cls.FAILED, cls.ABORTED],
            cls.COMPLETED: [],
            cls.FAILED: [],
            cls.ABORTED: []
        }
        return to_status in valid_transitions.get(from_status, [])


class TaskResult(Enum):
    """任务结果"""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class StationStatus(Enum):
    """工位状态"""
    IDLE = "idle"
    RUNNING = "running"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class StationMode(Enum):
    """工位运行模式"""
    AUTO = "auto"
    MANUAL = "manual"


class DeviceStatus(Enum):
    """设备状态"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class DeviceConnectStatus(Enum):
    """设备连接状态"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class DeviceType(Enum):
    """设备类型"""
    ENCODER = "encoder"
    MOTOR = "motor"
    PLC = "plc"
    CAMERA = "camera"
    LASER = "laser"
    POWER_SUPPLY = "power_supply"
    DAQ = "daq"


class ProtocolType(Enum):
    """协议类型"""
    MODBUS_RTU = "modbus_rtu"
    MODBUS_TCP = "modbus_tcp"
    CANOPEN = "canopen"
    ETHERCAT = "ethercat"
    SCPI = "scpi"
    CUSTOM = "custom"


class WorkOrderStatus(Enum):
    """工单状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReportStatus(Enum):
    """报告状态"""
    DRAFT = "draft"
    GENERATED = "generated"
    ARCHIVED = "archived"


class AlarmLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventType(Enum):
    """领域事件类型"""
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_ABORTED = "task_aborted"
    TASK_RETRY = "task_retry"
    
    STATION_STATUS_CHANGED = "station_status_changed"
    DEVICE_STATUS_CHANGED = "device_status_changed"
    DEVICE_CONNECTED = "device_connected"
    DEVICE_DISCONNECTED = "device_disconnected"
    
    WORKORDER_CREATED = "workorder_created"
    WORKORDER_STARTED = "workorder_started"
    WORKORDER_COMPLETED = "workorder_completed"
    
    ALARM_RAISED = "alarm_raised"
    ALARM_CLEARED = "alarm_cleared"
    
    # Specific alarm event types
    ALARM_TRIGGERED = "alarm_triggered"
    ALARM_ACKNOWLEDGED = "alarm_acknowledged"
    ALARM_RESOLVED = "alarm_resolved"
    ALARM_CLOSED = "alarm_closed"
    
    # Report event types
    REPORT_CREATED = "report_created"
    REPORT_GENERATED = "report_generated"
    REPORT_ARCHIVED = "report_archived"
    REPORT_ATTACHMENT_ADDED = "report_attachment_added"
    REPORT_VALIDATED = "report_validated"
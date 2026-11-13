"""
设备领域 - Device Domain（资源单元）

【职责】
- 设备连接状态管理
- 设备配置管理
- 设备心跳监控
- 设备校准信息管理
- 设备运行指标管理

【核心能力】
- 连接状态
- 设备配置
- 心跳
- 校准信息
- 运行指标

【设计原则】
- Device 是聚合根
- 设备配置必须 JSONB（工业设备差异极大）
- 支持心跳监控
- 支持校准信息管理
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import time

from ..common.aggregate_root import AggregateRoot, ValueObject, generate_id
from ..common.enums import DeviceStatus, DeviceConnectStatus, DeviceType, ProtocolType, EventType
from ..common.exceptions import DeviceNotConnectedException, DeviceBusyException


@dataclass
class DeviceConfig(ValueObject):
    """设备配置（值对象）
    
    【职责】
    - 封装设备配置
    - 不可变
    
    【设计原则】
    - 使用 JSONB 存储配置
    - 工业设备差异极大，不要用 nullable 字段
    """
    protocol: str
    connection_params: Dict[str, Any] = field(default_factory=dict)
    device_params: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 5.0
    retry_count: int = 3


@dataclass
class CalibrationInfo(ValueObject):
    """校准信息（值对象）
    
    【职责】
    - 记录设备校准信息
    - 不可变
    """
    is_calibrated: bool = False
    calibrated_at: Optional[float] = None
    calibration_data: Dict[str, Any] = field(default_factory=dict)
    next_calibration_time: Optional[float] = None
    
    @property
    def is_calibration_expired(self) -> bool:
        """校准是否过期"""
        if not self.next_calibration_time:
            return False
        return time.time() > self.next_calibration_time


@dataclass
class DeviceMetrics(ValueObject):
    """设备运行指标（值对象）
    
    【职责】
    - 记录设备运行指标
    - 不可变
    """
    total_operations: int = 0
    success_operations: int = 0
    failed_operations: int = 0
    uptime_seconds: float = 0.0
    last_operation_time: Optional[float] = None
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_operations == 0:
            return 0.0
        return self.success_operations / self.total_operations


class Device(AggregateRoot):
    """设备聚合根（资源单元）
    
    【职责】
    - 管理设备连接状态
    - 管理设备配置
    - 管理设备心跳
    - 管理设备校准信息
    - 管理设备运行指标
    
    【状态流转】
    disconnected -> connecting -> connected -> disconnected
    
    【核心方法】
    - connect(): 连接设备
    - disconnect(): 断开设备
    - update_heartbeat(): 更新心跳
    - calibrate(): 校准设备
    - record_operation(): 记录操作
    
    【使用示例】
    >>> device = Device.create(
    ...     station_id=1,
    ...     code="DEV-001",
    ...     name="编码器",
    ...     device_type=DeviceType.ENCODER,
    ...     protocol=ProtocolType.MODBUS_RTU
    ... )
    >>> device.connect()
    >>> device.update_heartbeat()
    """
    
    def __init__(self, device_id: str):
        """
        Args:
            device_id: 设备ID
        """
        super().__init__(device_id)
        
        self._station_id: Optional[int] = None
        self._code: Optional[str] = None
        self._name: Optional[str] = None
        self._device_type: Optional[DeviceType] = None
        self._protocol: Optional[ProtocolType] = None
        
        self._status = DeviceStatus.IDLE
        self._connect_status = DeviceConnectStatus.DISCONNECTED
        
        self._config: Optional[DeviceConfig] = None
        self._calibration_info = CalibrationInfo()
        self._metrics = DeviceMetrics()
        
        self._last_heartbeat: Optional[float] = None
        self._heartbeat_timeout = 30.0  # 心跳超时时间（秒）
        
        self._is_busy = False
    
    @property
    def station_id(self) -> Optional[int]:
        return self._station_id
    
    @property
    def code(self) -> Optional[str]:
        return self._code
    
    @property
    def name(self) -> Optional[str]:
        return self._name
    
    @property
    def device_type(self) -> Optional[DeviceType]:
        return self._device_type
    
    @property
    def protocol(self) -> Optional[ProtocolType]:
        return self._protocol
    
    @property
    def status(self) -> DeviceStatus:
        return self._status
    
    @property
    def connect_status(self) -> DeviceConnectStatus:
        return self._connect_status
    
    @property
    def config(self) -> Optional[DeviceConfig]:
        return self._config
    
    @property
    def calibration_info(self) -> CalibrationInfo:
        return self._calibration_info
    
    @property
    def metrics(self) -> DeviceMetrics:
        return self._metrics
    
    @property
    def last_heartbeat(self) -> Optional[float]:
        return self._last_heartbeat
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connect_status == DeviceConnectStatus.CONNECTED
    
    @property
    def is_heartbeat_alive(self) -> bool:
        """心跳是否存活"""
        if not self._last_heartbeat:
            return False
        return (time.time() - self._last_heartbeat) < self._heartbeat_timeout
    
    @property
    def is_busy(self) -> bool:
        """是否忙碌"""
        return self._is_busy
    
    @classmethod
    def create(cls, station_id: int, code: str, name: str, 
               device_type: DeviceType, protocol: ProtocolType,
               config: DeviceConfig = None) -> 'Device':
        """创建设备（工厂方法）
        
        Args:
            station_id: 工位ID
            code: 设备编号
            name: 设备名称
            device_type: 设备类型
            protocol: 协议类型
            config: 设备配置
            
        Returns:
            Device实例
        """
        device_id = generate_id("DEV")
        device = cls(device_id)
        
        device._station_id = station_id
        device._code = code
        device._name = name
        device._device_type = device_type
        device._protocol = protocol
        device._config = config or DeviceConfig(protocol=protocol.value)
        
        return device
    
    def connect(self) -> None:
        """连接设备"""
        self._connect_status = DeviceConnectStatus.CONNECTING
        self._increment_version()
        
        # 模拟连接成功
        self._connect_status = DeviceConnectStatus.CONNECTED
        self._last_heartbeat = time.time()
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.DEVICE_CONNECTED,
            'aggregate_id': self._id,
            'aggregate_type': 'Device',
            'data': {'device_type': self._device_type.value}
        })
    
    def disconnect(self) -> None:
        """断开设备"""
        self._connect_status = DeviceConnectStatus.DISCONNECTED
        self._last_heartbeat = None
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.DEVICE_DISCONNECTED,
            'aggregate_id': self._id,
            'aggregate_type': 'Device',
            'data': {'device_type': self._device_type.value}
        })
    
    def update_heartbeat(self) -> None:
        """更新心跳"""
        if not self.is_connected:
            raise DeviceNotConnectedException(self._id)
        
        self._last_heartbeat = time.time()
        self._increment_version()
    
    def set_busy(self, busy: bool = True) -> None:
        """设置忙碌状态
        
        Args:
            busy: 是否忙碌
        """
        self._is_busy = busy
        self._status = DeviceStatus.BUSY if busy else DeviceStatus.IDLE
        self._increment_version()
    
    def calibrate(self, calibration_data: Dict[str, Any] = None, 
                  next_calibration_days: int = 30) -> None:
        """校准设备
        
        Args:
            calibration_data: 校准数据
            next_calibration_days: 下次校准天数
        """
        if not self.is_connected:
            raise DeviceNotConnectedException(self._id)
        
        if self._is_busy:
            raise DeviceBusyException(self._id)
        
        calibrated_at = time.time()
        next_calibration_time = calibrated_at + (next_calibration_days * 24 * 3600)
        
        self._calibration_info = CalibrationInfo(
            is_calibrated=True,
            calibrated_at=calibrated_at,
            calibration_data=calibration_data or {},
            next_calibration_time=next_calibration_time
        )
        self._increment_version()
    
    def record_operation(self, success: bool = True) -> None:
        """记录操作
        
        Args:
            success: 是否成功
        """
        self._metrics = DeviceMetrics(
            total_operations=self._metrics.total_operations + 1,
            success_operations=self._metrics.success_operations + (1 if success else 0),
            failed_operations=self._metrics.failed_operations + (0 if success else 1),
            uptime_seconds=self._metrics.uptime_seconds,
            last_operation_time=time.time()
        )
        self._increment_version()
    
    def update_config(self, config: DeviceConfig) -> None:
        """更新设备配置
        
        Args:
            config: 新配置
        """
        self._config = config
        self._increment_version()
    
    def set_error(self) -> None:
        """设置错误状态"""
        self._status = DeviceStatus.ERROR
        self._connect_status = DeviceConnectStatus.ERROR
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.DEVICE_STATUS_CHANGED,
            'aggregate_id': self._id,
            'aggregate_type': 'Device',
            'data': {'status': 'error'}
        })
    
    def recover(self) -> None:
        """恢复设备"""
        self._status = DeviceStatus.IDLE
        self._connect_status = DeviceConnectStatus.CONNECTED
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.DEVICE_STATUS_CHANGED,
            'aggregate_id': self._id,
            'aggregate_type': 'Device',
            'data': {'status': 'idle'}
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            设备信息字典
        """
        return {
            'id': self._id,
            'station_id': self._station_id,
            'code': self._code,
            'name': self._name,
            'device_type': self._device_type.value if self._device_type else None,
            'protocol': self._protocol.value if self._protocol else None,
            'status': self._status.value,
            'connect_status': self._connect_status.value,
            'config': {
                'protocol': self._config.protocol if self._config else None,
                'connection_params': self._config.connection_params if self._config else {},
                'device_params': self._config.device_params if self._config else {},
                'timeout': self._config.timeout if self._config else 5.0,
                'retry_count': self._config.retry_count if self._config else 3
            } if self._config else None,
            'calibration_info': {
                'is_calibrated': self._calibration_info.is_calibrated,
                'calibrated_at': self._calibration_info.calibrated_at,
                'calibration_data': self._calibration_info.calibration_data,
                'next_calibration_time': self._calibration_info.next_calibration_time,
                'is_calibration_expired': self._calibration_info.is_calibration_expired
            },
            'metrics': {
                'total_operations': self._metrics.total_operations,
                'success_operations': self._metrics.success_operations,
                'failed_operations': self._metrics.failed_operations,
                'uptime_seconds': self._metrics.uptime_seconds,
                'last_operation_time': self._metrics.last_operation_time,
                'success_rate': self._metrics.success_rate
            },
            'last_heartbeat': self._last_heartbeat,
            'is_connected': self.is_connected,
            'is_heartbeat_alive': self.is_heartbeat_alive,
            'is_busy': self._is_busy,
            'version': self.version,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __repr__(self) -> str:
        return f"<Device id={self._id} code={self._code} type={self._device_type.value if self._device_type else None}>"
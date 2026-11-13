"""
工位领域 - Station Domain（运行单元）

【职责】
- 工位状态管理
- 工位资源占用
- 工位设备挂载
- 当前任务管理

【核心能力】
- 工位状态
- 工位资源占用
- 工位设备挂载
- 当前任务
- 工位运行模式

【设计原则】
- Station 是聚合根
- 工位状态转换必须通过领域方法
- 支持设备挂载/卸载
- 支持任务分配/释放
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import time

from ..common.aggregate_root import AggregateRoot, ValueObject, Entity, generate_id
from ..common.enums import StationStatus, StationMode, EventType
from ..common.exceptions import (
    StationNotFoundException,
    StationOfflineException,
    StationBusyException
)
from ..common.state_machine import StationStateMachine


@dataclass
class ResourceState(ValueObject):
    """资源状态（值对象）
    
    【职责】
    - 记录工位资源占用情况
    - 不可变
    """
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    is_available: bool = True


@dataclass
class AlarmState(ValueObject):
    """告警状态（值对象）
    
    【职责】
    - 记录工位告警信息
    - 不可变
    """
    has_alarm: bool = False
    alarm_level: str = ""
    alarm_message: str = ""


@dataclass
class DeviceMount(Entity):
    """设备挂载（实体）
    
    【职责】
    - 记录设备挂载信息
    - 支持设备生命周期管理
    """
    entity_id: str
    station_id: str
    device_id: str
    device_type: str
    mount_time: float
    is_active: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        Entity.__init__(self, self.entity_id)
    
    def unmount(self):
        """卸载设备"""
        self.is_active = False


class Station(AggregateRoot):
    """工位聚合根（运行单元）
    
    【职责】
    - 管理工位状态
    - 管理设备挂载
    - 管理任务分配
    - 管理资源占用
    
    【状态流转】
    idle -> running -> error/offline
    idle -> maintenance -> idle
    
    【核心方法】
    - start(): 启动工位
    - stop(): 停止工位
    - mount_device(): 挂载设备
    - unmount_device(): 卸载设备
    - assign_task(): 分配任务
    - release_task(): 释放任务
    
    【使用示例】
    >>> station = Station.create(
    ...     code="STATION-001",
    ...     name="编码器校准工位",
    ...     line_code="LINE-001",
    ...     area_code="AREA-001"
    ... )
    >>> station.start()
    >>> station.mount_device(device_id="DEV-001", device_type="encoder")
    >>> station.assign_task(task_id="TASK-001")
    """
    
    def __init__(self, station_id: str):
        """
        Args:
            station_id: 工位ID
        """
        super().__init__(station_id)
        
        self._code: Optional[str] = None
        self._name: Optional[str] = None
        self._line_code: Optional[str] = None
        self._area_code: Optional[str] = None
        
        self._status = StationStatus.IDLE
        self._mode = StationMode.AUTO
        
        self._current_task_id: Optional[str] = None
        self._is_enabled = True
        
        self._resource_state = ResourceState()
        self._alarm_state = AlarmState()
        
        self._mounted_devices: Dict[str, DeviceMount] = {}
        
        self._state_machine = StationStateMachine(station_id)
    
    @property
    def code(self) -> Optional[str]:
        return self._code
    
    @property
    def name(self) -> Optional[str]:
        return self._name
    
    @property
    def line_code(self) -> Optional[str]:
        return self._line_code
    
    @property
    def area_code(self) -> Optional[str]:
        return self._area_code
    
    @property
    def status(self) -> StationStatus:
        return self._status
    
    @property
    def mode(self) -> StationMode:
        return self._mode
    
    @property
    def current_task_id(self) -> Optional[str]:
        return self._current_task_id
    
    @property
    def is_enabled(self) -> bool:
        return self._is_enabled
    
    @property
    def resource_state(self) -> ResourceState:
        return self._resource_state
    
    @property
    def alarm_state(self) -> AlarmState:
        return self._alarm_state
    
    @property
    def mounted_devices(self) -> List[DeviceMount]:
        """获取已挂载设备列表"""
        return [d for d in self._mounted_devices.values() if d.is_active]
    
    @classmethod
    def create(cls, code: str, name: str, line_code: str = "", 
               area_code: str = "", mode: StationMode = StationMode.AUTO) -> 'Station':
        """创建工位（工厂方法）
        
        Args:
            code: 工位编号
            name: 工位名称
            line_code: 产线编号
            area_code: 区域编号
            mode: 运行模式
            
        Returns:
            Station实例
        """
        station_id = generate_id("STATION")
        station = cls(station_id)
        
        station._code = code
        station._name = name
        station._line_code = line_code
        station._area_code = area_code
        station._mode = mode
        
        return station
    
    def start(self) -> None:
        """启动工位
        
        Raises:
            StationOfflineException: 工位离线
        """
        if not self._is_enabled:
            raise StationOfflineException(self._id)
        
        self._state_machine.start()
        self._status = StationStatus.RUNNING
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.STATION_STATUS_CHANGED,
            'aggregate_id': self._id,
            'aggregate_type': 'Station',
            'data': {'status': 'running'}
        })
    
    def stop(self) -> None:
        """停止工位"""
        self._state_machine.stop()
        self._status = StationStatus.IDLE
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.STATION_STATUS_CHANGED,
            'aggregate_id': self._id,
            'aggregate_type': 'Station',
            'data': {'status': 'idle'}
        })
    
    def error(self, error_message: str = "") -> None:
        """工位错误
        
        Args:
            error_message: 错误信息
        """
        self._state_machine.error(error_message)
        self._status = StationStatus.ERROR
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.STATION_STATUS_CHANGED,
            'aggregate_id': self._id,
            'aggregate_type': 'Station',
            'data': {'status': 'error', 'error_message': error_message}
        })
    
    def offline(self) -> None:
        """工位离线"""
        self._state_machine.offline()
        self._status = StationStatus.OFFLINE
        self._is_enabled = False
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.STATION_STATUS_CHANGED,
            'aggregate_id': self._id,
            'aggregate_type': 'Station',
            'data': {'status': 'offline'}
        })
    
    def maintenance(self) -> None:
        """工位维护"""
        self._state_machine.maintenance()
        self._status = StationStatus.MAINTENANCE
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.STATION_STATUS_CHANGED,
            'aggregate_id': self._id,
            'aggregate_type': 'Station',
            'data': {'status': 'maintenance'}
        })
    
    def recover(self) -> None:
        """工位恢复"""
        self._state_machine.recover()
        self._status = StationStatus.IDLE
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.STATION_STATUS_CHANGED,
            'aggregate_id': self._id,
            'aggregate_type': 'Station',
            'data': {'status': 'idle'}
        })
    
    def mount_device(self, device_id: str, device_type: str, 
                     config: Dict[str, Any] = None) -> None:
        """挂载设备
        
        Args:
            device_id: 设备ID
            device_type: 设备类型
            config: 设备配置
        """
        if device_id in self._mounted_devices:
            existing = self._mounted_devices[device_id]
            if existing.is_active:
                return  # 已挂载
        
        mount = DeviceMount(
            entity_id=generate_id("MOUNT"),
            station_id=self._id,
            device_id=device_id,
            device_type=device_type,
            mount_time=time.time(),
            config=config or {}
        )
        
        self._mounted_devices[device_id] = mount
        self._increment_version()
    
    def unmount_device(self, device_id: str) -> None:
        """卸载设备
        
        Args:
            device_id: 设备ID
        """
        if device_id in self._mounted_devices:
            self._mounted_devices[device_id].unmount()
            self._increment_version()
    
    def assign_task(self, task_id: str) -> None:
        """分配任务
        
        Args:
            task_id: 任务ID
            
        Raises:
            StationBusyException: 工位忙碌
        """
        if self._current_task_id:
            raise StationBusyException(self._id, self._current_task_id)
        
        self._current_task_id = task_id
        self._increment_version()
    
    def release_task(self) -> None:
        """释放任务"""
        self._current_task_id = None
        self._increment_version()
    
    def update_resource_state(self, cpu_usage: float = None, 
                              memory_usage: float = None,
                              disk_usage: float = None,
                              is_available: bool = None) -> None:
        """更新资源状态
        
        Args:
            cpu_usage: CPU使用率
            memory_usage: 内存使用率
            disk_usage: 磁盘使用率
            is_available: 是否可用
        """
        self._resource_state = ResourceState(
            cpu_usage=cpu_usage if cpu_usage is not None else self._resource_state.cpu_usage,
            memory_usage=memory_usage if memory_usage is not None else self._resource_state.memory_usage,
            disk_usage=disk_usage if disk_usage is not None else self._resource_state.disk_usage,
            is_available=is_available if is_available is not None else self._resource_state.is_available
        )
        self._increment_version()
    
    def set_alarm(self, alarm_level: str, alarm_message: str) -> None:
        """设置告警
        
        Args:
            alarm_level: 告警级别
            alarm_message: 告警信息
        """
        self._alarm_state = AlarmState(
            has_alarm=True,
            alarm_level=alarm_level,
            alarm_message=alarm_message
        )
        self._increment_version()
    
    def clear_alarm(self) -> None:
        """清除告警"""
        self._alarm_state = AlarmState()
        self._increment_version()
    
    def set_mode(self, mode: StationMode) -> None:
        """设置运行模式
        
        Args:
            mode: 运行模式
        """
        self._mode = mode
        self._increment_version()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            工位信息字典
        """
        return {
            'id': self._id,
            'code': self._code,
            'name': self._name,
            'line_code': self._line_code,
            'area_code': self._area_code,
            'status': self._status.value,
            'mode': self._mode.value,
            'current_task_id': self._current_task_id,
            'is_enabled': self._is_enabled,
            'resource_state': {
                'cpu_usage': self._resource_state.cpu_usage,
                'memory_usage': self._resource_state.memory_usage,
                'disk_usage': self._resource_state.disk_usage,
                'is_available': self._resource_state.is_available
            },
            'alarm_state': {
                'has_alarm': self._alarm_state.has_alarm,
                'alarm_level': self._alarm_state.alarm_level,
                'alarm_message': self._alarm_state.alarm_message
            },
            'mounted_devices': [
                {
                    'device_id': d.device_id,
                    'device_type': d.device_type,
                    'mount_time': d.mount_time,
                    'is_active': d.is_active
                }
                for d in self.mounted_devices
            ],
            'version': self.version,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __repr__(self) -> str:
        return f"<Station id={self._id} code={self._code} status={self._status.value}>"
"""
存储仓库 - 数据访问接口定义

【职责】
- 定义数据访问契约
- 提供领域对象持久化接口
- 实现数据访问抽象

【设计原则】
- 仅包含CRUD/Query/Transaction操作
- 不包含业务逻辑
- 保持与ORM的具体实现解耦
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...domain.task.task import Task
from ...domain.station.station import Station
from ...domain.device.device import Device
from ...domain.alarm.alarm import Alarm
from ...domain.report.report import Report


class IRepository(ABC):
    """仓储基础接口"""
    
    @abstractmethod
    def save(self, entity):
        """保存实体"""
        pass

    @abstractmethod
    def get_by_id(self, entity_id: str):
        """根据ID获取实体"""
        pass

    @abstractmethod
    def delete(self, entity_id: str):
        """删除实体"""
        pass


class ITaskRepository(IRepository):
    """任务仓储接口"""
    
    @abstractmethod
    def save(self, task: Task) -> None:
        """保存任务"""
        pass

    @abstractmethod
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """根据ID获取任务"""
        pass

    @abstractmethod
    def get_by_task_id(self, task_id: str) -> Optional[Task]:
        """根据业务ID获取任务"""
        pass

    @abstractmethod
    def get_by_workorder(self, workorder_id: str) -> List[Task]:
        """根据工单获取任务列表"""
        pass

    @abstractmethod
    def get_by_station(self, station_id: int) -> List[Task]:
        """根据工位获取任务列表"""
        pass

    @abstractmethod
    def get_by_device(self, device_id: str) -> List[Task]:
        """根据设备获取任务列表"""
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[Task]:
        """根据状态获取任务列表"""
        pass

    @abstractmethod
    def get_by_result(self, result: str) -> List[Task]:
        """根据结果获取任务列表"""
        pass

    @abstractmethod
    def get_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Task]:
        """根据时间范围获取任务"""
        pass

    @abstractmethod
    def delete(self, task_id: str) -> bool:
        """删除任务"""
        pass

    @abstractmethod
    def bulk_save(self, tasks: List[Task]) -> None:
        """批量保存任务"""
        pass


class IReportRepository(IRepository):
    """报告仓储接口"""
    
    @abstractmethod
    def save(self, report: Report) -> None:
        """保存报告"""
        pass

    @abstractmethod
    def get_by_id(self, report_id: str) -> Optional[Report]:
        """根据ID获取报告"""
        pass

    @abstractmethod
    def get_by_report_id(self, report_id: str) -> Optional[Report]:
        """根据业务ID获取报告"""
        pass

    @abstractmethod
    def get_by_task_id(self, task_id: str) -> List[Report]:
        """根据任务ID获取报告"""
        pass

    @abstractmethod
    def get_by_workorder(self, workorder_id: str) -> List[Report]:
        """根据工单获取报告列表"""
        pass

    @abstractmethod
    def get_by_sn(self, sn: str) -> List[Report]:
        """根据序列号获取报告列表"""
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[Report]:
        """根据状态获取报告列表"""
        pass

    @abstractmethod
    def get_by_result(self, result: str) -> List[Report]:
        """根据结果获取报告列表"""
        pass

    @abstractmethod
    def get_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Report]:
        """根据时间范围获取报告"""
        pass

    @abstractmethod
    def delete(self, report_id: str) -> bool:
        """删除报告"""
        pass

    @abstractmethod
    def bulk_save(self, reports: List[Report]) -> None:
        """批量保存报告"""
        pass


class IAlarmRepository(IRepository):
    """告警仓储接口"""
    
    @abstractmethod
    def save(self, alarm: Alarm) -> None:
        """保存告警"""
        pass

    @abstractmethod
    def get_by_id(self, alarm_id: str) -> Optional[Alarm]:
        """根据ID获取告警"""
        pass

    @abstractmethod
    def get_by_alarm_id(self, alarm_id: str) -> Optional[Alarm]:
        """根据业务ID获取告警"""
        pass

    @abstractmethod
    def get_by_task(self, task_id: str) -> List[Alarm]:
        """根据任务获取告警列表"""
        pass

    @abstractmethod
    def get_by_station(self, station_id: str) -> List[Alarm]:
        """根据工位获取告警列表"""
        pass

    @abstractmethod
    def get_by_device(self, device_id: str) -> List[Alarm]:
        """根据设备获取告警列表"""
        pass

    @abstractmethod
    def get_by_workorder(self, workorder_id: str) -> List[Alarm]:
        """根据工单获取告警列表"""
        pass

    @abstractmethod
    def get_by_level(self, level: str) -> List[Alarm]:
        """根据级别获取告警列表"""
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[Alarm]:
        """根据状态获取告警列表"""
        pass

    @abstractmethod
    def get_active_alarms(self) -> List[Alarm]:
        """获取活跃告警"""
        pass

    @abstractmethod
    def get_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Alarm]:
        """根据时间范围获取告警"""
        pass

    @abstractmethod
    def delete(self, alarm_id: str) -> bool:
        """删除告警"""
        pass

    @abstractmethod
    def bulk_save(self, alarms: List[Alarm]) -> None:
        """批量保存告警"""
        pass


class IStationRepository(IRepository):
    """工位仓储接口"""
    
    @abstractmethod
    def save(self, station: Station) -> None:
        """保存工位"""
        pass

    @abstractmethod
    def get_by_id(self, station_id: str) -> Optional[Station]:
        """根据ID获取工位"""
        pass

    @abstractmethod
    def get_by_station_id(self, station_id: str) -> Optional[Station]:
        """根据业务ID获取工位"""
        pass

    @abstractmethod
    def get_by_code(self, code: str) -> Optional[Station]:
        """根据代码获取工位"""
        pass

    @abstractmethod
    def get_by_line(self, line_code: str) -> List[Station]:
        """根据生产线获取工位列表"""
        pass

    @abstractmethod
    def get_by_area(self, area_code: str) -> List[Station]:
        """根据区域获取工位列表"""
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[Station]:
        """根据状态获取工位列表"""
        pass

    @abstractmethod
    def get_enabled_stations(self) -> List[Station]:
        """获取启用的工位"""
        pass

    @abstractmethod
    def delete(self, station_id: str) -> bool:
        """删除工位"""
        pass

    @abstractmethod
    def bulk_save(self, stations: List[Station]) -> None:
        """批量保存工位"""
        pass


class IDeviceRepository(IRepository):
    """设备仓储接口"""
    
    @abstractmethod
    def save(self, device: Device) -> None:
        """保存设备"""
        pass

    @abstractmethod
    def get_by_id(self, device_id: str) -> Optional[Device]:
        """根据ID获取设备"""
        pass

    @abstractmethod
    def get_by_device_id(self, device_id: str) -> Optional[Device]:
        """根据业务ID获取设备"""
        pass

    @abstractmethod
    def get_by_code(self, code: str) -> Optional[Device]:
        """根据代码获取设备"""
        pass

    @abstractmethod
    def get_by_station(self, station_id: str) -> List[Device]:
        """根据工位获取设备列表"""
        pass

    @abstractmethod
    def get_by_type(self, device_type: str) -> List[Device]:
        """根据类型获取设备列表"""
        pass

    @abstractmethod
    def get_by_protocol(self, protocol: str) -> List[Device]:
        """根据协议获取设备列表"""
        pass

    @abstractmethod
    def get_by_connect_status(self, connect_status: str) -> List[Device]:
        """根据连接状态获取设备列表"""
        pass

    @abstractmethod
    def get_connected_devices(self) -> List[Device]:
        """获取已连接设备"""
        pass

    @abstractmethod
    def get_available_devices(self) -> List[Device]:
        """获取可用设备"""
        pass

    @abstractmethod
    def delete(self, device_id: str) -> bool:
        """删除设备"""
        pass

    @abstractmethod
    def bulk_save(self, devices: List[Device]) -> None:
        """批量保存设备"""
        pass
"""
工业自动化测试平台 - 查询服务接口定义
Query Service Interfaces for Industrial Data Access
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..read_models import (
    TaskReadModel, ReportReadModel, AlarmReadModel, 
    StationReadModel, DeviceReadModel, WorkOrderReadModel,
    YieldRateData, FailDistributionData, StationPerformanceData,
    TaskTimelineData, StationHistoryData
)


class ITaskQueryService(ABC):
    """任务查询服务接口"""
    
    @abstractmethod
    def list_running_tasks(self) -> List[TaskReadModel]:
        """列出运行中的任务"""
        pass
    
    @abstractmethod
    def list_failed_tasks(self) -> List[TaskReadModel]:
        """列出失败的任务"""
        pass
    
    @abstractmethod
    def query_by_sn(self, sn: str) -> List[TaskReadModel]:
        """根据序列号查询任务"""
        pass
    
    @abstractmethod
    def query_station_history(self, station_id: int) -> List[StationHistoryData]:
        """查询工位历史"""
        pass
    
    @abstractmethod
    def query_task_timeline(self, 
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> List[TaskTimelineData]:
        """查询任务时间线"""
        pass


class IReportQueryService(ABC):
    """报告查询服务接口"""
    
    @abstractmethod
    def query_by_sn(self, sn: str) -> List[ReportReadModel]:
        """根据序列号查询报告"""
        pass
    
    @abstractmethod
    def query_by_workorder(self, workorder_id: str) -> List[ReportReadModel]:
        """根据工单查询报告"""
        pass
    
    @abstractmethod
    def query_yield_rate(self, 
                        workorder_id: Optional[str] = None,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> List[YieldRateData]:
        """查询良率"""
        pass
    
    @abstractmethod
    def query_fail_distribution(self, 
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> Dict[str, int]:
        """查询失败分布"""
        pass
    
    @abstractmethod
    def query_station_ppm(self, 
                         station_id: Optional[int] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> Dict[str, float]:
        """查询工位PPM"""
        pass


class IAlarmQueryService(ABC):
    """告警查询服务接口"""
    
    @abstractmethod
    def list_active_alarms(self) -> List[AlarmReadModel]:
        """列出活跃告警"""
        pass
    
    @abstractmethod
    def query_by_station(self, station_id: int) -> List[AlarmReadModel]:
        """根据工位查询告警"""
        pass
    
    @abstractmethod
    def query_by_device(self, device_id: str) -> List[AlarmReadModel]:
        """根据设备查询告警"""
        pass
    
    @abstractmethod
    def query_by_severity(self, severity: str) -> List[AlarmReadModel]:
        """根据严重程度查询告警"""
        pass
    
    @abstractmethod
    def query_by_time_range(self, 
                           start_time: datetime, 
                           end_time: datetime) -> List[AlarmReadModel]:
        """根据时间范围查询告警"""
        pass


class IStationQueryService(ABC):
    """工位查询服务接口"""
    
    @abstractmethod
    def get_station_by_id(self, station_id: int) -> Optional[StationReadModel]:
        """根据ID获取工位"""
        pass
    
    @abstractmethod
    def get_stations_by_status(self, status: str) -> List[StationReadModel]:
        """根据状态获取工位"""
        pass
    
    @abstractmethod
    def get_station_performance(self, 
                               station_id: int,
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> StationPerformanceData:
        """获取工位性能数据"""
        pass


class IDeviceQueryService(ABC):
    """设备查询服务接口"""
    
    @abstractmethod
    def get_device_by_id(self, device_id: str) -> Optional[DeviceReadModel]:
        """根据ID获取设备"""
        pass
    
    @abstractmethod
    def get_devices_by_type(self, device_type: str) -> List[DeviceReadModel]:
        """根据类型获取设备"""
        pass
    
    @abstractmethod
    def get_devices_by_station(self, station_id: int) -> List[DeviceReadModel]:
        """根据工位获取设备"""
        pass


class IWorkOrderQueryService(ABC):
    """工单查询服务接口"""
    
    @abstractmethod
    def get_active_workorders(self) -> List[WorkOrderReadModel]:
        """获取活跃工单"""
        pass
    
    @abstractmethod
    def get_workorder_by_id(self, workorder_id: str) -> Optional[WorkOrderReadModel]:
        """根据ID获取工单"""
        pass
    
    @abstractmethod
    def get_workorder_progress(self, workorder_id: str) -> Dict[str, Any]:
        """获取工单进度"""
        pass
    
    @abstractmethod
    def get_workorder_statistics(self,
                                start_time: Optional[datetime] = None,
                                end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """获取工单统计"""
        pass


class IDashboardQueryService(ABC):
    """仪表板查询服务接口"""
    
    @abstractmethod
    def get_production_summary(self) -> Dict[str, Any]:
        """获取生产汇总"""
        pass
    
    @abstractmethod
    def get_quality_metrics(self) -> Dict[str, float]:
        """获取质量指标"""
        pass
    
    @abstractmethod
    def get_system_health(self) -> Dict[str, Any]:
        """获取系统健康状态"""
        pass
    
    @abstractmethod
    def get_recent_alarms(self, limit: int = 10) -> List[AlarmReadModel]:
        """获取最近告警"""
        pass
    
    @abstractmethod
    def get_station_utilization(self) -> Dict[str, float]:
        """获取工位利用率"""
        pass
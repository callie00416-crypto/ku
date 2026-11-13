"""
工业自动化测试平台 - 查询服务实现
Query Service Implementations for Industrial Data Access
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, case, cast, Float
from ..models import (
    TaskModel, ReportModel, AlarmModel, 
    StationModel, DeviceModel, WorkOrderModel
)
from ..read_models import (
    TaskReadModel, ReportReadModel, AlarmReadModel,
    StationReadModel, DeviceReadModel, WorkOrderReadModel,
    YieldRateData, FailDistributionData, StationPerformanceData,
    TaskTimelineData, StationHistoryData
)
from . import (
    ITaskQueryService, IReportQueryService, IAlarmQueryService,
    IStationQueryService, IDeviceQueryService, IWorkOrderQueryService,
    IDashboardQueryService
)


class TaskQueryService(ITaskQueryService):
    """任务查询服务实现"""
    
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
    
    def list_running_tasks(self) -> List[TaskReadModel]:
        """列出运行中的任务"""
        with self.session_factory() as session:
            tasks = session.query(TaskModel).filter(
                TaskModel.status.in_(['RUNNING', 'PENDING'])
            ).all()
            return [
                TaskReadModel(
                    id=task.id,
                    task_id=task.task_id,
                    workorder_id=task.workorder_id,
                    station_id=task.station_id,
                    device_id=task.device_id,
                    sn=task.sn,
                    task_type=task.task_type,
                    priority=task.priority,
                    status=task.status,
                    result=task.result,
                    error_code=task.error_code,
                    error_message=task.error_message,
                    retry_count=task.retry_count,
                    actor_id=task.actor_id,
                    started_at=task.started_at,
                    completed_at=task.completed_at,
                    duration_ms=task.duration_ms,
                    metrics=task.metrics,
                    trace_id=task.trace_id,
                    correlation_id=task.correlation_id,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                    version=task.version
                )
                for task in tasks
            ]
    
    def list_failed_tasks(self) -> List[TaskReadModel]:
        """列出失败的任务"""
        with self.session_factory() as session:
            tasks = session.query(TaskModel).filter(
                TaskModel.status == 'FAILED'
            ).all()
            return [
                TaskReadModel(
                    id=task.id,
                    task_id=task.task_id,
                    workorder_id=task.workorder_id,
                    station_id=task.station_id,
                    device_id=task.device_id,
                    sn=task.sn,
                    task_type=task.task_type,
                    priority=task.priority,
                    status=task.status,
                    result=task.result,
                    error_code=task.error_code,
                    error_message=task.error_message,
                    retry_count=task.retry_count,
                    actor_id=task.actor_id,
                    started_at=task.started_at,
                    completed_at=task.completed_at,
                    duration_ms=task.duration_ms,
                    metrics=task.metrics,
                    trace_id=task.trace_id,
                    correlation_id=task.correlation_id,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                    version=task.version
                )
                for task in tasks
            ]
    
    def query_by_sn(self, sn: str) -> List[TaskReadModel]:
        """根据序列号查询任务"""
        with self.session_factory() as session:
            tasks = session.query(TaskModel).filter(
                TaskModel.sn == sn
            ).all()
            return [
                TaskReadModel(
                    id=task.id,
                    task_id=task.task_id,
                    workorder_id=task.workorder_id,
                    station_id=task.station_id,
                    device_id=task.device_id,
                    sn=task.sn,
                    task_type=task.task_type,
                    priority=task.priority,
                    status=task.status,
                    result=task.result,
                    error_code=task.error_code,
                    error_message=task.error_message,
                    retry_count=task.retry_count,
                    actor_id=task.actor_id,
                    started_at=task.started_at,
                    completed_at=task.completed_at,
                    duration_ms=task.duration_ms,
                    metrics=task.metrics,
                    trace_id=task.trace_id,
                    correlation_id=task.correlation_id,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                    version=task.version
                )
                for task in tasks
            ]
    
    def query_station_history(self, station_id: int) -> List[StationHistoryData]:
        """查询工位历史"""
        with self.session_factory() as session:
            tasks = session.query(TaskModel).filter(
                TaskModel.station_id == station_id
            ).order_by(TaskModel.created_at.desc()).all()
            return [
                StationHistoryData(
                    station_id=str(task.station_id),
                    task_id=task.task_id,
                    sn=task.sn or "",
                    result=task.result,
                    started_at=task.started_at,
                    completed_at=task.completed_at,
                    duration_ms=task.duration_ms or 0,
                    created_at=task.created_at
                )
                for task in tasks
            ]
    
    def query_task_timeline(self, 
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> List[TaskTimelineData]:
        """查询任务时间线"""
        with self.session_factory() as session:
            query = session.query(TaskModel)
            if start_time:
                query = query.filter(TaskModel.created_at >= start_time)
            if end_time:
                query = query.filter(TaskModel.created_at <= end_time)
            
            tasks = query.order_by(TaskModel.created_at).all()
            return [
                TaskTimelineData(
                    task_id=task.task_id,
                    sn=task.sn or "",
                    status=task.status,
                    started_at=task.started_at,
                    completed_at=task.completed_at,
                    duration_ms=task.duration_ms,
                    station_id=task.station_id
                )
                for task in tasks
            ]


class ReportQueryService(IReportQueryService):
    """报告查询服务实现"""
    
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
    
    def query_by_sn(self, sn: str) -> List[ReportReadModel]:
        """根据序列号查询报告"""
        with self.session_factory() as session:
            reports = session.query(ReportModel).filter(
                ReportModel.sn == sn
            ).all()
            return [
                ReportReadModel(
                    id=report.id,
                    report_id=report.report_id,
                    task_id=report.task_id,
                    workorder_id=report.workorder_id,
                    sn=report.sn,
                    station_id=report.station_id,
                    device_id=report.device_id,
                    result=report.result,
                    detail=report.detail,
                    report_snapshot=report.report_snapshot,
                    attachments=report.attachments,
                    created_at=report.created_at,
                    updated_at=report.updated_at,
                    version=report.version
                )
                for report in reports
            ]
    
    def query_by_workorder(self, workorder_id: str) -> List[ReportReadModel]:
        """根据工单查询报告"""
        with self.session_factory() as session:
            reports = session.query(ReportModel).filter(
                ReportModel.workorder_id == workorder_id
            ).all()
            return [
                ReportReadModel(
                    id=report.id,
                    report_id=report.report_id,
                    task_id=report.task_id,
                    workorder_id=report.workorder_id,
                    sn=report.sn,
                    station_id=report.station_id,
                    device_id=report.device_id,
                    result=report.result,
                    detail=report.detail,
                    report_snapshot=report.report_snapshot,
                    attachments=report.attachments,
                    created_at=report.created_at,
                    updated_at=report.updated_at,
                    version=report.version
                )
                for report in reports
            ]
    
    def query_yield_rate(self, 
                        workorder_id: Optional[str] = None,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> List[YieldRateData]:
        """查询良率"""
        with self.session_factory() as session:
            query = session.query(
                ReportModel.workorder_id,
                func.count(ReportModel.id).label('total_count'),
                func.sum(case((ReportModel.result == 'PASS', 1), else_=0)).label('pass_count'),
                func.sum(case((ReportModel.result == 'FAIL', 1), else_=0)).label('fail_count')
            ).group_by(ReportModel.workorder_id)
            
            if workorder_id:
                query = query.filter(ReportModel.workorder_id == workorder_id)
            if start_time:
                query = query.filter(ReportModel.created_at >= start_time)
            if end_time:
                query = query.filter(ReportModel.created_at <= end_time)
            
            results = query.all()
            yield_rates = []
            
            for row in results:
                total = row.total_count or 0
                pass_count = row.pass_count or 0
                fail_count = row.fail_count or 0
                yield_rate = (pass_count / total * 100) if total > 0 else 0.0
                
                yield_rates.append(YieldRateData(
                    workorder_id=row.workorder_id,
                    total_count=total,
                    pass_count=pass_count,
                    fail_count=fail_count,
                    yield_rate=yield_rate,
                    calculated_at=datetime.now()
                ))
            
            return yield_rates
    
    def query_fail_distribution(self, 
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> Dict[str, int]:
        """查询失败分布"""
        with self.session_factory() as session:
            query = session.query(
                TaskModel.error_code,
                TaskModel.error_message,
                func.count(TaskModel.id).label('count')
            ).filter(TaskModel.result == 'FAIL').group_by(
                TaskModel.error_code, TaskModel.error_message
            )
            
            if start_time:
                query = query.filter(TaskModel.created_at >= start_time)
            if end_time:
                query = query.filter(TaskModel.created_at <= end_time)
            
            results = query.all()
            fail_distribution = {}
            
            for row in results:
                error_key = f"{row.error_code}: {row.error_message}" if row.error_code else row.error_message or "Unknown Error"
                fail_distribution[error_key] = row.count
            
            return fail_distribution
    
    def query_station_ppm(self, 
                         station_id: Optional[int] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> Dict[str, float]:
        """查询工位PPM（百万分之缺陷数）"""
        with self.session_factory() as session:
            query = session.query(
                ReportModel.station_id,
                func.count(ReportModel.id).label('total_count'),
                func.sum(case((ReportModel.result == 'FAIL', 1), else_=0)).label('fail_count')
            ).group_by(ReportModel.station_id)
            
            if station_id:
                query = query.filter(ReportModel.station_id == station_id)
            if start_time:
                query = query.filter(ReportModel.created_at >= start_time)
            if end_time:
                query = query.filter(ReportModel.created_at <= end_time)
            
            results = query.all()
            ppm_data = {}
            
            for row in results:
                station_key = f"station_{row.station_id}"
                total = row.total_count or 0
                fail_count = row.fail_count or 0
                ppm = (fail_count / total * 1000000) if total > 0 else 0.0
                ppm_data[station_key] = ppm
            
            return ppm_data


class AlarmQueryService(IAlarmQueryService):
    """告警查询服务实现"""
    
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
    
    def list_active_alarms(self) -> List[AlarmReadModel]:
        """列出活跃告警"""
        with self.session_factory() as session:
            alarms = session.query(AlarmModel).filter(
                AlarmModel.status == 'ACTIVE'
            ).all()
            return [
                AlarmReadModel(
                    id=alarm.id,
                    alarm_id=alarm.alarm_id,
                    station_id=alarm.station_id,
                    device_id=alarm.device_id,
                    alarm_type=alarm.alarm_type,
                    severity=alarm.severity,
                    title=alarm.title,
                    description=alarm.description,
                    status=alarm.status,
                    dedup_key=alarm.dedup_key,
                    resolved_by=alarm.resolved_by,
                    resolved_at=alarm.resolved_at,
                    created_at=alarm.created_at,
                    updated_at=alarm.updated_at,
                    version=alarm.version
                )
                for alarm in alarms
            ]
    
    def query_by_station(self, station_id: int) -> List[AlarmReadModel]:
        """根据工位查询告警"""
        with self.session_factory() as session:
            alarms = session.query(AlarmModel).filter(
                AlarmModel.station_id == station_id
            ).all()
            return [
                AlarmReadModel(
                    id=alarm.id,
                    alarm_id=alarm.alarm_id,
                    station_id=alarm.station_id,
                    device_id=alarm.device_id,
                    alarm_type=alarm.alarm_type,
                    severity=alarm.severity,
                    title=alarm.title,
                    description=alarm.description,
                    status=alarm.status,
                    dedup_key=alarm.dedup_key,
                    resolved_by=alarm.resolved_by,
                    resolved_at=alarm.resolved_at,
                    created_at=alarm.created_at,
                    updated_at=alarm.updated_at,
                    version=alarm.version
                )
                for alarm in alarms
            ]
    
    def query_by_device(self, device_id: str) -> List[AlarmReadModel]:
        """根据设备查询告警"""
        with self.session_factory() as session:
            alarms = session.query(AlarmModel).filter(
                AlarmModel.device_id == device_id
            ).all()
            return [
                AlarmReadModel(
                    id=alarm.id,
                    alarm_id=alarm.alarm_id,
                    station_id=alarm.station_id,
                    device_id=alarm.device_id,
                    alarm_type=alarm.alarm_type,
                    severity=alarm.severity,
                    title=alarm.title,
                    description=alarm.description,
                    status=alarm.status,
                    dedup_key=alarm.dedup_key,
                    resolved_by=alarm.resolved_by,
                    resolved_at=alarm.resolved_at,
                    created_at=alarm.created_at,
                    updated_at=alarm.updated_at,
                    version=alarm.version
                )
                for alarm in alarms
            ]
    
    def query_by_severity(self, severity: str) -> List[AlarmReadModel]:
        """根据严重程度查询告警"""
        with self.session_factory() as session:
            alarms = session.query(AlarmModel).filter(
                AlarmModel.severity == severity
            ).all()
            return [
                AlarmReadModel(
                    id=alarm.id,
                    alarm_id=alarm.alarm_id,
                    station_id=alarm.station_id,
                    device_id=alarm.device_id,
                    alarm_type=alarm.alarm_type,
                    severity=alarm.severity,
                    title=alarm.title,
                    description=alarm.description,
                    status=alarm.status,
                    dedup_key=alarm.dedup_key,
                    resolved_by=alarm.resolved_by,
                    resolved_at=alarm.resolved_at,
                    created_at=alarm.created_at,
                    updated_at=alarm.updated_at,
                    version=alarm.version
                )
                for alarm in alarms
            ]
    
    def query_by_time_range(self, 
                           start_time: datetime, 
                           end_time: datetime) -> List[AlarmReadModel]:
        """根据时间范围查询告警"""
        with self.session_factory() as session:
            alarms = session.query(AlarmModel).filter(
                AlarmModel.created_at >= start_time,
                AlarmModel.created_at <= end_time
            ).all()
            return [
                AlarmReadModel(
                    id=alarm.id,
                    alarm_id=alarm.alarm_id,
                    station_id=alarm.station_id,
                    device_id=alarm.device_id,
                    alarm_type=alarm.alarm_type,
                    severity=alarm.severity,
                    title=alarm.title,
                    description=alarm.description,
                    status=alarm.status,
                    dedup_key=alarm.dedup_key,
                    resolved_by=alarm.resolved_by,
                    resolved_at=alarm.resolved_at,
                    created_at=alarm.created_at,
                    updated_at=alarm.updated_at,
                    version=alarm.version
                )
                for alarm in alarms
            ]


class StationQueryService(IStationQueryService):
    """工位查询服务实现"""
    
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
    
    def get_station_by_id(self, station_id: int) -> Optional[StationReadModel]:
        """根据ID获取工位"""
        with self.session_factory() as session:
            station = session.query(StationModel).filter(
                StationModel.id == station_id
            ).first()
            if station:
                return StationReadModel(
                    id=station.id,
                    station_id=station.station_id,
                    name=station.name,
                    location=station.location,
                    status=station.status,
                    config=station.config,
                    last_heartbeat=station.last_heartbeat,
                    created_at=station.created_at,
                    updated_at=station.updated_at,
                    version=station.version
                )
            return None
    
    def get_stations_by_status(self, status: str) -> List[StationReadModel]:
        """根据状态获取工位"""
        with self.session_factory() as session:
            stations = session.query(StationModel).filter(
                StationModel.status == status
            ).all()
            return [
                StationReadModel(
                    id=station.id,
                    station_id=station.station_id,
                    name=station.name,
                    location=station.location,
                    status=station.status,
                    config=station.config,
                    last_heartbeat=station.last_heartbeat,
                    created_at=station.created_at,
                    updated_at=station.updated_at,
                    version=station.version
                )
                for station in stations
            ]
    
    def get_station_performance(self, 
                               station_id: int,
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> StationPerformanceData:
        """获取工位性能数据"""
        with self.session_factory() as session:
            # 查询任务统计数据
            task_query = session.query(
                func.count(TaskModel.id).label('total_tasks'),
                func.sum(case((TaskModel.status == 'COMPLETED', 1), else_=0)).label('completed_tasks'),
                func.sum(case((TaskModel.status == 'FAILED', 1), else_=0)).label('failed_tasks'),
                func.avg(cast(TaskModel.duration_ms, Float)).label('avg_duration_ms')
            ).filter(TaskModel.station_id == station_id)
            
            if start_time:
                task_query = task_query.filter(TaskModel.created_at >= start_time)
            if end_time:
                task_query = task_query.filter(TaskModel.created_at <= end_time)
            
            task_stats = task_query.first()
            
            # 这里简化计算uptime和downtime，实际可能需要更复杂的逻辑
            uptime_hours = 24.0  # 示例值
            downtime_hours = 0.0  # 示例值
            
            return StationPerformanceData(
                station_id=str(station_id),
                total_tasks=task_stats.total_tasks or 0,
                completed_tasks=task_stats.completed_tasks or 0,
                failed_tasks=task_stats.failed_tasks or 0,
                avg_duration_ms=task_stats.avg_duration_ms or 0.0,
                uptime_hours=uptime_hours,
                downtime_hours=downtime_hours,
                calculated_at=datetime.now()
            )


class DeviceQueryService(IDeviceQueryService):
    """设备查询服务实现"""
    
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
    
    def get_device_by_id(self, device_id: str) -> Optional[DeviceReadModel]:
        """根据ID获取设备"""
        with self.session_factory() as session:
            device = session.query(DeviceModel).filter(
                DeviceModel.device_id == device_id
            ).first()
            if device:
                return DeviceReadModel(
                    id=device.id,
                    device_id=device.device_id,
                    name=device.name,
                    device_type=device.device_type,
                    station_id=device.station_id,
                    ip_address=device.ip_address,
                    port=device.port,
                    status=device.status,
                    connection_info=device.connection_info,
                    config=device.config,
                    health_status=device.health_status,
                    last_heartbeat=device.last_heartbeat,
                    created_at=device.created_at,
                    updated_at=device.updated_at,
                    version=device.version
                )
            return None
    
    def get_devices_by_type(self, device_type: str) -> List[DeviceReadModel]:
        """根据类型获取设备"""
        with self.session_factory() as session:
            devices = session.query(DeviceModel).filter(
                DeviceModel.device_type == device_type
            ).all()
            return [
                DeviceReadModel(
                    id=device.id,
                    device_id=device.device_id,
                    name=device.name,
                    device_type=device.device_type,
                    station_id=device.station_id,
                    ip_address=device.ip_address,
                    port=device.port,
                    status=device.status,
                    connection_info=device.connection_info,
                    config=device.config,
                    health_status=device.health_status,
                    last_heartbeat=device.last_heartbeat,
                    created_at=device.created_at,
                    updated_at=device.updated_at,
                    version=device.version
                )
                for device in devices
            ]
    
    def get_devices_by_station(self, station_id: int) -> List[DeviceReadModel]:
        """根据工位获取设备"""
        with self.session_factory() as session:
            devices = session.query(DeviceModel).filter(
                DeviceModel.station_id == station_id
            ).all()
            return [
                DeviceReadModel(
                    id=device.id,
                    device_id=device.device_id,
                    name=device.name,
                    device_type=device.device_type,
                    station_id=device.station_id,
                    ip_address=device.ip_address,
                    port=device.port,
                    status=device.status,
                    connection_info=device.connection_info,
                    config=device.config,
                    health_status=device.health_status,
                    last_heartbeat=device.last_heartbeat,
                    created_at=device.created_at,
                    updated_at=device.updated_at,
                    version=device.version
                )
                for device in devices
            ]


class WorkOrderQueryService(IWorkOrderQueryService):
    """工单查询服务实现"""
    
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
    
    def get_active_workorders(self) -> List[WorkOrderReadModel]:
        """获取活跃工单"""
        with self.session_factory() as session:
            workorders = session.query(WorkOrderModel).filter(
                WorkOrderModel.status.in_(['PENDING', 'RUNNING', 'PAUSED'])
            ).all()
            return [
                WorkOrderReadModel(
                    id=workorder.id,
                    workorder_id=workorder.workorder_id,
                    product_model=workorder.product_model,
                    batch_number=workorder.batch_number,
                    planned_quantity=workorder.planned_quantity or 0,
                    completed_quantity=workorder.completed_quantity or 0,
                    ng_quantity=workorder.ng_quantity or 0,
                    route_config=workorder.route_config,
                    priority=workorder.priority or 0,
                    status=workorder.status,
                    start_time=workorder.start_time,
                    end_time=workorder.end_time,
                    created_at=workorder.created_at,
                    updated_at=workorder.updated_at,
                    version=workorder.version
                )
                for workorder in workorders
            ]
    
    def get_workorder_by_id(self, workorder_id: str) -> Optional[WorkOrderReadModel]:
        """根据ID获取工单"""
        with self.session_factory() as session:
            workorder = session.query(WorkOrderModel).filter(
                WorkOrderModel.workorder_id == workorder_id
            ).first()
            if workorder:
                return WorkOrderReadModel(
                    id=workorder.id,
                    workorder_id=workorder.workorder_id,
                    product_model=workorder.product_model,
                    batch_number=workorder.batch_number,
                    planned_quantity=workorder.planned_quantity or 0,
                    completed_quantity=workorder.completed_quantity or 0,
                    ng_quantity=workorder.ng_quantity or 0,
                    route_config=workorder.route_config,
                    priority=workorder.priority or 0,
                    status=workorder.status,
                    start_time=workorder.start_time,
                    end_time=workorder.end_time,
                    created_at=workorder.created_at,
                    updated_at=workorder.updated_at,
                    version=workorder.version
                )
            return None
    
    def get_workorder_progress(self, workorder_id: str) -> Dict[str, Any]:
        """获取工单进度"""
        with self.session_factory() as session:
            workorder = session.query(WorkOrderModel).filter(
                WorkOrderModel.workorder_id == workorder_id
            ).first()
            
            if not workorder:
                return {}
            
            # 获取相关任务统计
            task_stats = session.query(
                func.count(TaskModel.id).label('total_tasks'),
                func.sum(case((TaskModel.status == 'COMPLETED', 1), else_=0)).label('completed_tasks'),
                func.sum(case((TaskModel.status == 'FAILED', 1), else_=0)).label('failed_tasks')
            ).filter(
                TaskModel.workorder_id == workorder_id
            ).first()
            
            # 获取相关报告统计
            report_stats = session.query(
                func.count(ReportModel.id).label('total_reports'),
                func.sum(case((ReportModel.result == 'PASS', 1), else_=0)).label('pass_reports'),
                func.sum(case((ReportModel.result == 'FAIL', 1), else_=0)).label('fail_reports')
            ).filter(
                ReportModel.workorder_id == workorder_id
            ).first()
            
            planned = workorder.planned_quantity or 0
            completed = workorder.completed_quantity or 0
            ng = workorder.ng_quantity or 0
            
            progress_percentage = (completed / planned * 100) if planned > 0 else 0.0
            yield_rate = ((completed - ng) / completed * 100) if completed > 0 else 0.0
            
            return {
                'workorder_id': workorder_id,
                'planned_quantity': planned,
                'completed_quantity': completed,
                'ng_quantity': ng,
                'progress_percentage': progress_percentage,
                'yield_rate': yield_rate,
                'task_stats': {
                    'total': task_stats.total_tasks or 0,
                    'completed': task_stats.completed_tasks or 0,
                    'failed': task_stats.failed_tasks or 0
                },
                'report_stats': {
                    'total': report_stats.total_reports or 0,
                    'passed': report_stats.pass_reports or 0,
                    'failed': report_stats.fail_reports or 0
                }
            }
    
    def get_workorder_statistics(self,
                                start_time: Optional[datetime] = None,
                                end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """获取工单统计"""
        with self.session_factory() as session:
            query = session.query(WorkOrderModel)
            
            if start_time:
                query = query.filter(WorkOrderModel.created_at >= start_time)
            if end_time:
                query = query.filter(WorkOrderModel.created_at <= end_time)
            
            workorders = query.all()
            
            total_workorders = len(workorders)
            status_counts = {}
            product_models = set()
            
            for workorder in workorders:
                status = workorder.status
                status_counts[status] = status_counts.get(status, 0) + 1
                product_models.add(workorder.product_model)
            
            return {
                'total_workorders': total_workorders,
                'status_distribution': status_counts,
                'unique_product_models': len(product_models),
                'active_workorders': status_counts.get('RUNNING', 0) + status_counts.get('PENDING', 0),
                'completed_workorders': status_counts.get('COMPLETED', 0)
            }


class DashboardQueryService(IDashboardQueryService):
    """仪表板查询服务实现"""
    
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
    
    def get_production_summary(self) -> Dict[str, Any]:
        """获取生产汇总"""
        with self.session_factory() as session:
            # 获取当前活跃工单数量
            active_workorders = session.query(func.count(WorkOrderModel.id)).filter(
                WorkOrderModel.status.in_(['PENDING', 'RUNNING'])
            ).scalar()
            
            # 获取今日任务总数
            from datetime import date
            today = date.today()
            today_tasks = session.query(func.count(TaskModel.id)).filter(
                func.date(TaskModel.created_at) == today
            ).scalar()
            
            # 获取今日完成任务数
            completed_today = session.query(func.count(TaskModel.id)).filter(
                func.date(TaskModel.created_at) == today,
                TaskModel.status == 'COMPLETED'
            ).scalar()
            
            # 获取今日失败任务数
            failed_today = session.query(func.count(TaskModel.id)).filter(
                func.date(TaskModel.created_at) == today,
                TaskModel.status == 'FAILED'
            ).scalar()
            
            return {
                'active_workorders': active_workorders or 0,
                'today_total_tasks': today_tasks or 0,
                'today_completed_tasks': completed_today or 0,
                'today_failed_tasks': failed_today or 0,
                'completion_rate': ((completed_today or 0) / (today_tasks or 1) * 100)
            }
    
    def get_quality_metrics(self) -> Dict[str, float]:
        """获取质量指标"""
        with self.session_factory() as session:
            # 获取总的通过/失败报告数
            total_reports = session.query(func.count(ReportModel.id)).scalar()
            pass_reports = session.query(func.count(ReportModel.id)).filter(
                ReportModel.result == 'PASS'
            ).scalar()
            fail_reports = session.query(func.count(ReportModel.id)).filter(
                ReportModel.result == 'FAIL'
            ).scalar()
            
            # 计算良率
            yield_rate = (pass_reports or 0) / (total_reports or 1) * 100
            
            return {
                'yield_rate': round(yield_rate, 2),
                'total_reports': total_reports or 0,
                'pass_reports': pass_reports or 0,
                'fail_reports': fail_reports or 0,
                'defect_rate': round(100 - yield_rate, 2)
            }
    
    def get_system_health(self) -> Dict[str, Any]:
        """获取系统健康状态"""
        with self.session_factory() as session:
            # 获取活跃告警数
            active_alarms = session.query(func.count(AlarmModel.id)).filter(
                AlarmModel.status == 'ACTIVE'
            ).scalar()
            
            # 获取离线设备数
            offline_devices = session.query(func.count(DeviceModel.id)).filter(
                DeviceModel.status == 'OFFLINE'
            ).scalar()
            
            # 获取工位状态统计
            station_stats = session.query(
                StationModel.status,
                func.count(StationModel.id)
            ).group_by(StationModel.status).all()
            
            station_status = {}
            for status, count in station_stats:
                station_status[status] = count
            
            return {
                'active_alarms': active_alarms or 0,
                'offline_devices': offline_devices or 0,
                'station_status': station_status,
                'is_healthy': (active_alarms or 0) == 0 and (offline_devices or 0) == 0
            }
    
    def get_recent_alarms(self, limit: int = 10) -> List[AlarmReadModel]:
        """获取最近告警"""
        with self.session_factory() as session:
            alarms = session.query(AlarmModel).order_by(
                AlarmModel.created_at.desc()
            ).limit(limit).all()
            return [
                AlarmReadModel(
                    id=alarm.id,
                    alarm_id=alarm.alarm_id,
                    station_id=alarm.station_id,
                    device_id=alarm.device_id,
                    alarm_type=alarm.alarm_type,
                    severity=alarm.severity,
                    title=alarm.title,
                    description=alarm.description,
                    status=alarm.status,
                    dedup_key=alarm.dedup_key,
                    resolved_by=alarm.resolved_by,
                    resolved_at=alarm.resolved_at,
                    created_at=alarm.created_at,
                    updated_at=alarm.updated_at,
                    version=alarm.version
                )
                for alarm in alarms
            ]
    
    def get_station_utilization(self) -> Dict[str, float]:
        """获取工位利用率"""
        with self.session_factory() as session:
            # 获取每个工位的任务数
            station_tasks = session.query(
                TaskModel.station_id,
                func.count(TaskModel.id).label('task_count')
            ).group_by(TaskModel.station_id).all()
            
            # 简化的利用率计算（实际可能需要更复杂的计算方式）
            utilization = {}
            for station_id, task_count in station_tasks:
                # 假设基于任务数量来估算利用率
                # 实际应用中可能需要考虑更多因素
                station_key = f"station_{station_id}" if station_id is not None else "station_unknown"
                utilization[station_key] = min(task_count * 10, 100.0)  # 简化的计算
            
            return utilization
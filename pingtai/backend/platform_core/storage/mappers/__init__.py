"""
存储映射器 - 领域对象与ORM实体映射

【职责】
- 领域对象 ↔ ORM实体转换
- 数据格式适配
- 防腐层实现

【设计原则】
- 保持领域模型纯净
- 适配数据库结构
- 避免ORM污染领域层
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from decimal import Decimal

from ...domain.task.task import Task, TaskMetrics, RuntimeSession, TaskFlow
from ...domain.station.station import Station, ResourceState, AlarmState, DeviceMount
from ...domain.device.device import Device, DeviceMetrics
from ...domain.alarm.alarm import Alarm, AlarmLevel, AlarmStatus
from ...domain.report.report import (
    Report, ReportMetrics, DeviceSnapshot, TaskSnapshot, StationSnapshot,
    TestRecord, AlarmSnapshot, SoftwareVersion, OperatorInfo
)
from ...domain.report.enums import ReportStatus, ReportType, ReportFormat, RecordValueType
from ...domain.common.enums import TaskResult, TaskStatus, AlarmLevel as CommonAlarmLevel
from ...domain.alarm.enums import AlarmLevel as AlarmLevelEnum, AlarmStatus as CommonAlarmStatus, AlarmStatus as AlarmStatusEnum
from ..models import (
    TaskModel, ReportModel, AlarmModel, StationModel, DeviceModel,
    TestRecordModel, ReportAttachmentModel
)


class TaskMapper:
    """任务映射器"""
    
    @staticmethod
    def to_entity(task_model: TaskModel) -> Task:
        """ORM实体转领域对象"""
        task = Task(
            task_id=task_model.task_id,
            workorder_id=task_model.workorder_id,
            station_id=task_model.station_id,
            device_id=task_model.device_id,
            sn=task_model.sn,
            task_type=task_model.task_type,
            priority=task_model.priority,
            max_retries=task_model.max_retries
        )
        
        # 恢复状态和结果
        task._status = TaskStatus(task_model.status)
        if task_model.result:
            task._result = TaskResult(task_model.result)
        task._error_code = task_model.error_code
        task._error_message = task_model.error_message
        task._retry_count = task_model.retry_count
        task._actor_id = task_model.actor_id
        
        # 恢复时间信息
        if task_model.start_time:
            task._start_time = task_model.start_time.timestamp()
        if task_model.end_time:
            task._end_time = task_model.end_time.timestamp()
        if task_model.duration_ms:
            task._duration_ms = task_model.duration_ms
            
        # 恢复指标和元数据
        task._metrics = TaskMetrics(**(task_model.metrics or {}))
        task._metadata = task_model.extra_metadata or {}
        
        # 恢复版本
        task._version = task_model.version
        
        return task
    
    @staticmethod
    def to_model(task: Task) -> TaskModel:
        """领域对象转ORM实体"""
        task_model = TaskModel(
            id=task.id,
            task_id=task.id,
            workorder_id=task.workorder_id,
            station_id=task.station_id,
            device_id=task.device_id,
            sn=task.sn,
            task_type=task.task_type,
            priority=task.priority,
            status=task.status.value,
            max_retries=task.max_retries,
            retry_count=task.retry_count,
            actor_id=task.actor_id,
            metrics=task.metrics.__dict__ if task.metrics else {},
            extra_metadata=task.metadata,
            version=task.version
        )
        
        # 设置结果信息
        if task.result:
            task_model.result = task.result.value
        if task.error_code:
            task_model.error_code = task.error_code
        if task.error_message:
            task_model.error_message = task.error_message
            
        # 设置时间信息
        if task.start_time:
            task_model.start_time = datetime.fromtimestamp(task.start_time)
        if task.end_time:
            task_model.end_time = datetime.fromtimestamp(task.end_time)
        if task.duration_ms:
            task_model.duration_ms = task.duration_ms
            
        return task_model


class StationMapper:
    """工位映射器"""
    
    @staticmethod
    def to_entity(station_model: StationModel) -> Station:
        """ORM实体转领域对象"""
        station = Station(
            station_id=station_model.station_id,
            code=station_model.code,
            name=station_model.name,
            line_code=station_model.line_code,
            area_code=station_model.area_code
        )
        
        # 恢复状态信息
        station._status = station_model.status
        station._mode = station_model.mode
        station._current_task_id = station_model.current_task_id
        station._is_enabled = station_model.is_enabled
        
        # 恢复状态对象
        resource_state_data = station_model.resource_state or {}
        station._resource_state = ResourceState(
            cpu_usage=resource_state_data.get('cpu_usage', 0.0),
            memory_usage=resource_state_data.get('memory_usage', 0.0),
            disk_usage=resource_state_data.get('disk_usage', 0.0),
            network_latency=resource_state_data.get('network_latency', 0.0),
            temperature=resource_state_data.get('temperature', 25.0),
            uptime_hours=resource_state_data.get('uptime_hours', 0.0)
        )
        
        alarm_state_data = station_model.alarm_state or {}
        station._alarm_state = AlarmState(
            has_alarm=alarm_state_data.get('has_alarm', False),
            active_alarms=alarm_state_data.get('active_alarms', 0),
            last_alarm_time=alarm_state_data.get('last_alarm_time'),
            alarm_severity_avg=alarm_state_data.get('alarm_severity_avg', 'low')
        )
        
        # 恢复挂载设备
        mounted_devices_data = station_model.mounted_devices or []
        station._mounted_devices = [
            DeviceMount(**device_data) for device_data in mounted_devices_data
        ]
        
        # 恢复元数据和版本
        station._metadata = station_model.extra_metadata or {}
        station._version = station_model.version
        
        return station
    
    @staticmethod
    def to_model(station: Station) -> StationModel:
        """领域对象转ORM实体"""
        station_model = StationModel(
            id=station.id,
            station_id=station.station_id,
            code=station.code,
            name=station.name,
            line_code=station.line_code,
            area_code=station.area_code,
            status=station.status,
            mode=station.mode,
            current_task_id=station.current_task_id,
            is_enabled=station.is_enabled,
            resource_state={
                'cpu_usage': station.resource_state.cpu_usage,
                'memory_usage': station.resource_state.memory_usage,
                'disk_usage': station.resource_state.disk_usage,
                'network_latency': station.resource_state.network_latency,
                'temperature': station.resource_state.temperature,
                'uptime_hours': station.resource_state.uptime_hours
            } if station.resource_state else {},
            alarm_state={
                'has_alarm': station.alarm_state.has_alarm,
                'active_alarms': station.alarm_state.active_alarms,
                'last_alarm_time': station.alarm_state.last_alarm_time,
                'alarm_severity_avg': station.alarm_state.alarm_severity_avg
            } if station.alarm_state else {},
            mounted_devices=[
                device.__dict__ for device in station.mounted_devices
            ] if hasattr(station, 'mounted_devices') else [],
            extra_metadata=station.metadata,
            version=station.version
        )
        
        return station_model


class DeviceMapper:
    """设备映射器"""
    
    @staticmethod
    def to_entity(device_model: DeviceModel) -> Device:
        """ORM实体转领域对象"""
        device = Device(
            device_id=device_model.device_id,
            station_id=device_model.station_id,
            code=device_model.code,
            name=device_model.name,
            device_type=device_model.device_type,
            protocol=device_model.protocol
        )
        
        # 恢复状态信息
        device._connect_status = device_model.connect_status
        device._status = device_model.status
        device._is_connected = device_model.is_connected
        device._is_busy = device_model.is_busy
        device._is_heartbeat_alive = device_model.is_heartbeat_alive
        
        # 恢复配置和指标
        device._config = device_model.config or {}
        device._metrics = DeviceMetrics(**(device_model.metrics or {}))
        device._calibration_info = device_model.calibration_info or {}
        
        # 恢复时间信息
        if device_model.last_heartbeat:
            device._last_heartbeat = device_model.last_heartbeat.timestamp()
        device._created_at = device_model.created_at.timestamp()
        
        # 恢复元数据和版本
        device._metadata = device_model.extra_metadata or {}
        device._version = device_model.version
        
        return device
    
    @staticmethod
    def to_model(device: Device) -> DeviceModel:
        """领域对象转ORM实体"""
        device_model = DeviceModel(
            id=device.id,
            device_id=device.device_id,
            station_id=device.station_id,
            code=device.code,
            name=device.name,
            device_type=device.device_type,
            protocol=device.protocol,
            connect_status=device.connect_status,
            status=device.status,
            is_connected=device.is_connected,
            is_busy=device.is_busy,
            is_heartbeat_alive=device.is_heartbeat_alive,
            config=device.config,
            metrics=device.metrics.__dict__ if device.metrics else {},
            calibration_info=device.calibration_info,
            extra_metadata=device.metadata,
            version=device.version
        )
        
        # 设置时间信息
        if device.last_heartbeat:
            device_model.last_heartbeat = datetime.fromtimestamp(device.last_heartbeat)
        if device.created_at:
            device_model.created_at = datetime.fromtimestamp(device.created_at)
            
        return device_model


class AlarmMapper:
    """告警映射器"""
    
    @staticmethod
    def to_entity(alarm_model: AlarmModel) -> Alarm:
        """ORM实体转领域对象"""
        alarm = Alarm(
            alarm_code=alarm_model.alarm_code,
            message=alarm_model.message,
            level=AlarmLevelEnum(alarm_model.alarm_level),
            task_id=alarm_model.task_id,
            station_id=alarm_model.station_id,
            device_id=alarm_model.device_id,
            workorder_id=alarm_model.workorder_id
        )
        
        # 恢复状态
        alarm._status = CommonAlarmStatus(alarm_model.status)
        
        # 恢复时间信息
        if alarm_model.occurred_at:
            alarm._occurred_at = alarm_model.occurred_at.timestamp()
        if alarm_model.acknowledged_at:
            alarm._acknowledged_at = alarm_model.acknowledged_at.timestamp()
        if alarm_model.resolved_at:
            alarm._resolved_at = alarm_model.resolved_at.timestamp()
        if alarm_model.closed_at:
            alarm._closed_at = alarm_model.closed_at.timestamp()
        
        # 恢复元数据和版本
        alarm._metadata = alarm_model.extra_metadata or {}
        alarm._version = alarm_model.version
        
        return alarm
    
    @staticmethod
    def to_model(alarm: Alarm) -> AlarmModel:
        """领域对象转ORM实体"""
        alarm_model = AlarmModel(
            id=alarm.id,
            alarm_id=alarm.alarm_id,
            alarm_code=alarm.alarm_code,
            alarm_level=alarm.level.value,
            message=alarm.message,
            status=alarm.status.value,
            task_id=alarm.task_id,
            station_id=alarm.station_id,
            device_id=alarm.device_id,
            workorder_id=alarm.workorder_id,
            extra_metadata=alarm.metadata,
            version=alarm.version
        )
        
        # 设置时间信息
        if alarm.occurred_at:
            alarm_model.occurred_at = datetime.fromtimestamp(alarm.occurred_at)
        if alarm.acknowledged_at:
            alarm_model.acknowledged_at = datetime.fromtimestamp(alarm.acknowledged_at)
        if alarm.resolved_at:
            alarm_model.resolved_at = datetime.fromtimestamp(alarm.resolved_at)
        if alarm.closed_at:
            alarm_model.closed_at = datetime.fromtimestamp(alarm.closed_at)
            
        return alarm_model


class ReportMapper:
    """报告映射器"""
    
    @staticmethod
    def to_entity(report_model: ReportModel) -> Report:
        """ORM实体转领域对象"""
        report = Report(report_model.report_id)
        
        # 恢复基本信息
        report._task_id = report_model.task_id
        report._workorder_id = report_model.workorder_id
        report._sn = report_model.sn
        report._status = ReportStatus(report_model.status)
        if report_model.result:
            report._result = TaskResult(report_model.result)
        
        # 恢复快照数据
        if report_model.task_snapshot:
            task_snapshot_data = report_model.task_snapshot
            report._task_snapshot = TaskSnapshot(
                task_id=task_snapshot_data['task_id'],
                workorder_id=task_snapshot_data['workorder_id'],
                station_id=task_snapshot_data['station_id'],
                device_id=task_snapshot_data.get('device_id'),
                sn=task_snapshot_data['sn'],
                task_type=task_snapshot_data['task_type'],
                priority=task_snapshot_data['priority'],
                status=task_snapshot_data['status'],
                result=task_snapshot_data.get('result'),
                error_code=task_snapshot_data.get('error_code'),
                error_message=task_snapshot_data.get('error_message'),
                retry_count=task_snapshot_data['retry_count'],
                max_retries=task_snapshot_data['max_retries'],
                actor_id=task_snapshot_data.get('actor_id'),
                start_time=task_snapshot_data.get('start_time'),
                end_time=task_snapshot_data.get('end_time'),
                duration_ms=task_snapshot_data.get('duration_ms'),
                metrics=task_snapshot_data.get('metrics', {}),
                metadata=task_snapshot_data.get('metadata', {})
            )
        
        if report_model.station_snapshot:
            station_snapshot_data = report_model.station_snapshot
            report._station_snapshot = StationSnapshot(
                station_id=station_snapshot_data['station_id'],
                code=station_snapshot_data['code'],
                name=station_snapshot_data['name'],
                line_code=station_snapshot_data['line_code'],
                area_code=station_snapshot_data['area_code'],
                status=station_snapshot_data['status'],
                mode=station_snapshot_data['mode'],
                current_task_id=station_snapshot_data['current_task_id'],
                is_enabled=station_snapshot_data['is_enabled'],
                resource_state=station_snapshot_data.get('resource_state', {}),
                alarm_state=station_snapshot_data.get('alarm_state', {}),
                mounted_devices=station_snapshot_data.get('mounted_devices', []),
                metadata=station_snapshot_data.get('metadata', {})
            )
        
        if report_model.device_snapshots:
            report._device_snapshots = []
            for device_snapshot_data in report_model.device_snapshots:
                device_snapshot = DeviceSnapshot(
                    device_id=device_snapshot_data['device_id'],
                    station_id=device_snapshot_data['station_id'],
                    code=device_snapshot_data['code'],
                    name=device_snapshot_data['name'],
                    device_type=device_snapshot_data['device_type'],
                    protocol=device_snapshot_data['protocol'],
                    connect_status=device_snapshot_data['connect_status'],
                    status=device_snapshot_data['status'],
                    is_connected=device_snapshot_data['is_connected'],
                    is_busy=device_snapshot_data['is_busy'],
                    is_heartbeat_alive=device_snapshot_data['is_heartbeat_alive'],
                    config=device_snapshot_data['config'],
                    metrics=device_snapshot_data['metrics'],
                    calibration_info=device_snapshot_data['calibration_info'],
                    last_heartbeat=device_snapshot_data.get('last_heartbeat'),
                    created_at=device_snapshot_data['created_at'],
                    metadata=device_snapshot_data.get('metadata', {})
                )
                report._device_snapshots.append(device_snapshot)
        
        if report_model.test_records:
            report._test_records = []
            for test_record_data in report_model.test_records:
                test_record = TestRecord(
                    record_id=test_record_data['record_id'],
                    step=test_record_data['step'],
                    name=test_record_data['name'],
                    value_type=test_record_data['value_type'],
                    value_raw=test_record_data['value_raw'],
                    expected=test_record_data.get('expected'),
                    tolerance=test_record_data.get('tolerance'),
                    is_pass=test_record_data['is_pass'],
                    timestamp=test_record_data.get('timestamp', 0),
                    metadata=test_record_data.get('metadata', {})
                )
                report._test_records.append(test_record)
        
        if report_model.alarm_snapshots:
            report._alarm_snapshots = []
            for alarm_snapshot_data in report_model.alarm_snapshots:
                alarm_snapshot = AlarmSnapshot(
                    alarm_id=alarm_snapshot_data['alarm_id'],
                    alarm_code=alarm_snapshot_data['alarm_code'],
                    alarm_level=alarm_snapshot_data['alarm_level'],
                    message=alarm_snapshot_data['message'],
                    status=alarm_snapshot_data['status'],
                    occurred_at=alarm_snapshot_data['occurred_at'],
                    acknowledged_at=alarm_snapshot_data.get('acknowledged_at'),
                    resolved_at=alarm_snapshot_data.get('resolved_at'),
                    closed_at=alarm_snapshot_data.get('closed_at'),
                    task_id=alarm_snapshot_data.get('task_id'),
                    station_id=alarm_snapshot_data.get('station_id'),
                    device_id=alarm_snapshot_data.get('device_id'),
                    workorder_id=alarm_snapshot_data.get('workorder_id'),
                    metadata=alarm_snapshot_data.get('metadata', {})
                )
                report._alarm_snapshots.append(alarm_snapshot)
        
        if report_model.software_version:
            sw_version_data = report_model.software_version
            report._software_version = SoftwareVersion(
                encoder_test_version=sw_version_data['encoder_test_version'],
                driver_version=sw_version_data['driver_version'],
                firmware_version=sw_version_data['firmware_version'],
                os_version=sw_version_data['os_version'],
                python_version=sw_version_data['python_version'],
                created_at=sw_version_data.get('created_at', 0)
            )
        
        if report_model.operator_info:
            op_info_data = report_model.operator_info
            report._operator_info = OperatorInfo(
                operator_id=op_info_data['operator_id'],
                operator_name=op_info_data['operator_name'],
                role=op_info_data['role'],
                department=op_info_data['department'],
                timestamp=op_info_data.get('timestamp', 0)
            )
        
        # 恢复时间信息
        if report_model.generated_at:
            report._generated_at = report_model.generated_at.timestamp()
        if report_model.archived_at:
            report._archived_at = report_model.archived_at.timestamp()
        
        # 恢复指标和元数据
        if report_model.metrics:
            report._metrics = ReportMetrics(
                total_records=report_model.metrics.get('total_records', 0),
                pass_records=report_model.metrics.get('pass_records', 0),
                fail_records=report_model.metrics.get('fail_records', 0),
                duration_ms=report_model.metrics.get('duration_ms', 0)
            )
        report._metadata = report_model.extra_metadata or {}
        
        # 恢复版本
        report._version = report_model.version
        
        return report
    
    @staticmethod
    def to_model(report: Report) -> ReportModel:
        """领域对象转ORM实体"""
        report_model = ReportModel(
            id=report.id,
            report_id=report.report_id,
            task_id=report.task_id,
            workorder_id=report.workorder_id,
            sn=report.sn,
            status=report.status.value,
            extra_metadata=report.metadata,
            version=report.version
        )
        
        # 设置结果
        if report.result:
            report_model.result = report.result.value
            
        # 设置时间信息
        if report.generated_at:
            report_model.generated_at = datetime.fromtimestamp(report.generated_at)
        if report.archived_at:
            report_model.archived_at = datetime.fromtimestamp(report.archived_at)
            
        # 设置快照数据
        if report.task_snapshot:
            report_model.task_snapshot = {
                'task_id': report.task_snapshot.task_id,
                'workorder_id': report.task_snapshot.workorder_id,
                'station_id': report.task_snapshot.station_id,
                'device_id': report.task_snapshot.device_id,
                'sn': report.task_snapshot.sn,
                'task_type': report.task_snapshot.task_type,
                'priority': report.task_snapshot.priority,
                'status': report.task_snapshot.status,
                'result': report.task_snapshot.result,
                'error_code': report.task_snapshot.error_code,
                'error_message': report.task_snapshot.error_message,
                'retry_count': report.task_snapshot.retry_count,
                'max_retries': report.task_snapshot.max_retries,
                'actor_id': report.task_snapshot.actor_id,
                'start_time': report.task_snapshot.start_time,
                'end_time': report.task_snapshot.end_time,
                'duration_ms': report.task_snapshot.duration_ms,
                'metrics': report.task_snapshot.metrics,
                'metadata': report.task_snapshot.metadata
            }
        
        if report.station_snapshot:
            report_model.station_snapshot = {
                'station_id': report.station_snapshot.station_id,
                'code': report.station_snapshot.code,
                'name': report.station_snapshot.name,
                'line_code': report.station_snapshot.line_code,
                'area_code': report.station_snapshot.area_code,
                'status': report.station_snapshot.status,
                'mode': report.station_snapshot.mode,
                'current_task_id': report.station_snapshot.current_task_id,
                'is_enabled': report.station_snapshot.is_enabled,
                'resource_state': report.station_snapshot.resource_state,
                'alarm_state': report.station_snapshot.alarm_state,
                'mounted_devices': report.station_snapshot.mounted_devices,
                'metadata': report.station_snapshot.metadata
            }
        
        if report.device_snapshots:
            report_model.device_snapshots = [
                {
                    'device_id': ds.device_id,
                    'station_id': ds.station_id,
                    'code': ds.code,
                    'name': ds.name,
                    'device_type': ds.device_type,
                    'protocol': ds.protocol,
                    'connect_status': ds.connect_status,
                    'status': ds.status,
                    'is_connected': ds.is_connected,
                    'is_busy': ds.is_busy,
                    'is_heartbeat_alive': ds.is_heartbeat_alive,
                    'config': ds.config,
                    'metrics': ds.metrics,
                    'calibration_info': ds.calibration_info,
                    'last_heartbeat': ds.last_heartbeat,
                    'created_at': ds.created_at,
                    'metadata': ds.metadata
                }
                for ds in report.device_snapshots
            ]
        
        if report.test_records:
            report_model.test_records = [
                {
                    'record_id': tr.record_id,
                    'step': tr.step,
                    'name': tr.name,
                    'value_type': tr.value_type,
                    'value_raw': tr.value_raw,
                    'expected': tr.expected,
                    'tolerance': tr.tolerance,
                    'is_pass': tr.is_pass,
                    'timestamp': tr.timestamp,
                    'metadata': tr.metadata
                }
                for tr in report.test_records
            ]
        
        if report.alarm_snapshots:
            report_model.alarm_snapshots = [
                {
                    'alarm_id': as_.alarm_id,
                    'alarm_code': as_.alarm_code,
                    'alarm_level': as_.alarm_level,
                    'message': as_.message,
                    'status': as_.status,
                    'occurred_at': as_.occurred_at,
                    'acknowledged_at': as_.acknowledged_at,
                    'resolved_at': as_.resolved_at,
                    'closed_at': as_.closed_at,
                    'task_id': as_.task_id,
                    'station_id': as_.station_id,
                    'device_id': as_.device_id,
                    'workorder_id': as_.workorder_id,
                    'metadata': as_.metadata
                }
                for as_ in report.alarm_snapshots
            ]
        
        if report.software_version:
            report_model.software_version = {
                'encoder_test_version': report.software_version.encoder_test_version,
                'driver_version': report.software_version.driver_version,
                'firmware_version': report.software_version.firmware_version,
                'os_version': report.software_version.os_version,
                'python_version': report.software_version.python_version,
                'created_at': report.software_version.created_at
            }
        
        if report.operator_info:
            report_model.operator_info = {
                'operator_id': report.operator_info.operator_id,
                'operator_name': report.operator_info.operator_name,
                'role': report.operator_info.role,
                'department': report.operator_info.department,
                'timestamp': report.operator_info.timestamp
            }
        
        # 设置指标
        if report.metrics:
            report_model.metrics = {
                'total_records': report.metrics.total_records,
                'pass_records': report.metrics.pass_records,
                'fail_records': report.metrics.fail_records,
                'duration_ms': report.metrics.duration_ms
            }
            
        return report_model


class TestRecordMapper:
    """测试记录映射器"""
    
    @staticmethod
    def to_entity(test_record_model: TestRecordModel) -> TestRecord:
        """ORM实体转领域对象"""
        test_record = TestRecord(
            record_id=test_record_model.record_id,
            step=test_record_model.step,
            name=test_record_model.name,
            value_type=test_record_model.value_type,
            value_raw=test_record_model.value_raw,
            expected=test_record_model.expected,
            tolerance=test_record_model.tolerance,
            is_pass=test_record_model.is_pass,
            metadata=test_record_model.extra_metadata or {}
        )
        
        if test_record_model.timestamp:
            test_record.timestamp = test_record_model.timestamp.timestamp()
            
        return test_record
    
    @staticmethod
    def to_model(test_record: TestRecord) -> TestRecordModel:
        """领域对象转ORM实体"""
        test_record_model = TestRecordModel(
            record_id=test_record.record_id,
            report_id="",  # 这将在保存时设置
            step=test_record.step,
            name=test_record.name,
            value_type=test_record.value_type,
            value_raw=test_record.value_raw,
            expected=test_record.expected,
            tolerance=test_record.tolerance,
            is_pass=test_record.is_pass,
            extra_metadata=test_record.metadata
        )
        
        if hasattr(test_record, 'timestamp'):
            test_record_model.timestamp = datetime.fromtimestamp(test_record.timestamp)
            
        return test_record_model
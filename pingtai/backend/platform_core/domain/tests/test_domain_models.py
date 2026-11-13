"""
领域模型单元测试 - Domain Model Unit Tests

【职责】
- 测试聚合根行为
- 测试状态转换
- 测试业务规则
- 测试领域事件
"""
import pytest
import time

from platform.domain.common import (
    AggregateRoot, Entity, ValueObject, generate_id,
    TaskStatus, TaskResult, TaskPriority, StationStatus, StationMode,
    DeviceStatus, DeviceConnectStatus, DeviceType, ProtocolType,
    WorkOrderStatus, ReportStatus, AlarmLevel, EventType,
    DomainException,
    TaskException, TaskNotFoundException, TaskStatusTransitionException,
    TaskAlreadyRunningException, TaskRetryExhaustedException,
    StationException, StationNotFoundException, StationOfflineException, StationBusyException,
    DeviceException, DeviceNotFoundException, DeviceNotConnectedException, DeviceBusyException,
    ValidationException, ConcurrencyException,
    StateMachine, TaskStateMachine, StationStateMachine, StateTransition
)
from platform.domain.task import Task, TaskMetrics, RuntimeSession, TaskFlow, DomainEvent
from platform.domain.station import Station, ResourceState, AlarmState, DeviceMount
from platform.domain.device import Device, DeviceConfig, CalibrationInfo, DeviceMetrics


class TestAggregateRoot:
    """聚合根基类测试"""
    
    def test_aggregate_root_creation(self):
        """测试聚合根创建"""
        root = AggregateRoot("ROOT-001")
        assert root.id == "ROOT-001"
        assert root.version == 0
        assert root.created_at > 0
    
    def test_aggregate_root_version_increment(self):
        """测试版本号递增"""
        root = AggregateRoot("ROOT-001")
        initial_version = root.version
        
        root._increment_version()
        
        assert root.version == initial_version + 1
    
    def test_aggregate_root_domain_events(self):
        """测试领域事件"""
        root = AggregateRoot("ROOT-001")
        event = DomainEvent(
            event_type=EventType.TASK_CREATED,
            aggregate_id="ROOT-001",
            aggregate_type="TestRoot",
            data={}
        )
        
        root._add_domain_event(event)
        events = root.pull_domain_events()
        
        assert len(events) == 1
        assert events[0].event_type == EventType.TASK_CREATED
    
    def test_aggregate_root_equality(self):
        """测试相等性"""
        root1 = AggregateRoot("ROOT-001")
        root2 = AggregateRoot("ROOT-001")
        root3 = AggregateRoot("ROOT-002")
        
        assert root1 == root2
        assert root1 != root3
    
    def test_aggregate_root_hash(self):
        """测试哈希值"""
        root1 = AggregateRoot("ROOT-001")
        root2 = AggregateRoot("ROOT-001")
        
        assert hash(root1) == hash(root2)


class TestTask:
    """任务聚合根测试"""
    
    def test_task_creation(self):
        """测试任务创建"""
        task = Task.create(
            workorder_id="WO-001",
            station_id=1,
            sn="SN123456",
            task_type="encoder_accuracy"
        )
        
        assert task.id.startswith("TASK-")
        assert task.workorder_id == "WO-001"
        assert task.station_id == 1
        assert task.sn == "SN123456"
        assert task.task_type == "encoder_accuracy"
        assert task.status == TaskStatus.PENDING
        assert task.version == 0
    
    def test_task_start(self):
        """测试任务开始"""
        task = Task.create(
            workorder_id="WO-001",
            station_id=1,
            sn="SN123456",
            task_type="encoder_accuracy"
        )
        
        task.start(actor_id="ACTOR-001")
        
        assert task.status == TaskStatus.RUNNING
        assert task.actor_id == "ACTOR-001"
        assert task.start_time is not None
        assert task.runtime_session is not None
        assert task.version == 1
    
    def test_task_start_already_running(self):
        """测试任务重复开始"""
        task = Task.create(
            workorder_id="WO-001",
            station_id=1,
            sn="SN123456",
            task_type="encoder_accuracy"
        )
        
        task.start(actor_id="ACTOR-001")
        
        with pytest.raises(TaskAlreadyRunningException):
            task.start(actor_id="ACTOR-002")
    
    def test_task_complete(self):
        """测试任务完成"""
        task = Task.create(
            workorder_id="WO-001",
            station_id=1,
            sn="SN123456",
            task_type="encoder_accuracy"
        )
        
        task.start(actor_id="ACTOR-001")
        time.sleep(0.01)  # 添加小延迟确保有时间差
        task.complete(result=TaskResult.PASS)
        
        assert task.status == TaskStatus.COMPLETED
        assert task.result == TaskResult.PASS
        assert task.end_time is not None
        assert task.duration_ms >= 0
    
    def test_task_fail(self):
        """测试任务失败"""
        task = Task.create(
            workorder_id="WO-001",
            station_id=1,
            sn="SN123456",
            task_type="encoder_accuracy"
        )
        
        task.start(actor_id="ACTOR-001")
        task.fail(error_code="ERR-001", error_message="设备连接失败")
        
        assert task.status == TaskStatus.FAILED
        assert task.result == TaskResult.FAIL
        assert task.error_code == "ERR-001"
        assert task.error_message == "设备连接失败"
    
    def test_task_abort(self):
        """测试任务中止"""
        task = Task.create(
            workorder_id="WO-001",
            station_id=1,
            sn="SN123456",
            task_type="encoder_accuracy"
        )
        
        task.start(actor_id="ACTOR-001")
        task.abort(reason="用户取消")
        
        assert task.status == TaskStatus.ABORTED
    
    def test_task_retry(self):
        """测试任务重试"""
        task = Task.create(
            workorder_id="WO-001",
            station_id=1,
            sn="SN123456",
            task_type="encoder_accuracy",
            max_retries=3
        )
        
        task.start(actor_id="ACTOR-001")
        task.fail(error_code="ERR-001", error_message="设备连接失败")
        task.retry()
        
        assert task.status == TaskStatus.PENDING
        assert task.retry_count == 1
        assert task.error_code is None
    
    def test_task_retry_exhausted(self):
        """测试重试次数耗尽"""
        from encoder_test.domain.common import TaskRetryExhaustedException
        
        task = Task.create(
            workorder_id="WO-001",
            station_id=1,
            sn="SN123456",
            task_type="encoder_accuracy",
            max_retries=2
        )
        
        task.start(actor_id="ACTOR-001")
        task.fail(error_code="ERR-001", error_message="设备连接失败")
        task.retry()
        
        task.start(actor_id="ACTOR-001")
        task.fail(error_code="ERR-001", error_message="设备连接失败")
        task.retry()
        
        task.start(actor_id="ACTOR-001")
        task.fail(error_code="ERR-001", error_message="设备连接失败")
        
        with pytest.raises(TaskRetryExhaustedException):
            task.retry()
    
    def test_task_flow(self):
        """测试任务流程"""
        task = Task.create(
            workorder_id="WO-001",
            station_id=1,
            sn="SN123456",
            task_type="encoder_accuracy"
        )
        
        task.set_task_flow(
            flow_name="calibration_flow",
            flow_config={"steps": ["step1", "step2", "step3"]},
            total_steps=3
        )
        
        assert task.task_flow is not None
        assert task.task_flow.total_steps == 3
        assert task.task_flow.current_step == 0
        
        task.advance_flow_step({"step": "step1", "result": "pass"})
        assert task.task_flow.current_step == 1
    
    def test_task_to_dict(self):
        """测试转换为字典"""
        task = Task.create(
            workorder_id="WO-001",
            station_id=1,
            sn="SN123456",
            task_type="encoder_accuracy"
        )
        
        task_dict = task.to_dict()
        
        assert 'id' in task_dict
        assert 'workorder_id' in task_dict
        assert 'station_id' in task_dict
        assert 'sn' in task_dict
        assert 'task_type' in task_dict
        assert 'status' in task_dict
        assert 'version' in task_dict
    
    def test_task_repr(self):
        """测试字符串表示"""
        task = Task.create(
            workorder_id="WO-001",
            station_id=1,
            sn="SN123456",
            task_type="encoder_accuracy"
        )
        
        repr_str = repr(task)
        assert "Task" in repr_str
        assert "SN123456" in repr_str


class TestStation:
    """工位聚合根测试"""
    
    def test_station_creation(self):
        """测试工位创建"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位",
            line_code="LINE-001",
            area_code="AREA-001"
        )
        
        assert station.id.startswith("STATION-")
        assert station.code == "STATION-001"
        assert station.name == "编码器校准工位"
        assert station.status == StationStatus.IDLE
        assert station.mode == StationMode.AUTO
    
    def test_station_start(self):
        """测试工位启动"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        station.start()
        
        assert station.status == StationStatus.RUNNING
    
    def test_station_stop(self):
        """测试工位停止"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        station.start()
        station.stop()
        
        assert station.status == StationStatus.IDLE
    
    def test_station_mount_device(self):
        """测试挂载设备"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        station.mount_device(
            device_id="DEV-001",
            device_type="encoder"
        )
        
        assert len(station.mounted_devices) == 1
        assert station.mounted_devices[0].device_id == "DEV-001"
    
    def test_station_unmount_device(self):
        """测试卸载设备"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        station.mount_device(
            device_id="DEV-001",
            device_type="encoder"
        )
        station.unmount_device("DEV-001")
        
        assert len(station.mounted_devices) == 0
    
    def test_station_assign_task(self):
        """测试分配任务"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        station.assign_task(task_id="TASK-001")
        
        assert station.current_task_id == "TASK-001"
    
    def test_station_assign_task_busy(self):
        """测试分配任务（工位忙碌）"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        station.assign_task(task_id="TASK-001")
        
        with pytest.raises(StationBusyException):
            station.assign_task(task_id="TASK-002")
    
    def test_station_release_task(self):
        """测试释放任务"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        station.assign_task(task_id="TASK-001")
        station.release_task()
        
        assert station.current_task_id is None
    
    def test_station_update_resource_state(self):
        """测试更新资源状态"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        station.update_resource_state(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=70.0
        )
        
        assert station.resource_state.cpu_usage == 50.0
        assert station.resource_state.memory_usage == 60.0
        assert station.resource_state.disk_usage == 70.0
    
    def test_station_set_alarm(self):
        """测试设置告警"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        station.set_alarm(
            alarm_level="warning",
            alarm_message="CPU使用率过高"
        )
        
        assert station.alarm_state.has_alarm is True
        assert station.alarm_state.alarm_level == "warning"
        assert station.alarm_state.alarm_message == "CPU使用率过高"
    
    def test_station_clear_alarm(self):
        """测试清除告警"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        station.set_alarm(
            alarm_level="warning",
            alarm_message="CPU使用率过高"
        )
        station.clear_alarm()
        
        assert station.alarm_state.has_alarm is False
    
    def test_station_offline(self):
        """测试工位离线"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        station.offline()
        
        assert station.status == StationStatus.OFFLINE
        assert station.is_enabled is False
    
    def test_station_maintenance(self):
        """测试工位维护"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        station.maintenance()
        
        assert station.status == StationStatus.MAINTENANCE
    
    def test_station_recover(self):
        """测试工位恢复"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        # 先让工位进入错误状态
        station.error("测试错误")
        assert station.status == StationStatus.ERROR
        
        # 然后恢复工位
        station.recover()
        
        assert station.status == StationStatus.IDLE
    
    def test_station_set_mode(self):
        """测试设置运行模式"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        station.set_mode(StationMode.MANUAL)
        
        assert station.mode == StationMode.MANUAL
    
    def test_station_to_dict(self):
        """测试转换为字典"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        station_dict = station.to_dict()
        
        assert 'id' in station_dict
        assert 'code' in station_dict
        assert 'name' in station_dict
        assert 'status' in station_dict
        assert 'version' in station_dict
    
    def test_station_repr(self):
        """测试字符串表示"""
        station = Station.create(
            code="STATION-001",
            name="编码器校准工位"
        )
        
        repr_str = repr(station)
        assert "Station" in repr_str
        assert "STATION-001" in repr_str


class TestDevice:
    """设备聚合根测试"""
    
    def test_device_creation(self):
        """测试设备创建"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        assert device.id.startswith("DEV-")
        assert device.station_id == 1
        assert device.code == "DEV-001"
        assert device.name == "编码器"
        assert device.device_type == DeviceType.ENCODER
        assert device.protocol == ProtocolType.MODBUS_RTU
        assert device.status == DeviceStatus.IDLE
        assert device.connect_status == DeviceConnectStatus.DISCONNECTED
    
    def test_device_connect(self):
        """测试设备连接"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        device.connect()
        
        assert device.connect_status == DeviceConnectStatus.CONNECTED
        assert device.is_connected is True
        assert device.last_heartbeat is not None
    
    def test_device_disconnect(self):
        """测试设备断开"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        device.connect()
        device.disconnect()
        
        assert device.connect_status == DeviceConnectStatus.DISCONNECTED
        assert device.is_connected is False
        assert device.last_heartbeat is None
    
    def test_device_update_heartbeat(self):
        """测试更新心跳"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        device.connect()
        time.sleep(0.1)
        device.update_heartbeat()
        
        assert device.last_heartbeat > 0
        assert device.is_heartbeat_alive is True
    
    def test_device_update_heartbeat_not_connected(self):
        """测试更新心跳（未连接）"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        with pytest.raises(DeviceNotConnectedException):
            device.update_heartbeat()
    
    def test_device_set_busy(self):
        """测试设置忙碌"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        device.set_busy(True)
        
        assert device.is_busy is True
        assert device.status == DeviceStatus.BUSY
        
        device.set_busy(False)
        
        assert device.is_busy is False
        assert device.status == DeviceStatus.IDLE
    
    def test_device_calibrate(self):
        """测试设备校准"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        device.connect()
        device.calibrate(
            calibration_data={"offset": 0.1, "scale": 1.0},
            next_calibration_days=30
        )
        
        assert device.calibration_info.is_calibrated is True
        assert device.calibration_info.calibrated_at is not None
        assert device.calibration_info.calibration_data == {"offset": 0.1, "scale": 1.0}
        assert device.calibration_info.is_calibration_expired is False
    
    def test_device_calibrate_not_connected(self):
        """测试设备校准（未连接）"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        with pytest.raises(DeviceNotConnectedException):
            device.calibrate()
    
    def test_device_calibrate_busy(self):
        """测试设备校准（忙碌）"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        device.connect()
        device.set_busy(True)
        
        with pytest.raises(DeviceBusyException):
            device.calibrate()
    
    def test_device_record_operation(self):
        """测试记录操作"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        device.record_operation(success=True)
        device.record_operation(success=True)
        device.record_operation(success=False)
        
        assert device.metrics.total_operations == 3
        assert device.metrics.success_operations == 2
        assert device.metrics.failed_operations == 1
        assert device.metrics.success_rate == 2.0 / 3.0
    
    def test_device_set_error(self):
        """测试设置错误"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        device.connect()
        device.set_error()
        
        assert device.status == DeviceStatus.ERROR
        assert device.connect_status == DeviceConnectStatus.ERROR
    
    def test_device_recover(self):
        """测试设备恢复"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        device.connect()
        device.set_error()
        device.recover()
        
        assert device.status == DeviceStatus.IDLE
        assert device.connect_status == DeviceConnectStatus.CONNECTED
    
    def test_device_update_config(self):
        """测试更新设备配置"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        new_config = DeviceConfig(protocol="custom", timeout=10.0)
        device.update_config(new_config)
        
        assert device.config.timeout == 10.0
    
    def test_device_to_dict(self):
        """测试转换为字典"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        device_dict = device.to_dict()
        
        assert 'id' in device_dict
        assert 'code' in device_dict
        assert 'name' in device_dict
        assert 'device_type' in device_dict
        assert 'protocol' in device_dict
        assert 'version' in device_dict
    
    def test_device_repr(self):
        """测试字符串表示"""
        device = Device.create(
            station_id=1,
            code="DEV-001",
            name="编码器",
            device_type=DeviceType.ENCODER,
            protocol=ProtocolType.MODBUS_RTU
        )
        
        repr_str = repr(device)
        assert "Device" in repr_str
        assert "DEV-001" in repr_str


class TestValueObjects:
    """值对象测试"""
    
    def test_task_metrics_equality(self):
        """测试任务指标相等性"""
        metrics1 = TaskMetrics(duration_ms=1000, step_count=10, retry_count=0, error_count=0)
        metrics2 = TaskMetrics(duration_ms=1000, step_count=10, retry_count=0, error_count=0)
        metrics3 = TaskMetrics(duration_ms=2000, step_count=10, retry_count=0, error_count=0)
        
        assert metrics1 == metrics2
        assert metrics1 != metrics3
    
    def test_resource_state_equality(self):
        """测试资源状态相等性"""
        state1 = ResourceState(cpu_usage=50.0, memory_usage=60.0, disk_usage=70.0)
        state2 = ResourceState(cpu_usage=50.0, memory_usage=60.0, disk_usage=70.0)
        state3 = ResourceState(cpu_usage=80.0, memory_usage=60.0, disk_usage=70.0)
        
        assert state1 == state2
        assert state1 != state3
    
    def test_calibration_info_equality(self):
        """测试校准信息相等性"""
        info1 = CalibrationInfo(is_calibrated=True, calibrated_at=time.time())
        info2 = CalibrationInfo(is_calibrated=True, calibrated_at=info1.calibrated_at)
        info3 = CalibrationInfo(is_calibrated=False)
        
        assert info1 == info2
        assert info1 != info3
    
    def test_device_metrics_success_rate(self):
        """测试设备指标成功率"""
        metrics = DeviceMetrics(
            total_operations=10,
            success_operations=8,
            failed_operations=2
        )
        
        assert metrics.success_rate == 0.8
    
    def test_calibration_info_expired(self):
        """测试校准信息过期"""
        past_time = time.time() - 3600 * 24 * 2  # 2天前
        info = CalibrationInfo(
            is_calibrated=True,
            calibrated_at=past_time,
            next_calibration_time=time.time() - 3600  # 1小时前
        )
        
        assert info.is_calibration_expired is True


class TestEnums:
    """枚举测试"""
    
    def test_task_status_transitions(self):
        """测试任务状态转换"""
        # 合法转换
        assert TaskStatus.can_transition(TaskStatus.PENDING, TaskStatus.RUNNING)
        assert TaskStatus.can_transition(TaskStatus.PENDING, TaskStatus.ABORTED)
        assert TaskStatus.can_transition(TaskStatus.RUNNING, TaskStatus.COMPLETED)
        assert TaskStatus.can_transition(TaskStatus.RUNNING, TaskStatus.FAILED)
        assert TaskStatus.can_transition(TaskStatus.RUNNING, TaskStatus.ABORTED)
        
        # 非法转换
        assert not TaskStatus.can_transition(TaskStatus.COMPLETED, TaskStatus.RUNNING)
        assert not TaskStatus.can_transition(TaskStatus.FAILED, TaskStatus.RUNNING)
        assert not TaskStatus.can_transition(TaskStatus.ABORTED, TaskStatus.RUNNING)
    
    def test_task_status_values(self):
        """测试任务状态值"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.ABORTED.value == "aborted"
    
    def test_task_result_values(self):
        """测试任务结果值"""
        assert TaskResult.PASS.value == "pass"
        assert TaskResult.FAIL.value == "fail"
        assert TaskResult.SKIP.value == "skip"
    
    def test_station_status_values(self):
        """测试工位状态值"""
        assert StationStatus.IDLE.value == "idle"
        assert StationStatus.RUNNING.value == "running"
        assert StationStatus.OFFLINE.value == "offline"
        assert StationStatus.ERROR.value == "error"
        assert StationStatus.MAINTENANCE.value == "maintenance"
    
    def test_device_status_values(self):
        """测试设备状态值"""
        assert DeviceStatus.IDLE.value == "idle"
        assert DeviceStatus.BUSY.value == "busy"
        assert DeviceStatus.ERROR.value == "error"
        assert DeviceStatus.OFFLINE.value == "offline"


class TestExceptions:
    """异常测试"""
    
    def test_task_not_found_exception(self):
        """测试任务不存在异常"""
        exc = TaskNotFoundException("TASK-001")
        
        assert exc.error_code == "TASK_NOT_FOUND"
        assert "TASK-001" in exc.message
        assert exc.context['task_id'] == "TASK-001"
    
    def test_task_status_transition_exception(self):
        """测试任务状态转换异常"""
        exc = TaskStatusTransitionException("TASK-001", "running", "pending")
        
        assert exc.error_code == "TASK_STATUS_TRANSITION_INVALID"
        assert "running -> pending" in exc.message
        assert exc.context['from_status'] == "running"
        assert exc.context['to_status'] == "pending"
    
    def test_task_already_running_exception(self):
        """测试任务已运行异常"""
        exc = TaskAlreadyRunningException("TASK-001")
        
        assert exc.error_code == "TASK_ALREADY_RUNNING"
        assert "TASK-001" in exc.message
    
    def test_task_retry_exhausted_exception(self):
        """测试任务重试耗尽异常"""
        exc = TaskRetryExhaustedException("TASK-001", 3, 3)
        
        assert exc.error_code == "TASK_RETRY_EXHAUSTED"
        assert "3/3" in exc.message
    
    def test_station_not_found_exception(self):
        """测试工位不存在异常"""
        exc = StationNotFoundException("STATION-001")
        
        assert exc.error_code == "STATION_NOT_FOUND"
        assert "STATION-001" in exc.message
    
    def test_station_offline_exception(self):
        """测试工位离线异常"""
        exc = StationOfflineException("STATION-001")
        
        assert exc.error_code == "STATION_OFFLINE"
        assert "STATION-001" in exc.message
    
    def test_station_busy_exception(self):
        """测试工位忙碌异常"""
        exc = StationBusyException("STATION-001", "TASK-001")
        
        assert exc.error_code == "STATION_BUSY"
        assert "STATION-001" in exc.message
        assert "TASK-001" in exc.message
    
    def test_device_not_found_exception(self):
        """测试设备不存在异常"""
        exc = DeviceNotFoundException("DEV-001")
        
        assert exc.error_code == "DEVICE_NOT_FOUND"
        assert "DEV-001" in exc.message
    
    def test_device_not_connected_exception(self):
        """测试设备未连接异常"""
        exc = DeviceNotConnectedException("DEV-001")
        
        assert exc.error_code == "DEVICE_NOT_CONNECTED"
        assert "DEV-001" in exc.message
    
    def test_device_busy_exception(self):
        """测试设备忙碌异常"""
        exc = DeviceBusyException("DEV-001")
        
        assert exc.error_code == "DEVICE_BUSY"
        assert "DEV-001" in exc.message
    
    def test_validation_exception(self):
        """测试校验异常"""
        exc = ValidationException("字段校验失败", "field_name", "field_value")
        
        assert exc.error_code == "VALIDATION_ERROR"
        assert "字段校验失败" in exc.message
        assert exc.context['field'] == "field_name"
        assert exc.context['value'] == "field_value"
    
    def test_concurrency_exception(self):
        """测试并发异常"""
        exc = ConcurrencyException("Task", "TASK-001", 2, 1)
        
        assert exc.error_code == "CONCURRENCY_CONFLICT"
        assert "Task#TASK-001" in exc.message
        assert exc.context['current_version'] == 2
        assert exc.context['expected_version'] == 1


class TestStateMachines:
    """状态机测试"""
    
    def test_task_state_machine(self):
        """测试任务状态机"""
        sm = TaskStateMachine("TASK-001")
        
        assert sm.current_state == "pending"
        
        # 测试合法转换
        sm.start()
        assert sm.current_state == "running"
        
        sm.complete()
        assert sm.current_state == "completed"
    
    def test_task_state_machine_invalid_transition(self):
        """测试任务状态机非法转换"""
        sm = TaskStateMachine("TASK-001")
        
        # 尝试从 pending 直接到 completed（非法）
        with pytest.raises(ValueError):
            sm.transition("completed")
    
    def test_station_state_machine(self):
        """测试工位状态机"""
        sm = StationStateMachine("STATION-001")
        
        assert sm.current_state == "idle"
        
        sm.start()
        assert sm.current_state == "running"
        
        sm.stop()
        assert sm.current_state == "idle"
    
    def test_station_state_machine_error(self):
        """测试工位状态机错误"""
        sm = StationStateMachine("STATION-001")
        
        sm.error("测试错误")
        assert sm.current_state == "error"
    
    def test_station_state_machine_recovery(self):
        """测试工位状态机恢复"""
        sm = StationStateMachine("STATION-001")
        
        sm.error("测试错误")
        sm.recover()
        assert sm.current_state == "idle"
    
    def test_state_machine_history(self):
        """测试状态机历史记录"""
        sm = TaskStateMachine("TASK-001")
        
        sm.start()
        sm.complete()
        
        history = sm.history
        assert len(history) == 2
        assert history[0].from_state == "pending"
        assert history[0].to_state == "running"
        assert history[1].from_state == "running"
        assert history[1].to_state == "completed"
    
    def test_state_machine_reset(self):
        """测试状态机重置"""
        sm = TaskStateMachine("TASK-001")
        
        sm.start()
        sm.reset()
        
        assert sm.current_state == "pending"
        assert len(sm.history) == 0
    
    def test_state_machine_get_history_limit(self):
        """测试状态机历史记录限制"""
        sm = TaskStateMachine("TASK-001")
        
        sm.start()
        sm.complete()
        
        limited_history = sm.get_history(limit=1)
        assert len(limited_history) == 1
        assert limited_history[0].from_state == "running"  # 最后一条记录


class TestRuntimeSession:
    """运行会话测试"""
    
    def test_runtime_session_duration(self):
        """测试运行会话时长"""
        session = RuntimeSession(
            entity_id="SESSION-001",
            task_id="TASK-001",
            station_id=1,
            actor_id="ACTOR-001",
            start_time=time.time() - 2
        )
        
        assert session.duration_ms >= 2000  # 至少2秒
        
        # 测试结束后的时长
        session.end_time = session.start_time + 1  # 1秒后结束
        assert session.duration_ms == 1000  # 1000毫秒
    
    def test_runtime_session_entity_id(self):
        """测试运行会话实体ID"""
        session = RuntimeSession(
            entity_id="SESSION-001",
            task_id="TASK-001",
            station_id=1,
            actor_id="ACTOR-001",
            start_time=time.time()
        )
        
        assert session.id == "SESSION-001"


class TestTaskFlow:
    """任务流程测试"""
    
    def test_task_flow_advance_step(self):
        """测试任务流程推进步骤"""
        flow = TaskFlow(
            entity_id="FLOW-001",
            task_id="TASK-001",
            flow_name="test_flow",
            flow_config={},
            total_steps=3
        )
        
        assert flow.current_step == 0
        assert flow.is_completed() is False
        
        flow.advance_step({"result": "pass"})
        assert flow.current_step == 1
        assert len(flow.step_results) == 1
        
        flow.advance_step({"result": "fail"})
        assert flow.current_step == 2
        assert len(flow.step_results) == 2
        
        flow.advance_step({"result": "pass"})
        assert flow.current_step == 3
        assert flow.is_completed() is True
    
    def test_task_flow_entity_id(self):
        """测试任务流程实体ID"""
        flow = TaskFlow(
            entity_id="FLOW-001",
            task_id="TASK-001",
            flow_name="test_flow",
            flow_config={},
            total_steps=3
        )
        
        assert flow.id == "FLOW-001"


class TestDeviceMount:
    """设备挂载测试"""
    
    def test_device_mount_unmount(self):
        """测试设备挂载卸载"""
        mount = DeviceMount(
            entity_id="MOUNT-001",
            station_id="STATION-001",
            device_id="DEV-001",
            device_type="encoder",
            mount_time=time.time()
        )
        
        assert mount.is_active is True
        
        mount.unmount()
        assert mount.is_active is False
    
    def test_device_mount_entity_id(self):
        """测试设备挂载实体ID"""
        mount = DeviceMount(
            entity_id="MOUNT-001",
            station_id="STATION-001",
            device_id="DEV-001",
            device_type="encoder",
            mount_time=time.time()
        )
        
        assert mount.id == "MOUNT-001"


class TestGenerateId:
    """ID生成测试"""
    
    def test_generate_id(self):
        """测试ID生成"""
        id1 = generate_id("TEST")
        id2 = generate_id("TEST")
        
        assert id1.startswith("TEST-")
        assert id2.startswith("TEST-")
        assert id1 != id2
        
        # 测试无前缀
        id3 = generate_id()
        assert "-" in id3
        assert id3.startswith("ID-")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
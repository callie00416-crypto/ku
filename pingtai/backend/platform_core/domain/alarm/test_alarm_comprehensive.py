"""
告警领域单元测试 - Alarm Domain Unit Tests

【职责】
- 测试告警聚合根行为
- 测试告警状态机
- 测试告警生命周期
- 测试告警关联关系
- 测试告警异常情况
- 测试告警事件
"""
import pytest
import time

from encoder_test.domain.alarm import (
    Alarm, AlarmStateMachine, AlarmMetrics,
    AlarmLevel, AlarmStatus,
    AlarmException, AlarmNotFoundException, AlarmStatusTransitionException,
    AlarmAlreadyActiveException, AlarmAlreadyAcknowledgedException,
    AlarmAlreadyResolvedException, AlarmDeDuplicationException
)
from encoder_test.domain.alarm.events import (
    AlarmEventType, AlarmEvent, AlarmTriggeredEvent, AlarmAcknowledgedEvent,
    AlarmResolvedEvent, AlarmClosedEvent, AlarmReopenedEvent
)
from encoder_test.domain.common.enums import EventType


class TestAlarmCreation:
    """告警创建测试"""
    
    def test_alarm_create_basic(self):
        """测试基本告警创建"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败"
        )
        
        assert alarm.id.startswith("ALARM-")
        assert alarm.alarm_code == "CONN_ERR_001"
        assert alarm.alarm_level == AlarmLevel.ERROR
        assert alarm.message == "设备连接失败"
        assert alarm.status == AlarmStatus.ACTIVE  # 默认是ACTIVE状态
        assert alarm.version == 0
    
    def test_alarm_create_with_all_fields(self):
        """测试带所有字段的告警创建"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败",
            task_id="TASK-001",
            station_id="STATION-001",
            device_id="DEV-001",
            workorder_id="WO-001",
            source_type="device",
            source_id="SRC-001",
            metadata={"error_code": "E1001", "retry_count": 3}
        )
        
        assert alarm.task_id == "TASK-001"
        assert alarm.station_id == "STATION-001"
        assert alarm.device_id == "DEV-001"
        assert alarm.workorder_id == "WO-001"
        assert alarm.source_type == "device"
        assert alarm.source_id == "SRC-001"
        assert alarm.metadata["error_code"] == "E1001"
        assert alarm.metadata["retry_count"] == 3


class TestAlarmLifecycle:
    """告警生命周期测试"""
    
    def test_alarm_full_lifecycle(self):
        """测试告警完整生命周期"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败"
        )
        
        # 初始状态
        assert alarm.status == AlarmStatus.ACTIVE
        
        # 触发告警
        alarm.trigger(operator_id="OP-001")
        assert alarm.status == AlarmStatus.ACTIVE
        assert alarm.occurred_at is not None
        assert alarm.operator_id == "OP-001"
        assert alarm.version == 1
        
        # 确认告警
        alarm.acknowledge(operator_id="OP-002")
        assert alarm.status == AlarmStatus.ACKED
        assert alarm.acknowledged_at is not None
        assert alarm.ack_operator == "OP-002"
        assert alarm.version == 2
        
        # 解决告警
        alarm.resolve(operator_id="OP-003")
        assert alarm.status == AlarmStatus.RESOLVED
        assert alarm.resolved_at is not None
        assert alarm.resolve_operator == "OP-003"
        assert alarm.version == 3
        
        # 关闭告警
        alarm.close(operator_id="OP-004")
        assert alarm.status == AlarmStatus.CLOSED
        assert alarm.closed_at is not None
        assert alarm.close_operator == "OP-004"
        assert alarm.version == 4
    
    def test_alarm_trigger(self):
        """测试告警触发"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败"
        )
        
        alarm.trigger(operator_id="OP-001")
        
        assert alarm.status == AlarmStatus.ACTIVE
        assert alarm.occurred_at is not None
        assert alarm.operator_id == "OP-001"
        assert alarm.metrics.trigger_count == 1
        assert alarm.version == 1
    
    def test_alarm_acknowledge(self):
        """测试告警确认"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败"
        )
        
        alarm.trigger(operator_id="OP-001")
        alarm.acknowledge(operator_id="OP-002")
        
        assert alarm.status == AlarmStatus.ACKED
        assert alarm.acknowledged_at is not None
        assert alarm.ack_operator == "OP-002"
        assert alarm.metrics.ack_count == 1
        assert alarm.version == 2
    
    def test_alarm_resolve(self):
        """测试告警解决"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败"
        )
        
        alarm.trigger(operator_id="OP-001")
        alarm.acknowledge(operator_id="OP-002")
        alarm.resolve(operator_id="OP-003")
        
        assert alarm.status == AlarmStatus.RESOLVED
        assert alarm.resolved_at is not None
        assert alarm.resolve_operator == "OP-003"
        assert alarm.metrics.resolve_count == 1
        assert alarm.version == 3
    
    def test_alarm_close(self):
        """测试告警关闭"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败"
        )
        
        alarm.trigger(operator_id="OP-001")
        alarm.acknowledge(operator_id="OP-002")
        alarm.resolve(operator_id="OP-003")
        alarm.close(operator_id="OP-004")
        
        assert alarm.status == AlarmStatus.CLOSED
        assert alarm.closed_at is not None
        assert alarm.close_operator == "OP-004"
        assert alarm.metrics.close_count == 1
        assert alarm.version == 4


class TestAlarmMetrics:
    """告警指标测试"""
    
    def test_alarm_metrics_creation(self):
        """测试告警指标创建"""
        metrics = AlarmMetrics()
        
        assert metrics.trigger_count == 0
        assert metrics.ack_count == 0
        assert metrics.resolve_count == 0
        assert metrics.close_count == 0
    
    def test_alarm_metrics_updates(self):
        """测试告警指标更新"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败"
        )
        
        # 触发
        alarm.trigger(operator_id="OP-001")
        assert alarm.metrics.trigger_count == 1
        
        # 确认
        alarm.acknowledge(operator_id="OP-002")
        assert alarm.metrics.ack_count == 1
        
        # 解决
        alarm.resolve(operator_id="OP-003")
        assert alarm.metrics.resolve_count == 1
        
        # 关闭
        alarm.close(operator_id="OP-004")
        assert alarm.metrics.close_count == 1
    
    def test_alarm_metrics_immutability(self):
        """测试告警指标不可变性"""
        metrics1 = AlarmMetrics(trigger_count=1, ack_count=2)
        metrics2 = AlarmMetrics(trigger_count=1, ack_count=2)
        
        assert metrics1 == metrics2
        assert hash(metrics1) == hash(metrics2)


class TestAlarmStateMachine:
    """告警状态机测试"""
    
    def test_alarm_state_machine_initial(self):
        """测试告警状态机初始状态"""
        sm = AlarmStateMachine("ALARM-001")
        
        assert sm.current_state == "active"
    
    def test_alarm_state_machine_valid_transitions(self):
        """测试告警状态机合法转换"""
        sm = AlarmStateMachine("ALARM-001")
        
        # active -> acked
        sm.ack()
        assert sm.current_state == "acked"
        
        # acked -> resolved
        sm.resolve()
        assert sm.current_state == "resolved"
        
        # resolved -> closed
        sm.close()
        assert sm.current_state == "closed"
    
    def test_alarm_state_machine_multiple_paths(self):
        """测试告警状态机多种路径"""
        # 路径1: active -> resolved (跳过ack)
        sm1 = AlarmStateMachine("ALARM-001")
        sm1.resolve()  # Should work as per our transition rules
        assert sm1.current_state == "resolved"
        
        # 路径2: active -> closed (direct close)
        sm2 = AlarmStateMachine("ALARM-002")
        sm2.close()  # Should work as per our transition rules
        assert sm2.current_state == "closed"
    
    def test_alarm_state_machine_history(self):
        """测试告警状态机历史记录"""
        sm = AlarmStateMachine("ALARM-001")
        
        sm.ack()
        sm.resolve()
        sm.close()
        
        history = sm.history
        assert len(history) == 3  # ack, resolve, close
        
        assert history[0].from_state == "active"
        assert history[0].to_state == "acked"
        
        assert history[1].from_state == "acked"
        assert history[1].to_state == "resolved"
        
        assert history[2].from_state == "resolved"
        assert history[2].to_state == "closed"
    
    def test_alarm_state_machine_reset(self):
        """测试告警状态机重置"""
        sm = AlarmStateMachine("ALARM-001")
        
        sm.ack()
        sm.resolve()
        
        # Reset to original state
        sm.reset()
        
        assert sm.current_state == "active"
        assert len(sm.history) == 0


class TestAlarmEvents:
    """告警事件测试"""
    
    def test_alarm_triggered_event(self):
        """测试告警触发事件"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败",
            task_id="TASK-001",
            station_id="STATION-001"
        )
        
        # Trigger will create event internally
        alarm.trigger(operator_id="OP-001")
        
        events = alarm.pull_domain_events()
        assert len(events) == 1
        assert events[0]['event_type'] == EventType.ALARM_TRIGGERED
        assert events[0]['data']['alarm_code'] == "CONN_ERR_001"
    
    def test_alarm_acknowledged_event(self):
        """测试告警确认事件"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败"
        )
        
        alarm.trigger(operator_id="OP-001")
        alarm.acknowledge(operator_id="OP-002")
        
        events = alarm.pull_domain_events()
        # Should have 2 events: triggered + acknowledged
        assert len(events) >= 1  # At least acknowledged event
        
        # Find acknowledged event
        ack_events = [e for e in events if e['event_type'] == EventType.ALARM_ACKNOWLEDGED]
        assert len(ack_events) >= 1
        assert ack_events[0]['data']['ack_operator'] == "OP-002"
    
    def test_alarm_resolved_event(self):
        """测试告警解决事件"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败"
        )
        
        alarm.trigger(operator_id="OP-001")
        alarm.acknowledge(operator_id="OP-002")
        alarm.resolve(operator_id="OP-003")
        
        events = alarm.pull_domain_events()
        # Should have resolved event
        resolved_events = [e for e in events if e['event_type'] == EventType.ALARM_RESOLVED]
        assert len(resolved_events) >= 1
        assert resolved_events[0]['data']['resolve_operator'] == "OP-003"
    
    def test_alarm_closed_event(self):
        """测试告警关闭事件"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败"
        )
        
        alarm.trigger(operator_id="OP-001")
        alarm.acknowledge(operator_id="OP-002")
        alarm.resolve(operator_id="OP-003")
        alarm.close(operator_id="OP-004")
        
        events = alarm.pull_domain_events()
        # Should have closed event
        closed_events = [e for e in events if e['event_type'] == EventType.ALARM_CLOSED]
        assert len(closed_events) >= 1
        assert closed_events[0]['data']['close_operator'] == "OP-004"


class TestAlarmSerialization:
    """告警序列化测试"""
    
    def test_alarm_to_dict(self):
        """测试告警转字典"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败",
            task_id="TASK-001",
            station_id="STATION-001"
        )
        
        alarm.trigger(operator_id="OP-001")
        
        alarm_dict = alarm.to_dict()
        
        # Check all required fields exist
        assert 'id' in alarm_dict
        assert 'alarm_code' in alarm_dict
        assert 'alarm_level' in alarm_dict
        assert 'message' in alarm_dict
        assert 'task_id' in alarm_dict
        assert 'station_id' in alarm_dict
        assert 'status' in alarm_dict
        assert 'occurred_at' in alarm_dict
        assert 'metrics' in alarm_dict
        assert 'version' in alarm_dict
        
        # Check values
        assert alarm_dict['alarm_code'] == "CONN_ERR_001"
        assert alarm_dict['alarm_level'] == "error"
        assert alarm_dict['status'] == "active"
        assert alarm_dict['task_id'] == "TASK-001"
    
    def test_alarm_repr(self):
        """测试告警字符串表示"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败"
        )
        
        repr_str = repr(alarm)
        assert "Alarm" in repr_str
        assert "CONN_ERR_001" in repr_str
        assert "error" in repr_str
        assert "active" in repr_str


class TestAlarmEnums:
    """告警枚举测试"""
    
    def test_alarm_level_values(self):
        """测试告警等级值"""
        assert AlarmLevel.FATAL.value == "fatal"
        assert AlarmLevel.ERROR.value == "error"
        assert AlarmLevel.WARN.value == "warn"
        assert AlarmLevel.INFO.value == "info"
    
    def test_alarm_status_values(self):
        """测试告警状态值"""
        assert AlarmStatus.ACTIVE.value == "active"
        assert AlarmStatus.ACKED.value == "acked"
        assert AlarmStatus.RESOLVED.value == "resolved"
        assert AlarmStatus.CLOSED.value == "closed"


class TestAlarmExceptions:
    """告警异常测试"""
    
    def test_alarm_exceptions_creation(self):
        """测试告警异常创建"""
        # Test each exception type
        ex1 = AlarmNotFoundException("ALARM-001")
        assert "ALARM-001" in str(ex1)
        
        ex2 = AlarmStatusTransitionException("ALARM-001", "active", "invalid")
        assert "ALARM-001" in str(ex2)
        assert "active -> invalid" in str(ex2)
        
        ex3 = AlarmAlreadyActiveException("ALARM-001")
        assert "ALARM-001" in str(ex3)
        
        ex4 = AlarmAlreadyAcknowledgedException("ALARM-001")
        assert "ALARM-001" in str(ex4)
        
        ex5 = AlarmAlreadyResolvedException("ALARM-001")
        assert "ALARM-001" in str(ex5)
        
        ex6 = AlarmDeDuplicationException("DEV-001", "CODE-001", 300)
        assert "DEV-001" in str(ex6)
        assert "CODE-001" in str(ex6)


class TestAlarmEdgeCases:
    """告警边界情况测试"""
    
    def test_alarm_same_operator_all_steps(self):
        """测试同一操作员执行所有步骤"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败"
        )
        
        op_id = "OP-SAME"
        
        alarm.trigger(operator_id=op_id)
        assert alarm.operator_id == op_id
        
        alarm.acknowledge(operator_id=op_id)
        assert alarm.ack_operator == op_id
        
        alarm.resolve(operator_id=op_id)
        assert alarm.resolve_operator == op_id
        
        alarm.close(operator_id=op_id)
        assert alarm.close_operator == op_id
    
    def test_alarm_empty_metadata(self):
        """测试空元数据"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败"
        )
        
        assert alarm.metadata == {}
        
        alarm.trigger(operator_id="OP-001")
        assert isinstance(alarm.metadata, dict)
    
    def test_alarm_none_associations(self):
        """测试空关联字段"""
        alarm = Alarm.create(
            alarm_code="CONN_ERR_001",
            alarm_level=AlarmLevel.ERROR,
            message="设备连接失败"
        )
        
        assert alarm.task_id is None
        assert alarm.station_id is None
        assert alarm.device_id is None
        assert alarm.workorder_id is None
        assert alarm.source_type is None
        assert alarm.source_id is None


class TestAlarmEventsModule:
    """告警事件模块测试"""
    
    def test_alarm_triggered_event_creation(self):
        """测试告警触发事件创建"""
        event = AlarmTriggeredEvent(
            alarm_id="ALARM-001",
            alarm_code="CONN_ERR",
            alarm_level="error",
            message="Connection failed",
            occurred_at=time.time(),
            task_id="TASK-001",
            station_id="STATION-001",
            device_id="DEV-001",
            workorder_id="WO-001",
            metadata={"retry": 3}
        )
        
        assert event.event_type == AlarmEventType.ALARM_TRIGGERED
        assert event.alarm_id == "ALARM-001"
        assert event.data['alarm_code'] == "CONN_ERR"
        assert event.data['task_id'] == "TASK-001"
    
    def test_alarm_acknowledged_event_creation(self):
        """测试告警确认事件创建"""
        now = time.time()
        event = AlarmAcknowledgedEvent(
            alarm_id="ALARM-001",
            operator_id="OP-001",
            acknowledged_at=now,
            extra_data={"notes": "Checked connection"}
        )
        
        assert event.event_type == AlarmEventType.ALARM_ACKNOWLEDGED
        assert event.alarm_id == "ALARM-001"
        assert event.data['operator_id'] == "OP-001"
        assert event.data['extra_data']['notes'] == "Checked connection"
    
    def test_alarm_resolved_event_creation(self):
        """测试告警解决事件创建"""
        now = time.time()
        event = AlarmResolvedEvent(
            alarm_id="ALARM-001",
            operator_id="OP-001",
            resolved_at=now,
            resolution_notes="Fixed cable connection",
            extra_data={"fix_time": 120}
        )
        
        assert event.event_type == AlarmEventType.ALARM_RESOLVED
        assert event.alarm_id == "ALARM-001"
        assert event.data['resolution_notes'] == "Fixed cable connection"
    
    def test_alarm_closed_event_creation(self):
        """测试告警关闭事件创建"""
        now = time.time()
        event = AlarmClosedEvent(
            alarm_id="ALARM-001",
            operator_id="OP-001",
            closed_at=now,
            close_reason="Problem resolved",
            extra_data={"archive": True}
        )
        
        assert event.event_type == AlarmEventType.ALARM_CLOSED
        assert event.alarm_id == "ALARM-001"
        assert event.data['close_reason'] == "Problem resolved"
    
    def test_alarm_reopened_event_creation(self):
        """测试告警重开事件创建"""
        now = time.time()
        event = AlarmReopenedEvent(
            alarm_id="ALARM-001",
            operator_id="OP-001",
            reopened_at=now,
            reopen_reason="Problem reoccurred",
            extra_data={"incident_id": "INC-001"}
        )
        
        assert event.event_type == AlarmEventType.ALARM_REOPENED
        assert event.alarm_id == "ALARM-001"
        assert event.data['reopen_reason'] == "Problem reoccurred"
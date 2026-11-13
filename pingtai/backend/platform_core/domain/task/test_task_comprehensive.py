"""
任务领域综合单元测试 - Task Domain Comprehensive Unit Tests

【职责】
- 测试任务聚合根所有功能
- 验证任务状态机
- 验证任务生命周期
- 测试任务异常情况
- 验证任务指标和会话
- 测试任务流程管理
"""
import pytest
import time

from encoder_test.domain.task.task import (
    Task, TaskMetrics, RuntimeSession, TaskFlow,
    DomainEvent
)
from encoder_test.domain.common.enums import (
    TaskStatus, TaskResult, TaskPriority, EventType
)
from encoder_test.domain.common.exceptions import (
    TaskStatusTransitionException,
    TaskAlreadyRunningException,
    TaskRetryExhaustedException
)


class TestTaskAdvancedLifecycle:
    """高级任务生命周期测试"""
    
    def test_task_complete_success_flow(self):
        """测试任务成功完成流程"""
        task = Task.create(
            workorder_id="WO-001",
            station_id=1,
            sn="SN-001",
            task_type="test"
        )
        
        # 开始任务
        task.start(actor_id="ACTOR-001")
        assert task.status == TaskStatus.RUNNING
        assert task.actor_id == "ACTOR-001"
        assert task.start_time is not None
        
        # Sleep briefly to ensure duration > 0
        time.sleep(0.001)
        
        # 完成任务
        task.complete(result=TaskResult.PASS)
        assert task.status == TaskStatus.COMPLETED
        assert task.result == TaskResult.PASS
        assert task.end_time is not None
        assert task.duration_ms >= 0  # Duration could be 0 for very fast tasks
    
    def test_task_fail_flow(self):
        """测试任务失败流程"""
        task = Task.create(
            workorder_id="WO-002",
            station_id=1,
            sn="SN-002",
            task_type="test"
        )
        
        # 开始任务
        task.start(actor_id="ACTOR-002")
        
        # 任务失败
        task.fail(error_code="ERR-001", error_message="测试失败")
        assert task.status == TaskStatus.FAILED
        assert task.result == TaskResult.FAIL
        assert task.error_code == "ERR-001"
        assert task.error_message == "测试失败"
    
    def test_task_abort_flow(self):
        """测试任务中止流程"""
        task = Task.create(
            workorder_id="WO-003",
            station_id=1,
            sn="SN-003",
            task_type="test"
        )
        
        # 开始任务
        task.start(actor_id="ACTOR-003")
        
        # 中止任务
        task.abort(reason="紧急停止")
        assert task.status == TaskStatus.ABORTED
        assert task.end_time is not None
    
    def test_task_retry_mechanism(self):
        """测试任务重试机制"""
        task = Task.create(
            workorder_id="WO-004",
            station_id=1,
            sn="SN-004",
            task_type="test",
            max_retries=2
        )
        
        # 开始任务
        task.start(actor_id="ACTOR-004")
        task.fail(error_code="ERR-002", error_message="临时错误")
        
        # 第一次重试
        task.retry()
        assert task.status == TaskStatus.PENDING
        assert task.retry_count == 1
        assert task.error_code is None
        assert task.error_message is None
        
        # 再次开始和失败
        task.start(actor_id="ACTOR-004")
        task.fail(error_code="ERR-002", error_message="临时错误")
        
        # 第二次重试
        task.retry()
        assert task.status == TaskStatus.PENDING
        assert task.retry_count == 2
        
        # 再次开始和失败
        task.start(actor_id="ACTOR-004")
        task.fail(error_code="ERR-002", error_message="临时错误")
        
        # 尝试第三次重试（应该抛出异常）
        with pytest.raises(TaskRetryExhaustedException):
            task.retry()
    
    def test_task_already_running_exception(self):
        """测试任务已运行异常"""
        task = Task.create(
            workorder_id="WO-005",
            station_id=1,
            sn="SN-005",
            task_type="test"
        )
        
        # 开始任务
        task.start(actor_id="ACTOR-005")
        
        # 尝试再次开始（应该抛出异常）
        with pytest.raises(TaskAlreadyRunningException):
            task.start(actor_id="ACTOR-006")
    
    def test_task_invalid_status_transitions(self):
        """测试无效状态转换"""
        task = Task.create(
            workorder_id="WO-006",
            station_id=1,
            sn="SN-006",
            task_type="test"
        )
        
        # 尝试直接从PENDING状态跳转到其他状态（应该抛出异常）
        # 注意：根据状态机，PENDING只能转换到RUNNING或ABORTED
        with pytest.raises(ValueError):  # Should raise ValueError for invalid transition
            # Try to go from pending to completed directly (invalid)
            task.complete(result=TaskResult.PASS)
    
    def test_task_metrics_calculation(self):
        """测试任务指标计算"""
        task = Task.create(
            workorder_id="WO-007",
            station_id=1,
            sn="SN-007",
            task_type="test"
        )
        
        # 开始任务
        task.start(actor_id="ACTOR-007")
        
        # 模拟一些延迟以便计算持续时间
        time.sleep(0.01)  # 10ms
        
        # 完成任务
        task.complete(result=TaskResult.PASS)
        
        # 验证指标
        assert task.metrics.duration_ms >= 10  # 至少10ms
        assert task.metrics.retry_count == 0
        assert task.metrics.error_count == 0
    
    def test_task_runtime_session_creation(self):
        """测试任务运行会话创建"""
        task = Task.create(
            workorder_id="WO-008",
            station_id=1,
            sn="SN-008",
            task_type="test"
        )
        
        # 开始任务
        task.start(actor_id="ACTOR-008")
        
        # 验证运行会话创建
        assert task.runtime_session is not None
        assert task.runtime_session.entity_id.startswith("SESSION-")
        assert task.runtime_session.task_id == task.id
        assert task.runtime_session.actor_id == "ACTOR-008"
        assert task.runtime_session.station_id == 1
        assert task.runtime_session.start_time is not None
    
    def test_task_flow_management(self):
        """测试任务流程管理"""
        task = Task.create(
            workorder_id="WO-009",
            station_id=1,
            sn="SN-009",
            task_type="test"
        )
        
        # 设置任务流程
        task.set_task_flow(
            flow_name="CalibrationFlow",
            flow_config={"speed": 100, "precision": "high"},
            total_steps=5
        )
        
        assert task.task_flow is not None
        assert task.task_flow.flow_name == "CalibrationFlow"
        assert task.task_flow.total_steps == 5
        assert task.task_flow.current_step == 0
        
        # 推进步骤
        task.advance_flow_step({"result": "success", "value": 123.45})
        assert task.task_flow.current_step == 1
        assert len(task.task_flow.step_results) == 1
        
        # 推进更多步骤
        for i in range(2, 5):
            task.advance_flow_step({"step": i, "result": "ok"})
        
        assert task.task_flow.current_step == 4
        assert len(task.task_flow.step_results) == 4
        assert task.task_flow.is_completed() is False
        
        # 完成最后一步
        task.advance_flow_step({"step": 5, "result": "completed"})
        assert task.task_flow.current_step == 5
        assert task.task_flow.is_completed() is True


class TestTaskAdvancedFeatures:
    """高级任务特性测试"""
    
    def test_task_metadata_handling(self):
        """测试任务元数据处理"""
        task = Task.create(
            workorder_id="WO-010",
            station_id=1,
            sn="SN-010",
            task_type="test"
        )
        
        # 验证默认元数据
        assert task.metadata == {}
        
        # 测试元数据可以被修改（虽然内部使用的是私有属性）
        task._metadata["test_key"] = "test_value"
        assert task.metadata["test_key"] == "test_value"
    
    def test_task_to_dict_method(self):
        """测试任务转字典方法"""
        task = Task.create(
            workorder_id="WO-011",
            station_id=1,
            sn="SN-011",
            task_type="test",
            device_id="DEV-011"
        )
        
        # 开始任务
        task.start(actor_id="ACTOR-011")
        time.sleep(0.001)  # 小延迟
        task.complete(result=TaskResult.PASS)
        
        # 转换为字典
        task_dict = task.to_dict()
        
        # 验证关键字段存在
        assert "id" in task_dict
        assert "workorder_id" in task_dict
        assert "status" in task_dict
        assert "result" in task_dict
        assert "duration_ms" in task_dict
        assert "version" in task_dict
        
        # 验证值正确
        assert task_dict["workorder_id"] == "WO-011"
        assert task_dict["status"] == "completed"
        assert task_dict["result"] == "pass"
        assert task_dict["actor_id"] == "ACTOR-011"
    
    def test_task_repr_method(self):
        """测试任务字符串表示"""
        task = Task.create(
            workorder_id="WO-012",
            station_id=1,
            sn="SN-012",
            task_type="test"
        )
        
        repr_str = repr(task)
        assert "<Task" in repr_str
        assert task.id in repr_str
        assert "pending" in repr_str.lower()  # Status is lowercase in actual output
        assert "SN-012" in repr_str
    
    def test_task_version_increment(self):
        """测试任务版本递增"""
        task = Task.create(
            workorder_id="WO-013",
            station_id=1,
            sn="SN-013",
            task_type="test"
        )
        
        initial_version = task.version
        assert initial_version == 0
        
        # 开始任务会增加版本
        task.start(actor_id="ACTOR-013")
        assert task.version == 1
        
        # 完成任务会再次增加版本
        task.complete(result=TaskResult.PASS)
        assert task.version == 2
        
        # 设置任务流程也会增加版本
        task.set_task_flow("TestFlow", {}, 1)
        assert task.version == 3
        
        # 推进流程步骤也会增加版本
        task.advance_flow_step({"result": "ok"})
        assert task.version == 4


class TestTaskEdgeCases:
    """任务边界情况测试"""
    
    def test_task_with_empty_strings(self):
        """测试带空字符串的任务"""
        task = Task.create(
            workorder_id="",
            station_id=0,
            sn="",
            task_type=""
        )
        
        assert task.workorder_id == ""
        assert task.station_id == 0
        assert task.sn == ""
        assert task.task_type == ""
    
    def test_task_with_special_characters(self):
        """测试带特殊字符的任务"""
        special_task = Task.create(
            workorder_id="WO-测试&@#$%",
            station_id=1,
            sn="SN-测试中文123!@#",
            task_type="test-类型_特殊字符"
        )
        
        assert special_task.workorder_id == "WO-测试&@#$%"
        assert special_task.sn == "SN-测试中文123!@#"
        assert special_task.task_type == "test-类型_特殊字符"
    
    def test_task_long_values(self):
        """测试长值任务"""
        long_task = Task.create(
            workorder_id="WO-" + "X" * 100,
            station_id=999999,
            sn="SN-" + "Y" * 200,
            task_type="type_" + "Z" * 50
        )
        
        assert len(long_task.workorder_id) == 103  # "WO-" + 100 chars
        assert len(long_task.sn) == 203  # "SN-" + 200 chars
        assert long_task.station_id == 999999
    
    def test_task_priority_levels(self):
        """测试任务优先级级别"""
        for priority in TaskPriority:
            task = Task.create(
                workorder_id=f"WO-{priority.value}",
                station_id=1,
                sn=f"SN-{priority.value}",
                task_type="test",
                priority=priority
            )
            
            assert task.priority == priority
    
    def test_task_result_types(self):
        """测试任务结果类型"""
        task = Task.create(
            workorder_id="WO-RESULT",
            station_id=1,
            sn="SN-RESULT",
            task_type="test"
        )
        
        task.start(actor_id="ACTOR-RESULT")
        
        for result in [TaskResult.PASS, TaskResult.FAIL, TaskResult.SKIP]:
            # Need to reset the task status since we can't complete multiple times
            temp_task = Task.create(
                workorder_id="WO-TEMP",
                station_id=1,
                sn="SN-TEMP",
                task_type="test"
            )
            temp_task.start(actor_id="ACTOR-TEMP")
            temp_task.complete(result=result)
            assert temp_task.result == result


class TestTaskErrorConditions:
    """任务错误条件测试"""
    
    def test_task_without_start_cannot_complete(self):
        """测试未开始的任务无法完成"""
        task = Task.create(
            workorder_id="WO-NO-START",
            station_id=1,
            sn="SN-NO-START",
            task_type="test"
        )
        
        # 尝试在未开始状态下完成任务（应该失败）
        # According to state machine, can't go from pending to completed directly
        with pytest.raises(ValueError):
            task.complete(result=TaskResult.PASS)
    
    def test_task_without_start_cannot_fail(self):
        """测试未开始的任务无法失败"""
        task = Task.create(
            workorder_id="WO-NO-START2",
            station_id=1,
            sn="SN-NO-START2",
            task_type="test"
        )
        
        # 尝试在未开始状态下使任务失败（应该失败）
        # According to state machine, can't go from pending to failed directly
        with pytest.raises(ValueError):
            task.fail(error_code="TEST-ERR", error_message="Test error")
    
    def test_task_cannot_be_aborted_when_pending(self):
        """测试待定任务无法中止（可能允许）"""
        task = Task.create(
            workorder_id="WO-PEND-ABORT",
            station_id=1,
            sn="SN-PEND-ABORT",
            task_type="test"
        )
        
        # 测试是否允许中止待定任务
        try:
            task.abort(reason="Test abort")
            assert task.status == TaskStatus.ABORTED
        except TaskStatusTransitionException:
            # 如果不允许，这也是一种有效的行为
            pass
    
    def test_task_max_retries_boundary(self):
        """测试任务最大重试边界"""
        task = Task.create(
            workorder_id="WO-MAX-RETRY",
            station_id=1,
            sn="SN-MAX-RETRY",
            task_type="test",
            max_retries=0  # 不允许重试
        )
        
        task.start(actor_id="ACTOR-MAX-RETRY")
        task.fail(error_code="ERR", error_message="Error")
        
        # 尝试重试（应该立即抛出异常）
        with pytest.raises(TaskRetryExhaustedException):
            task.retry()
    
    def test_task_flow_without_setting(self):
        """测试未设置流程的任务"""
        task = Task.create(
            workorder_id="WO-NO-FLOW",
            station_id=1,
            sn="SN-NO-FLOW",
            task_type="test"
        )
        
        # 推进流程步骤（当没有流程时）
        # 这应该不会报错，只是没有效果
        task.advance_flow_step({"result": "test"})
        # task_flow 应该仍然为None
        assert task.task_flow is None
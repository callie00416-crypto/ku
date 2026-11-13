"""
任务领域单元测试 - Task Domain Unit Tests

【职责】
- 测试任务基本创建功能
- 测试任务状态转换
- 测试任务生命周期
- 验证任务属性
"""
import pytest
import time

from platform.domain.task.task import (
    Task, TaskMetrics, RuntimeSession, TaskFlow,
    DomainEvent
)
from platform.domain.common.enums import (
    TaskStatus, TaskResult, TaskPriority, EventType
)
from platform.domain.common.exceptions import (
    TaskStatusTransitionException,
    TaskAlreadyRunningException,
    TaskRetryExhaustedException
)


class TestTaskBasicCreation:
    """任务基本创建测试"""
    
    def test_task_create_basic(self):
        """测试基本任务创建"""
        task = Task.create(
            workorder_id="WO-001",
            station_id=1,
            sn="SN-001",
            task_type="test"
        )
        
        assert task.id.startswith("TASK-")
        assert task.workorder_id == "WO-001"
        assert task.station_id == 1
        assert task.sn == "SN-001"
        assert task.task_type == "test"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.NORMAL
        assert task.max_retries == 3
        assert task.retry_count == 0
        assert task.version == 0
    
    def test_task_create_with_optional_params(self):
        """测试带可选参数的任务创建"""
        task = Task.create(
            workorder_id="WO-002",
            station_id=2,
            sn="SN-002",
            task_type="calibration",
            device_id="DEV-001",
            priority=TaskPriority.HIGH,
            max_retries=5
        )
        
        assert task.workorder_id == "WO-002"
        assert task.device_id == "DEV-001"
        assert task.priority == TaskPriority.HIGH
        assert task.max_retries == 5
"""
任务领域 - Task Domain（工业核心聚合）

【职责】
- Task 是工业平台核心聚合
- 管理测试任务完整生命周期
- 保证任务状态转换合法性
- 支持重试、失败恢复、幂等性

【核心能力】
- 状态流转
- 工艺流程
- retry/fail/result
- runtime session
- actor绑定

【设计原则】
- Task 是聚合根，唯一标识
- 所有状态转换必须通过领域方法
- 支持乐观锁（version字段）
- 支持领域事件
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import time

from ..common.aggregate_root import AggregateRoot, ValueObject, Entity, generate_id
from ..common.enums import TaskStatus, TaskResult, TaskPriority, EventType
from ..common.exceptions import (
    TaskStatusTransitionException,
    TaskAlreadyRunningException,
    TaskRetryExhaustedException
)
from ..common.state_machine import TaskStateMachine


@dataclass
class TaskMetrics(ValueObject):
    """任务指标（值对象）
    
    【职责】
    - 记录任务运行指标
    - 不可变
    """
    duration_ms: int = 0
    step_count: int = 0
    retry_count: int = 0
    error_count: int = 0


@dataclass
class RuntimeSession(Entity):
    """运行会话（实体）
    
    【职责】
    - 记录任务运行会话
    - 支持会话追踪
    """
    entity_id: str
    task_id: str
    station_id: int
    actor_id: str
    start_time: float
    end_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        Entity.__init__(self, self.entity_id)
    
    @property
    def duration_ms(self) -> int:
        """获取运行时长（毫秒）"""
        if self.end_time:
            return int((self.end_time - self.start_time) * 1000)
        return int((time.time() - self.start_time) * 1000)


@dataclass
class TaskFlow(Entity):
    """任务流程（实体）
    
    【职责】
    - 定义任务工艺流程
    - 记录流程执行状态
    """
    entity_id: str
    task_id: str
    flow_name: str
    flow_config: Dict[str, Any]
    current_step: int = 0
    total_steps: int = 0
    step_results: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        Entity.__init__(self, self.entity_id)
    
    def advance_step(self, result: Dict[str, Any] = None):
        """推进到下一步"""
        if result:
            self.step_results.append(result)
        self.current_step += 1
    
    def is_completed(self) -> bool:
        """是否完成"""
        return self.current_step >= self.total_steps


@dataclass
class DomainEvent:
    """领域事件
    
    【职责】
    - 记录领域事件
    - 支持事件溯源
    """
    event_type: EventType
    aggregate_id: str
    aggregate_type: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default_factory=lambda: generate_id("EVT"))


class Task(AggregateRoot):
    """任务聚合根（工业核心）
    
    【职责】
    - 管理任务完整生命周期
    - 保证状态转换合法性
    - 支持重试、失败恢复
    - 发布领域事件
    
    【状态流转】
    pending -> running -> completed/failed/aborted
    
    【核心方法】
    - start(): 开始任务
    - complete(): 完成任务
    - fail(): 任务失败
    - abort(): 中止任务
    - retry(): 重试任务
    
    【使用示例】
    >>> task = Task.create(
    ...     workorder_id="WO-001",
    ...     station_id=1,
    ...     sn="SN123456",
    ...     task_type="encoder_accuracy"
    ... )
    >>> task.start(actor_id="ACTOR-001")
    >>> task.complete(result=TaskResult.PASS)
    """
    
    def __init__(self, task_id: str):
        """
        Args:
            task_id: 任务ID
        """
        super().__init__(task_id)
        
        self._workorder_id: Optional[str] = None
        self._station_id: Optional[int] = None
        self._device_id: Optional[str] = None
        self._sn: Optional[str] = None
        self._task_type: Optional[str] = None
        
        self._status = TaskStatus.PENDING
        self._result: Optional[TaskResult] = None
        self._priority = TaskPriority.NORMAL
        
        self._retry_count = 0
        self._max_retries = 3
        self._error_code: Optional[str] = None
        self._error_message: Optional[str] = None
        
        self._actor_id: Optional[str] = None
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None
        
        self._metrics = TaskMetrics()
        self._runtime_session: Optional[RuntimeSession] = None
        self._task_flow: Optional[TaskFlow] = None
        self._metadata: Dict[str, Any] = {}
        
        self._state_machine = TaskStateMachine(task_id)
    
    @property
    def workorder_id(self) -> Optional[str]:
        return self._workorder_id
    
    @property
    def station_id(self) -> Optional[int]:
        return self._station_id
    
    @property
    def device_id(self) -> Optional[str]:
        return self._device_id
    
    @property
    def sn(self) -> Optional[str]:
        return self._sn
    
    @property
    def task_type(self) -> Optional[str]:
        return self._task_type
    
    @property
    def status(self) -> TaskStatus:
        return self._status
    
    @property
    def result(self) -> Optional[TaskResult]:
        return self._result
    
    @property
    def priority(self) -> TaskPriority:
        return self._priority
    
    @property
    def retry_count(self) -> int:
        return self._retry_count
    
    @property
    def max_retries(self) -> int:
        return self._max_retries
    
    @property
    def error_code(self) -> Optional[str]:
        return self._error_code
    
    @property
    def error_message(self) -> Optional[str]:
        return self._error_message
    
    @property
    def actor_id(self) -> Optional[str]:
        return self._actor_id
    
    @property
    def start_time(self) -> Optional[float]:
        return self._start_time
    
    @property
    def end_time(self) -> Optional[float]:
        return self._end_time
    
    @property
    def duration_ms(self) -> int:
        """获取任务时长（毫秒）"""
        if self._start_time and self._end_time:
            return int((self._end_time - self._start_time) * 1000)
        return 0
    
    @property
    def metrics(self) -> TaskMetrics:
        return self._metrics
    
    @property
    def runtime_session(self) -> Optional[RuntimeSession]:
        return self._runtime_session
    
    @property
    def task_flow(self) -> Optional[TaskFlow]:
        return self._task_flow
    
    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata
    
    @classmethod
    def create(cls, workorder_id: str, station_id: int, sn: str, 
               task_type: str, device_id: str = None, 
               priority: TaskPriority = TaskPriority.NORMAL,
               max_retries: int = 3) -> 'Task':
        """创建任务（工厂方法）
        
        Args:
            workorder_id: 工单ID
            station_id: 工位ID
            sn: 产品SN码
            task_type: 任务类型
            device_id: 设备ID
            priority: 优先级
            max_retries: 最大重试次数
            
        Returns:
            Task实例
        """
        task_id = generate_id("TASK")
        task = cls(task_id)
        
        task._workorder_id = workorder_id
        task._station_id = station_id
        task._device_id = device_id
        task._sn = sn
        task._task_type = task_type
        task._priority = priority
        task._max_retries = max_retries
        
        # 发布领域事件
        task._add_domain_event(DomainEvent(
            event_type=EventType.TASK_CREATED,
            aggregate_id=task_id,
            aggregate_type="Task",
            data={
                'workorder_id': workorder_id,
                'station_id': station_id,
                'sn': sn,
                'task_type': task_type
            }
        ))
        
        return task
    
    def start(self, actor_id: str) -> None:
        """开始任务
        
        Args:
            actor_id: 执行者ID
            
        Raises:
            TaskAlreadyRunningException: 任务已在运行
            TaskStatusTransitionException: 状态转换非法
        """
        if self._status == TaskStatus.RUNNING:
            raise TaskAlreadyRunningException(self._id)
        
        # 状态转换
        self._state_machine.start()
        self._status = TaskStatus.RUNNING
        
        # 更新字段
        self._actor_id = actor_id
        self._start_time = time.time()
        
        # 创建运行会话
        self._runtime_session = RuntimeSession(
            entity_id=generate_id("SESSION"),
            task_id=self._id,
            station_id=self._station_id,
            actor_id=actor_id,
            start_time=self._start_time
        )
        
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event(DomainEvent(
            event_type=EventType.TASK_STARTED,
            aggregate_id=self._id,
            aggregate_type="Task",
            data={'actor_id': actor_id}
        ))
    
    def complete(self, result: TaskResult = TaskResult.PASS) -> None:
        """完成任务
        
        Args:
            result: 任务结果
            
        Raises:
            TaskStatusTransitionException: 状态转换非法
        """
        self._state_machine.complete()
        self._status = TaskStatus.COMPLETED
        self._result = result
        self._end_time = time.time()
        
        # 更新运行会话
        if self._runtime_session:
            self._runtime_session.end_time = self._end_time
        
        # 更新指标
        self._metrics = TaskMetrics(
            duration_ms=self.duration_ms,
            step_count=self._task_flow.current_step if self._task_flow else 0,
            retry_count=self._retry_count,
            error_count=self._metrics.error_count
        )
        
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event(DomainEvent(
            event_type=EventType.TASK_COMPLETED,
            aggregate_id=self._id,
            aggregate_type="Task",
            data={'result': result.value}
        ))
    
    def fail(self, error_code: str, error_message: str) -> None:
        """任务失败
        
        Args:
            error_code: 错误码
            error_message: 错误信息
            
        Raises:
            TaskStatusTransitionException: 状态转换非法
        """
        self._state_machine.fail(error_message)
        self._status = TaskStatus.FAILED
        self._result = TaskResult.FAIL
        self._error_code = error_code
        self._error_message = error_message
        self._end_time = time.time()
        
        # 更新运行会话
        if self._runtime_session:
            self._runtime_session.end_time = self._end_time
        
        # 更新指标
        self._metrics = TaskMetrics(
            duration_ms=self.duration_ms,
            step_count=self._task_flow.current_step if self._task_flow else 0,
            retry_count=self._retry_count,
            error_count=self._metrics.error_count + 1
        )
        
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event(DomainEvent(
            event_type=EventType.TASK_FAILED,
            aggregate_id=self._id,
            aggregate_type="Task",
            data={
                'error_code': error_code,
                'error_message': error_message
            }
        ))
    
    def abort(self, reason: str = "") -> None:
        """中止任务
        
        Args:
            reason: 中止原因
        """
        self._state_machine.abort(reason)
        self._status = TaskStatus.ABORTED
        self._end_time = time.time()
        
        # 更新运行会话
        if self._runtime_session:
            self._runtime_session.end_time = self._end_time
        
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event(DomainEvent(
            event_type=EventType.TASK_ABORTED,
            aggregate_id=self._id,
            aggregate_type="Task",
            data={'reason': reason}
        ))
    
    def retry(self) -> None:
        """重试任务
        
        Raises:
            TaskRetryExhaustedException: 重试次数耗尽
        """
        if self._retry_count >= self._max_retries:
            raise TaskRetryExhaustedException(
                self._id,
                self._retry_count,
                self._max_retries
            )
        
        self._state_machine.retry()
        self._status = TaskStatus.PENDING
        self._retry_count += 1
        self._error_code = None
        self._error_message = None
        self._start_time = None
        self._end_time = None
        
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event(DomainEvent(
            event_type=EventType.TASK_RETRY,
            aggregate_id=self._id,
            aggregate_type="Task",
            data={'retry_count': self._retry_count}
        ))
    
    def set_task_flow(self, flow_name: str, flow_config: Dict[str, Any], 
                      total_steps: int) -> None:
        """设置任务流程
        
        Args:
            flow_name: 流程名称
            flow_config: 流程配置
            total_steps: 总步骤数
        """
        self._task_flow = TaskFlow(
            entity_id=generate_id("FLOW"),
            task_id=self._id,
            flow_name=flow_name,
            flow_config=flow_config,
            total_steps=total_steps
        )
        self._increment_version()
    
    def advance_flow_step(self, result: Dict[str, Any] = None) -> None:
        """推进流程步骤
        
        Args:
            result: 步骤结果
        """
        if self._task_flow:
            self._task_flow.advance_step(result)
            self._increment_version()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            任务信息字典
        """
        return {
            'id': self._id,
            'workorder_id': self._workorder_id,
            'station_id': self._station_id,
            'device_id': self._device_id,
            'sn': self._sn,
            'task_type': self._task_type,
            'status': self._status.value,
            'result': self._result.value if self._result else None,
            'priority': self._priority.value,
            'retry_count': self._retry_count,
            'max_retries': self._max_retries,
            'error_code': self._error_code,
            'error_message': self._error_message,
            'actor_id': self._actor_id,
            'start_time': self._start_time,
            'end_time': self._end_time,
            'duration_ms': self.duration_ms,
            'version': self.version,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metrics': {
                'duration_ms': self._metrics.duration_ms,
                'step_count': self._metrics.step_count,
                'retry_count': self._metrics.retry_count,
                'error_count': self._metrics.error_count
            }
        }
    
    def __repr__(self) -> str:
        return f"<Task id={self._id} status={self._status.value} sn={self._sn}>"
"""
BaseFlow - 流程基类

所属层级：Flow 层
职责：定义所有业务流程的标准接口

Flow = Action容器 = 业务流程

使用示例：
>>> class StartupFlow(BaseFlow):
...     def setup(self):
...         self.add(PowerOnAction(power, voltage=5.0))
...         self.add(DelayAction(delay=2.0))
...         self.add(MotorHomeAction(motor))
...
>>> flow = StartupFlow()
>>> results = flow.execute()
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
import time
from dataclasses import dataclass, field

from projects.encoder_test.actions.base.base_action import BaseAction
from projects.encoder_test.actions.base.action_result import ActionResult

logger = logging.getLogger(__name__)


class FlowState:
    """流程状态"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    STOPPED = "stopped"
    PAUSED = "paused"


@dataclass
class FlowResult:
    """流程执行结果"""
    success: bool = True
    state: str = FlowState.IDLE
    message: str = ""
    action_results: List[Dict[str, Any]] = field(default_factory=list)
    duration: float = 0.0
    failed_action: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'state': self.state,
            'message': self.message,
            'action_results': self.action_results,
            'duration': self.duration,
            'failed_action': self.failed_action
        }


class BaseFlow(ABC):
    """流程基类
    
    Flow = Action容器 = 业务流程
    
    【职责】
    - 管理 Action 序列
    - 执行流程
    - 失败回滚
    - 状态管理
    
    【使用示例】
    >>> class StartupFlow(BaseFlow):
    ...     def setup(self):
    ...         self.add(PowerOnAction(power))
    ...         self.add(DelayAction(delay=2.0))
    ...
    >>> flow = StartupFlow()
    >>> result = flow.execute()
    """
    
    def __init__(self, flow_id: str = None, timeout: float = 300.0, **kwargs):
        """
        Args:
            flow_id: 流程唯一标识
            timeout: 超时时间（秒）
        """
        self.flow_id = flow_id or self.__class__.__name__
        self.timeout = timeout
        
        self._actions: List[BaseAction] = []
        self._state = FlowState.IDLE
        self._results: List[ActionResult] = []
        self._start_time: float = 0.0
        self._end_time: float = 0.0
        self._current_index: int = 0
        self._is_stopping: bool = False
        
        self._context: Dict[str, Any] = {}
        
        self.setup()
    
    @property
    def state(self) -> str:
        """获取当前状态"""
        return self._state
    
    @property
    def is_running(self) -> bool:
        return self._state == FlowState.RUNNING
    
    @property
    def duration(self) -> float:
        if self._end_time and self._start_time:
            return self._end_time - self._start_time
        return 0.0
    
    @property
    def action_count(self) -> int:
        return len(self._actions)
    
    @abstractmethod
    def setup(self):
        """设置流程动作（子类实现）
        
        在此方法中添加所有需要的 Action
        
        示例：
        def setup(self):
            self.add(PowerOnAction(self.power))
            self.add(DelayAction(delay=2.0))
        """
        pass
    
    def add(self, action: BaseAction) -> 'BaseFlow':
        """添加 Action（支持链式调用）
        
        Returns:
            self: 返回自身，支持链式调用
        """
        self._actions.append(action)
        return self
    
    def insert(self, index: int, action: BaseAction) -> 'BaseFlow':
        """在指定位置插入 Action"""
        self._actions.insert(index, action)
        return self
    
    def clear(self):
        """清空所有 Action"""
        self._actions.clear()
        self._results.clear()
    
    def get_action(self, index: int) -> Optional[BaseAction]:
        """获取指定位置的 Action"""
        if 0 <= index < len(self._actions):
            return self._actions[index]
        return None
    
    def set_context(self, key: str, value: Any):
        """设置上下文"""
        self._context[key] = value
    
    def get_context(self, key: str, default=None) -> Any:
        """获取上下文"""
        return self._context.get(key, default)
    
    def execute(self) -> FlowResult:
        """执行流程
        
        Returns:
            FlowResult: 流程执行结果
        """
        logger.info(f"[{self.flow_id}] 开始执行流程, 共 {len(self._actions)} 个动作")
        
        self._start_time = time.time()
        self._state = FlowState.RUNNING
        self._results.clear()
        self._current_index = 0
        self._is_stopping = False
        
        flow_result = FlowResult(state=FlowState.RUNNING)
        
        try:
            for i, action in enumerate(self._actions):
                if self._is_stopping:
                    logger.warning(f"[{self.flow_id}] 流程被停止")
                    self._state = FlowState.STOPPED
                    flow_result.state = FlowState.STOPPED
                    flow_result.success = False
                    flow_result.message = "流程被停止"
                    break
                
                self._current_index = i
                
                logger.info(f"[{self.flow_id}] 执行动作 {i+1}/{len(self._actions)}: {action.action_id}")
                
                result = action.execute()
                self._results.append(result)
                
                flow_result.action_results.append({
                    'index': i,
                    'action_id': action.action_id,
                    'success': result.is_success(),
                    'message': result.message,
                    'duration': result.duration
                })
                
                if result.is_failed():
                    logger.error(f"[{self.flow_id}] 动作失败: {action.action_id}")
                    self._state = FlowState.FAILED
                    flow_result.state = FlowState.FAILED
                    flow_result.success = False
                    flow_result.message = f"动作 {action.action_id} 失败: {result.message}"
                    flow_result.failed_action = action.action_id
                    
                    logger.info(f"[{self.flow_id}] 开始回滚")
                    self.rollback()
                    flow_result.state = FlowState.ROLLING_BACK
                    break
            else:
                self._state = FlowState.SUCCESS
                flow_result.state = FlowState.SUCCESS
                flow_result.success = True
                flow_result.message = f"流程执行成功, 共 {len(self._actions)} 个动作"
            
        except Exception as e:
            logger.exception(f"[{self.flow_id}] 流程执行异常")
            self._state = FlowState.FAILED
            flow_result.state = FlowState.FAILED
            flow_result.success = False
            flow_result.message = f"流程执行异常: {str(e)}"
        
        finally:
            self._end_time = time.time()
            flow_result.duration = self.duration
        
        logger.info(f"[{self.flow_id}] 流程执行完成: {flow_result.state}, 耗时: {flow_result.duration:.2f}s")
        
        return flow_result
    
    def rollback(self):
        """回滚流程
        
        按逆序执行所有已执行动作的回滚
        """
        logger.info(f"[{self.flow_id}] 开始回滚, 共 {self._current_index + 1} 个动作")
        self._state = FlowState.ROLLING_BACK
        
        for i in range(self._current_index, -1, -1):
            action = self._actions[i]
            try:
                action.rollback()
                logger.info(f"[{self.flow_id}] 回滚动作: {action.action_id}")
            except Exception as e:
                logger.error(f"[{self.flow_id}] 回滚动作失败: {action.action_id}, {e}")
        
        logger.info(f"[{self.flow_id}] 回滚完成")
    
    def stop(self):
        """停止流程"""
        logger.info(f"[{self.flow_id}] 收到停止信号")
        self._is_stopping = True
        
        for action in self._actions:
            action.stop()
    
    def pause(self):
        """暂停流程"""
        self._state = FlowState.PAUSED
        logger.info(f"[{self.flow_id}] 流程暂停")
    
    def resume(self):
        """恢复流程"""
        if self._state == FlowState.PAUSED:
            self._state = FlowState.RUNNING
            logger.info(f"[{self.flow_id}] 流程恢复")
    
    def get_results(self) -> List[ActionResult]:
        """获取所有 Action 的执行结果"""
        return self._results.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """获取流程执行摘要"""
        total = len(self._results)
        success = sum(1 for r in self._results if r.is_success())
        failed = sum(1 for r in self._results if r.is_failed())
        
        return {
            'flow_id': self.flow_id,
            'state': self._state,
            'total_actions': total,
            'success_count': success,
            'failed_count': failed,
            'duration': self.duration,
            'current_action': self._current_index
        }
    
    def __repr__(self):
        return f"<{self.__class__.__name__}[{self._state}] actions={len(self._actions)}>"


class SequenceFlow(BaseFlow):
    """序列流程（通用）
    
    简单的 Action 序列执行
    
    使用示例：
    >>> flow = SequenceFlow(flow_id="test")
    >>> flow.add(PowerOnAction(power))
    >>> flow.add(DelayAction(delay=1.0))
    >>> flow.add(EncoderReadAction(encoder))
    >>> result = flow.execute()
    """
    
    def setup(self):
        """序列流程不需要预定义动作，可直接用 add() 添加"""
        pass


class ConditionalFlow(BaseFlow):
    """条件流程（支持条件判断）
    
    根据条件决定是否执行某些 Action
    """
    
    def __init__(self, flow_id: str = None, timeout: float = 300.0, **kwargs):
        super().__init__(flow_id, timeout, **kwargs)
        self._conditions: Dict[str, bool] = {}
    
    def setup(self):
        """条件流程不需要预定义动作"""
        pass
    
    def set_condition(self, name: str, value: bool):
        """设置条件"""
        self._conditions[name] = value
    
    def get_condition(self, name: str) -> bool:
        """获取条件"""
        return self._conditions.get(name, False)
    
    def add_if(self, condition_name: str, action: BaseAction):
        """条件添加 Action"""
        if self.get_condition(condition_name):
            self.add(action)
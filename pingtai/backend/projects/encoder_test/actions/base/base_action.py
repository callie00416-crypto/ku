"""
BaseAction - 动作基类（完整版）

所属层级：Action 层
职责：定义所有工业动作的标准接口和生命周期

生命周期：
before_run() -> run() -> after_run() -> cleanup()

回滚机制：
rollback() - 失败时回滚到之前状态

统一执行：
统一使用 execute() 而非 run()

使用示例：
>>> class PowerOnAction(BaseAction):
...     def run(self):
...         self.device.connect()
...         return ActionResult.success()
...
>>> action = PowerOnAction(device=ps)
>>> result = action.execute()  # 统一用 execute()
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, List
import logging
import time

from projects.encoder_test.actions.base.action_result import ActionResult, ResultStatus

logger = logging.getLogger(__name__)


class ActionState:
    """动作状态"""
    IDLE = "idle"
    BEFORE_RUNNING = "before_running"
    RUNNING = "running"
    AFTER_RUNNING = "after_running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    STOPPING = "stopping"
    STOPPED = "stopped"
    CLEANING_UP = "cleaning_up"
    CLEANED = "cleaned"


class BaseAction(ABC):
    """动作基类（完整生命周期）
    
    【生命周期】
    execute()
        ├── before_run()      # 执行前钩子
        ├── run()             # 核心动作（子类必须实现）
        ├── after_run()      # 执行后钩子
        └── cleanup()        # 清理钩子
    
    【回滚机制】
    rollback() - 失败时回滚
    
    【停止机制】
    stop() - 停止执行
    
    【使用示例】
    >>> class PowerOnAction(BaseAction):
    ...     def run(self):
    ...         self.device.connect()
    ...         return ActionResult.success()
    ...
    >>> action = PowerOnAction(device=ps)
    >>> result = action.execute()
    """
    
    def __init__(
        self,
        action_id: str = None,
        timeout: float = 30.0,
        retry_on_fail: bool = False,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Args:
            action_id: 动作唯一标识
            timeout: 超时时间（秒）
            retry_on_fail: 失败时是否重试
            max_retries: 最大重试次数
        """
        self.action_id = action_id or self.__class__.__name__
        self.timeout = timeout
        self.retry_on_fail = retry_on_fail
        self.max_retries = max_retries
        
        self._state = ActionState.IDLE
        self._result: Optional[ActionResult] = None
        self._start_time: float = 0.0
        self._end_time: float = 0.0
        self._rollback_handlers: List[Callable] = []
        self._is_stopping = False
        
        self._context: Dict[str, Any] = {}
        self._device: Any = None
        self._parent_action: 'BaseAction' = None
    
    @property
    def state(self) -> str:
        """获取当前状态"""
        return self._state
    
    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._state in [ActionState.RUNNING, ActionState.BEFORE_RUNNING, ActionState.AFTER_RUNNING]
    
    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self._state == ActionState.SUCCESS
    
    @property
    def is_failed(self) -> bool:
        """是否失败"""
        return self._state in [ActionState.FAILED, ActionState.STOPPED]
    
    @property
    def duration(self) -> float:
        """执行时长"""
        if self._end_time and self._start_time:
            return self._end_time - self._start_time
        return 0.0
    
    def set_device(self, device: Any):
        """设置关联设备"""
        self._device = device
    
    def get_device(self) -> Any:
        """获取关联设备"""
        return self._device
    
    def set_context(self, key: str, value: Any):
        """设置上下文"""
        self._context[key] = value
    
    def get_context(self, key: str, default=None) -> Any:
        """获取上下文"""
        return self._context.get(key, default)
    
    def add_rollback(self, handler: Callable):
        """添加回滚处理器"""
        self._rollback_handlers.append(handler)
    
    def execute(self) -> ActionResult:
        """统一执行入口（替代原来的 run）
        
        包含完整生命周期：
        1. before_run() - 执行前
        2. run() - 核心动作
        3. after_run() - 执行后
        4. cleanup() - 清理
        """
        logger.info(f"[{self.action_id}] 开始执行")
        self._start_time = time.time()
        self._is_stopping = False
        self._rollback_handlers.clear()
        
        try:
            self._state = ActionState.BEFORE_RUNNING
            self.before_run()
            
            self._state = ActionState.RUNNING
            self._result = self.run()
            
            self._state = ActionState.AFTER_RUNNING
            self.after_run()
            
            if self._result and self._result.is_success():
                self._state = ActionState.SUCCESS
                logger.info(f"[{self.action_id}] 执行成功: {self._result.message}")
            else:
                self._state = ActionState.FAILED
                logger.error(f"[{self.action_id}] 执行失败: {self._result.message if self._result else 'Unknown'}")
            
        except Exception as e:
            self._state = ActionState.FAILED
            self._result = ActionResult.failed(
                message=f"执行异常: {str(e)}",
                error_detail=str(e)
            )
            logger.exception(f"[{self.action_id}] 执行异常")
        
        finally:
            self._end_time = time.time()
            self._state = ActionState.CLEANING_UP
            self.cleanup()
            self._state = ActionState.CLEANED
        
        self._result.duration = self.duration
        return self._result
    
    def before_run(self):
        """执行前钩子（可重写）
        
        可用于：
        - 参数校验
        - 状态检查
        - 日志记录
        """
        logger.debug(f"[{self.action_id}] before_run")
    
    @abstractmethod
    def run(self) -> ActionResult:
        """核心动作（子类必须实现）
        
        Returns:
            ActionResult: 执行结果
        """
        pass
    
    def after_run(self):
        """执行后钩子（可重写）
        
        可用于：
        - 结果记录
        - 状态更新
        - 通知
        """
        logger.debug(f"[{self.action_id}] after_run")
    
    def rollback(self):
        """回滚动作
        
        失败时调用，按逆序执行回滚处理器
        """
        if self._state == ActionState.ROLLED_BACK:
            return
        
        logger.warning(f"[{self.action_id}] 开始回滚")
        self._state = ActionState.ROLLING_BACK
        
        for handler in reversed(self._rollback_handlers):
            try:
                handler()
                logger.info(f"[{self.action_id}] 回滚成功: {handler.__name__}")
            except Exception as e:
                logger.error(f"[{self.action_id}] 回滚失败: {e}")
        
        self._state = ActionState.ROLLED_BACK
        logger.info(f"[{self.action_id}] 回滚完成")
    
    def stop(self):
        """停止动作
        
        设置停止标志，让正在运行的动作检查并停止
        """
        if self._state in [ActionState.SUCCESS, ActionState.FAILED, ActionState.STOPPED]:
            return
        
        logger.info(f"[{self.action_id}] 收到停止信号")
        self._is_stopping = True
        self._state = ActionState.STOPPING
        self._result = ActionResult(
            success=False,
            status=ResultStatus.CANCELLED,
            message="动作被停止"
        )
    
    def cleanup(self):
        """清理钩子（可重写）
        
        无论成功失败都会执行，用于：
        - 资源释放
        - 连接关闭
        - 状态重置
        """
        logger.debug(f"[{self.action_id}] cleanup")
    
    def check_stop(self) -> bool:
        """检查是否收到停止信号
        
        在长时间运行的 action 中调用此方法检查是否需要停止
        
        Returns:
            bool: True 表示需要停止
        """
        return self._is_stopping
    
    def __repr__(self):
        return f"<{self.__class__.__name__}[{self._state}]>"


class CompositeAction(BaseAction):
    """组合动作
    
    将多个动作组合成一个序列执行
    
    使用示例：
    >>> class StartupFlow(CompositeAction):
    ...     def setup_actions(self):
    ...         return [
    ...             PowerOnAction(power),
    ...             MotorHomeAction(motor),
    ...             EncoderZeroAction(encoder)
    ...         ]
    """
    
    def __init__(self, actions: List[BaseAction] = None, **kwargs):
        super().__init__(**kwargs)
        self._actions = actions or []
        self._action_results: List[ActionResult] = []
    
    def add_action(self, action: BaseAction):
        """添加动作"""
        self._actions.append(action)
    
    def run(self) -> ActionResult:
        """执行所有动作"""
        self._action_results.clear()
        
        for action in self._actions:
            if self.check_stop():
                return ActionResult.failed(message="组合动作被停止")
            
            result = action.execute()
            self._action_results.append(result)
            
            if result.is_failed():
                return ActionResult.failed(
                    message=f"动作 {action.action_id} 失败: {result.message}",
                    data={'failed_action': action.action_id, 'results': [r.to_dict() for r in self._action_results]}
                )
        
        return ActionResult.success(
            message=f"组合动作完成: {len(self._actions)}个",
            data={'results': [r.to_dict() for r in self._action_results]}
        )
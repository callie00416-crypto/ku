"""
状态机 - State Machine

【职责】
- 定义状态转换规则
- 保证状态转换合法性
- 记录状态转换历史

【设计原则】
- 状态转换必须显式
- 禁止非法转换
- 状态转换可追踪
"""
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import time


@dataclass
class StateTransition:
    """状态转换记录"""
    from_state: str
    to_state: str
    timestamp: float
    reason: str = ""
    context: dict = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


class StateMachine:
    """状态机基类
    
    【职责】
    - 管理状态转换
    - 保证状态转换合法性
    - 记录状态转换历史
    
    【使用示例】
    >>> transitions = {
    ...     'pending': ['running', 'aborted'],
    ...     'running': ['completed', 'failed', 'aborted']
    ... }
    >>> sm = StateMachine(initial_state='pending', transitions=transitions)
    >>> sm.transition('running', reason='开始执行')
    >>> sm.current_state
    'running'
    >>> sm.get_history()
    [StateTransition(from_state='pending', to_state='running', ...)]
    """
    
    def __init__(self, initial_state: str, 
                 transitions: Dict[str, List[str]],
                 state_machine_id: str = None):
        """
        Args:
            initial_state: 初始状态
            transitions: 状态转换规则 {from_state: [to_states]}
            state_machine_id: 状态机ID
        """
        self._current_state = initial_state
        self._original_initial_state = initial_state
        self._transitions = transitions
        self._state_machine_id = state_machine_id or "default"
        self._history: List[StateTransition] = []
        self._transition_hooks: Dict[str, List[Callable]] = {}
    
    @property
    def current_state(self) -> str:
        """获取当前状态"""
        return self._current_state
    
    @property
    def history(self) -> List[StateTransition]:
        """获取状态转换历史"""
        return self._history.copy()
    
    def can_transition(self, to_state: str) -> bool:
        """检查是否可以转换到目标状态
        
        Args:
            to_state: 目标状态
            
        Returns:
            是否允许转换
        """
        if to_state == self._current_state:
            return True
        
        allowed_states = self._transitions.get(self._current_state, [])
        return to_state in allowed_states
    
    def transition(self, to_state: str, reason: str = "", 
                   context: dict = None, force: bool = False) -> bool:
        """执行状态转换
        
        Args:
            to_state: 目标状态
            reason: 转换原因
            context: 上下文数据
            force: 是否强制转换（跳过检查）
            
        Returns:
            是否转换成功
            
        Raises:
            ValueError: 非法状态转换
        """
        if not force and not self.can_transition(to_state):
            raise ValueError(
                f"非法状态转换: {self._current_state} -> {to_state}, "
                f"允许的状态: {self._transitions.get(self._current_state, [])}"
            )
        
        from_state = self._current_state
        
        # 执行转换前钩子
        self._execute_hooks('before_transition', from_state, to_state, context)
        
        # 执行转换
        self._current_state = to_state
        
        # 记录历史
        transition = StateTransition(
            from_state=from_state,
            to_state=to_state,
            timestamp=time.time(),
            reason=reason,
            context=context or {}
        )
        self._history.append(transition)
        
        # 执行转换后钩子
        self._execute_hooks('after_transition', from_state, to_state, context)
        
        return True
    
    def add_hook(self, hook_type: str, hook: Callable):
        """添加状态转换钩子
        
        Args:
            hook_type: 钩子类型 (before_transition/after_transition)
            hook: 钩子函数
        """
        if hook_type not in self._transition_hooks:
            self._transition_hooks[hook_type] = []
        self._transition_hooks[hook_type].append(hook)
    
    def _execute_hooks(self, hook_type: str, from_state: str, 
                      to_state: str, context: dict = None):
        """执行钩子
        
        Args:
            hook_type: 钩子类型
            from_state: 源状态
            to_state: 目标状态
            context: 上下文数据
        """
        hooks = self._transition_hooks.get(hook_type, [])
        for hook in hooks:
            try:
                hook(from_state, to_state, context)
            except Exception as e:
                pass
    
    def get_history(self, limit: int = None) -> List[StateTransition]:
        """获取状态转换历史
        
        Args:
            limit: 返回数量限制
            
        Returns:
            状态转换历史
        """
        history = self._history.copy()
        if limit:
            return history[-limit:]
        return history
    
    def reset(self, initial_state: str = None):
        """重置状态机
        
        Args:
            initial_state: 初始状态（不指定则使用原初始状态）
        """
        # Use the specified initial state or the original one
        reset_state = initial_state or self._original_initial_state
        self._current_state = reset_state
        self._history.clear()
    
    def __repr__(self) -> str:
        return f"<StateMachine id={self._state_machine_id} state={self._current_state}>"


class TaskStateMachine(StateMachine):
    """任务状态机
    
    【状态流转】
    pending -> running -> completed/failed/aborted
    
    【禁止】
    - 禁止逆流
    - 禁止跳过状态
    """
    
    def __init__(self, task_id: str):
        """
        Args:
            task_id: 任务ID
        """
        transitions = {
            'pending': ['running', 'aborted'],
            'running': ['completed', 'failed', 'aborted'],
            'completed': [],
            'failed': [],
            'aborted': []
        }
        super().__init__(
            initial_state='pending',
            transitions=transitions,
            state_machine_id=f"task_{task_id}"
        )
        self._task_id = task_id
    
    def start(self) -> bool:
        """开始任务
        
        Returns:
            是否成功
        """
        return self.transition('running', reason='任务开始')
    
    def complete(self) -> bool:
        """完成任务
        
        Returns:
            是否成功
        """
        return self.transition('completed', reason='任务完成')
    
    def fail(self, error: str = "") -> bool:
        """任务失败
        
        Args:
            error: 错误信息
            
        Returns:
            是否成功
        """
        return self.transition('failed', reason=f'任务失败: {error}')
    
    def abort(self, reason: str = "") -> bool:
        """中止任务
        
        Args:
            reason: 中止原因
            
        Returns:
            是否成功
        """
        return self.transition('aborted', reason=reason or '任务被中止')
    
    def retry(self) -> bool:
        """重试任务
        
        Returns:
            是否成功
        """
        if self._current_state != 'failed':
            raise ValueError("只有失败的任务才能重试")
        
        # 重置为 pending 状态
        self._current_state = 'pending'
        return True


class StationStateMachine(StateMachine):
    """工位状态机"""
    
    def __init__(self, station_id: str):
        """
        Args:
            station_id: 工位ID
        """
        transitions = {
            'idle': ['running', 'offline', 'maintenance', 'error'],
            'running': ['idle', 'error', 'offline'],
            'offline': ['idle'],
            'error': ['idle', 'maintenance', 'offline'],
            'maintenance': ['idle']
        }
        super().__init__(
            initial_state='idle',
            transitions=transitions,
            state_machine_id=f"station_{station_id}"
        )
        self._station_id = station_id
    
    def start(self) -> bool:
        """启动工位"""
        return self.transition('running', reason='工位启动')
    
    def stop(self) -> bool:
        """停止工位"""
        return self.transition('idle', reason='工位停止')
    
    def error(self, error: str = "") -> bool:
        """工位错误"""
        return self.transition('error', reason=error or '工位错误')
    
    def offline(self) -> bool:
        """工位离线"""
        return self.transition('offline', reason='工位离线')
    
    def maintenance(self) -> bool:
        """工位维护"""
        return self.transition('maintenance', reason='工位维护')
    
    def recover(self) -> bool:
        """工位恢复"""
        if self._current_state == 'error':
            return self.transition('idle', reason='工位恢复')
        return False
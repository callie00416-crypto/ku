"""
Base 模块 - Action 基类

职责：定义所有工业动作的标准接口
"""
from projects.encoder_test.actions.base.base_action import BaseAction, CompositeAction, ActionState
from projects.encoder_test.actions.base.action_result import ActionResult, ResultStatus
from projects.encoder_test.actions.base.action_context import ActionContext, ContextHolder

__all__ = [
    'BaseAction',
    'CompositeAction',
    'ActionState',
    'ActionResult',
    'ResultStatus',
    'ActionContext',
    'ContextHolder',
]
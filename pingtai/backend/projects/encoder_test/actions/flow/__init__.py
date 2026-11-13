"""
Flow 模块 - 流程编排层

职责：业务流程编排（Action容器）

【架构位置】
Scheduler
    ↓
TestCase
    ↓
Flow        ← 当前层
    ↓
Action
    ↓
Device
    ↓
Protocol
    ↓
Comm

【使用示例】
>>> from actions.flow import StartupFlow, ShutdownFlow, CalibrationFlow
>>> 
>>> # 开机
>>> flow = StartupFlow(power=ps, motor=motor, encoder=encoder)
>>> result = flow.execute()
>>> 
>>> # 关机
>>> flow = ShutdownFlow(power=ps, motor=motor)
>>> flow.execute()
"""
from projects.encoder_test.actions.flow.base_flow import (
    BaseFlow,
    FlowState,
    FlowResult,
    SequenceFlow,
    ConditionalFlow,
)
from projects.encoder_test.actions.flow.startup_flow import StartupFlow, ShutdownFlow
from projects.encoder_test.actions.flow.calibration_flow import CalibrationFlow, AgingFlow

__all__ = [
    'BaseFlow',
    'FlowState',
    'FlowResult',
    'SequenceFlow',
    'ConditionalFlow',
    'StartupFlow',
    'ShutdownFlow',
    'CalibrationFlow',
    'AgingFlow',
]
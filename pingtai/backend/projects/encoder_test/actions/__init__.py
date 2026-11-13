"""
Actions 层 - 工业动作标准化

【架构】
┌─────────────────────────────────────────────────────────────────────────────┐
│  Scheduler   - 调度器                                                       │
│      ↓                                                                     │
│  TestCase    - 测试业务逻辑                                                 │
│      ↓ 编排                                                                │
│  Flow        - 业务流程（Action容器）  ← 当前层                            │
│      ↓                                                                     │
│  Action      - 工业动作（复用流程）                                        │
│      ↓ 调用                                                                │
│  Device      - 设备能力                                                     │
│      ↓ 使用                                                                │
│  Protocol    - 协议封装                                                     │
│      ↓ 使用                                                                │
│  Comm        - 字节传输                                                    │
└─────────────────────────────────────────────────────────────────────────────┘

【使用示例】
>>> from actions import StartupFlow, ShutdownFlow
>>> from actions import PowerOnAction, DelayAction
>>> 
>>> # Flow 方式（推荐）
>>> flow = StartupFlow(power=ps, motor=motor, encoder=encoder)
>>> result = flow.execute()
>>> 
>>> # 直接调用 Action
>>> PowerOnAction(ps, voltage=5.0).execute()
>>> DelayAction(delay=2.0).execute()
"""
from projects.encoder_test.actions.base import (
    BaseAction,
    CompositeAction,
    ActionState,
    ActionResult,
    ResultStatus,
    ActionContext,
    ContextHolder,
)
from projects.encoder_test.actions.flow import (
    BaseFlow,
    FlowState,
    FlowResult,
    SequenceFlow,
    ConditionalFlow,
    StartupFlow,
    ShutdownFlow,
    CalibrationFlow,
    AgingFlow,
)
from projects.encoder_test.actions.power import PowerOnAction, PowerOffAction, PowerStableAction
from projects.encoder_test.actions.encoder import EncoderReadAction, EncoderZeroAction
from projects.encoder_test.actions.common import DelayAction, RetryAction, SafetyCheckAction
from projects.encoder_test.actions.motor_action import MotorAction
from projects.encoder_test.actions.encoder_action import EncoderAction
from projects.encoder_test.actions.power_amplifier_action import PowerAmplifierAction
from projects.encoder_test.actions.waveform_generator_action import WaveformGeneratorAction

__all__ = [
    # Base
    'BaseAction',
    'CompositeAction',
    'ActionState',
    'ActionResult',
    'ResultStatus',
    'ActionContext',
    'ContextHolder',
    # Flow
    'BaseFlow',
    'FlowState',
    'FlowResult',
    'SequenceFlow',
    'ConditionalFlow',
    'StartupFlow',
    'ShutdownFlow',
    'CalibrationFlow',
    'AgingFlow',
    # Power
    'PowerOnAction',
    'PowerOffAction',
    'PowerStableAction',
    # Motor
    'MotorAction',
    # Encoder
    'EncoderReadAction',
    'EncoderZeroAction',
    'EncoderAction',
    # Power Amplifier
    'PowerAmplifierAction',
    # Waveform Generator
    'WaveformGeneratorAction',
    # Common
    'DelayAction',
    'RetryAction',
    'SafetyCheckAction',
]
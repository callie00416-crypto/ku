"""
StartupFlow - 开机流程

所属层级：Flow 层
职责：标准设备启动流程

流程：
PowerOnAction
    ↓
DelayAction (等待稳定)
    ↓
MotorHomeAction (电机回零)
    ↓
EncoderZeroAction (编码器清零)
    ↓
SafetyCheckAction (安全检查)

使用示例：
>>> from drivers.factory import DeviceFactory
>>> power = DeviceFactory.create('power_supply', ...)
>>> motor = DeviceFactory.create('motor', ...)
>>> encoder = DeviceFactory.create('encoder', ...)
>>> 
>>> flow = StartupFlow(power=power, motor=motor, encoder=encoder)
>>> result = flow.execute()
"""
from projects.encoder_test.actions.flow.base_flow import BaseFlow
from projects.encoder_test.actions.power import PowerOnAction, PowerOffAction, PowerStableAction
from projects.encoder_test.actions.encoder import EncoderZeroAction
from projects.encoder_test.actions.common import DelayAction, SafetyCheckAction
from projects.encoder_test.actions.motor_action import MotorAction


class StartupFlow(BaseFlow):
    """设备启动流程
    
    标准开机流程：
    1. 电源上电
    2. 等待稳定
    3. 电机回零
    4. 编码器清零
    5. 安全检查
    """
    
    def __init__(
        self,
        power=None,
        motor=None,
        encoder=None,
        voltage: float = 5.0,
        current: float = 1.0,
        **kwargs
    ):
        """
        Args:
            power: 电源设备
            motor: 电机设备（MotorAction实例）
            encoder: 编码器设备
            voltage: 目标电压
            current: 目标电流
        """
        self._power = power
        self._motor = motor
        self._encoder = encoder
        self._voltage = voltage
        self._current = current
        
        super().__init__(flow_id="startup", **kwargs)
    
    def setup(self):
        """设置启动流程动作"""
        if self._power:
            self.add(PowerOnAction(
                power=self._power,
                voltage=self._voltage,
                current=self._current
            ))
        
        self.add(DelayAction(delay=1.0))
        
        if self._power:
            self.add(PowerStableAction(
                power=self._power,
                channel=1,
                stable_time=2.0
            ))
        
        if self._motor:
            if isinstance(self._motor, MotorAction):
                self._motor.enable_servo(True)
                self._motor.run_speed(1000, direction='CW')
                self._motor.stop()
            else:
                self.add(self._motor)
        
        if self._encoder:
            self.add(EncoderZeroAction(encoder=self._encoder))
        
        devices = {}
        if self._power:
            devices['power'] = self._power
        if self._motor:
            devices['motor'] = self._motor
        if self._encoder:
            devices['encoder'] = self._encoder
        
        if devices:
            self.add(SafetyCheckAction(devices=devices))


class ShutdownFlow(BaseFlow):
    """设备关机流程
    
    标准关机流程：
    1. 电机停止
    2. 电源下电
    """
    
    def __init__(self, power=None, motor=None, **kwargs):
        self._power = power
        self._motor = motor
        
        super().__init__(flow_id="shutdown", **kwargs)
    
    def setup(self):
        """设置关机流程动作"""
        if self._motor:
            if isinstance(self._motor, MotorAction):
                self._motor.stop()
            else:
                self.add(self._motor)
        
        if self._power:
            self.add(PowerOffAction(power=self._power, channel=1))
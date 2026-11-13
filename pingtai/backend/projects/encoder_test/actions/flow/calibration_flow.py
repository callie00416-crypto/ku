"""
CalibrationFlow - 标定流程

所属层级：Flow 层
职责：编码器标定业务流程

流程：
EncoderZeroAction (清零)
    ↓
MotorMoveAction (移动到位置1)
    ↓
EncoderReadAction (读取角度1)
    ↓
MotorMoveAction (移动到位置2)
    ↓
EncoderReadAction (读取角度2)
    ↓
计算误差并写入补偿
    ↓
校验结果

使用示例：
>>> flow = CalibrationFlow(encoder=encoder, motor=motor)
>>> result = flow.execute()
"""
from projects.encoder_test.actions.flow.base_flow import BaseFlow
from projects.encoder_test.actions.encoder import EncoderReadAction, EncoderZeroAction
from projects.encoder_test.actions.common import DelayAction
from projects.encoder_test.actions.motor_action import MotorAction


class CalibrationFlow(BaseFlow):
    """编码器标定流程
    
    标准标定流程：
    1. 编码器清零
    2. 移动到参考位置
    3. 记录角度
    4. 移动到另一个位置
    5. 记录角度
    6. 计算误差并补偿
    7. 校验结果
    """
    
    def __init__(
        self,
        encoder=None,
        motor=None,
        reference_positions: list = None,
        **kwargs
    ):
        """
        Args:
            encoder: 编码器设备
            motor: 电机设备（MotorAction实例）
            reference_positions: 参考位置列表
        """
        self._encoder = encoder
        self._motor = motor
        self._reference_positions = reference_positions or [0, 90, 180, 270]
        
        super().__init__(flow_id="calibration", timeout=600, **kwargs)
    
    def setup(self):
        """设置标定流程"""
        if self._encoder:
            self.add(EncoderZeroAction(encoder=self._encoder))
        
        for pos in self._reference_positions:
            if self._motor:
                if isinstance(self._motor, MotorAction):
                    self._motor.run_speed(500, direction='CW')
                else:
                    self.add(self._motor)
            
            self.add(DelayAction(delay=0.5))
            
            if self._encoder:
                self.add(EncoderReadAction(encoder=self._encoder))
        
        self.add(DelayAction(delay=1.0))


class AgingFlow(BaseFlow):
    """老化测试流程
    
    标准老化流程：
    1. 电源上电
    2. 循环执行：
       - 电机移动
       - 编码器读取
       - 数据记录
    3. 异常监控
    4. 电源下电
    """
    
    def __init__(
        self,
        power=None,
        motor=None,
        encoder=None,
        cycles: int = 100,
        interval: float = 5.0,
        **kwargs
    ):
        """
        Args:
            power: 电源设备
            motor: 电机设备（MotorAction实例）
            encoder: 编码器设备
            cycles: 循环次数
            interval: 循环间隔（秒）
        """
        self._power = power
        self._motor = motor
        self._encoder = encoder
        self._cycles = cycles
        self._interval = interval
        
        super().__init__(flow_id="aging", timeout=cycles * (interval + 10), **kwargs)
    
    def setup(self):
        """设置老化流程"""
        if self._power:
            from projects.encoder_test.actions.power import PowerOnAction
            self.add(PowerOnAction(power=self._power, voltage=5.0))
        
        for cycle in range(self._cycles):
            if self._motor:
                if isinstance(self._motor, MotorAction):
                    self._motor.run_speed(1000, direction='CW' if cycle % 2 == 0 else 'CCW')
                else:
                    self.add(self._motor)
            
            if self._encoder:
                self.add(EncoderReadAction(encoder=self._encoder))
            
            self.add(DelayAction(delay=self._interval))
"""
PowerAction - 电源动作

所属层级：Action 层
职责：标准电源上电/下电/稳定流程

使用示例：
>>> action = PowerOnAction(power, voltage=5.0, current=1.0)
>>> result = action.execute()
"""
import time
import logging
from shared.drivers.base.base_device import BaseDevice
from projects.encoder_test.actions.base.base_action import BaseAction
from projects.encoder_test.actions.base.action_result import ActionResult

logger = logging.getLogger(__name__)


class PowerOnAction(BaseAction):
    """电源上电动作"""
    
    def __init__(self, power: BaseDevice, voltage: float = 5.0, 
                 current: float = 1.0, channel: int = 1, **kwargs):
        """
        Args:
            power: 电源设备实例
            voltage: 目标电压 (V)
            current: 目标电流 (A)
            channel: 通道号 (1 或 2)
        """
        super().__init__(action_id=f"power_on_ch{channel}", **kwargs)
        self.power = power
        self.voltage = voltage
        self.current = current
        self.channel = channel
    
    def run(self) -> ActionResult:
        """执行上电流程"""
        logger.info(f"开始上电: 电压={self.voltage}V, 电流={self.current}A")
        
        try:
            if not self.power.is_connected():
                if not self.power.connect():
                    return ActionResult.failed("电源连接失败")
                self.add_rollback(lambda: self.power.disconnect())
            
            self.power.set_voltage(self.voltage, self.channel)
            self.add_rollback(lambda: self.power.set_voltage(0, self.channel))
            
            self.power.set_current(self.current, self.channel)
            self.add_rollback(lambda: self.power.set_current(0, self.channel))
            
            time.sleep(0.3)
            
            if not self.power.turn_on(self.channel):
                return ActionResult.failed("打开输出失败")
            self.add_rollback(lambda: self.power.turn_off(self.channel))
            
            time.sleep(0.5)
            
            actual_voltage = self.power.read_voltage(self.channel)
            
            logger.info(f"上电完成: 设定={self.voltage}V, 实际={actual_voltage}V")
            
            return ActionResult.success(
                message=f"通道 {self.channel} 上电成功",
                data={
                    'voltage': actual_voltage,
                    'current': self.power.read_current(self.channel),
                    'channel': self.channel
                }
            )
            
        except Exception as e:
            logger.exception(f"上电异常: {e}")
            self.rollback()
            return ActionResult.failed(f"上电异常: {str(e)}", error_detail=str(e))


class PowerOffAction(BaseAction):
    """电源下电动作"""
    
    def __init__(self, power: BaseDevice, channel: int = 1, **kwargs):
        super().__init__(action_id=f"power_off_ch{channel}", **kwargs)
        self.power = power
        self.channel = channel
    
    def run(self) -> ActionResult:
        """执行下电流程"""
        logger.info(f"开始下电: 通道 {self.channel}")
        
        try:
            self.power.turn_off(self.channel)
            time.sleep(0.3)
            self.power.set_voltage(0, self.channel)
            self.power.set_current(0, self.channel)
            
            return ActionResult.success(
                message=f"通道 {self.channel} 下电成功",
                data={'channel': self.channel}
            )
            
        except Exception as e:
            logger.exception(f"下电异常: {e}")
            return ActionResult.failed(f"下电异常: {str(e)}", error_detail=str(e))


class PowerStableAction(BaseAction):
    """电源稳定等待动作"""
    
    def __init__(self, power: BaseDevice, channel: int = 1,
                 stable_time: float = 2.0, tolerance: float = 0.1, **kwargs):
        """
        Args:
            power: 电源设备
            channel: 通道号
            stable_time: 稳定时间（秒）
            tolerance: 电压波动容忍度 (V)
        """
        super().__init__(action_id=f"power_stable_ch{channel}", timeout=stable_time + 10, **kwargs)
        self.power = power
        self.channel = channel
        self.stable_time = stable_time
        self.tolerance = tolerance
        self._start_voltage = None
        self._stable_start = None
    
    def run(self) -> ActionResult:
        """等待电源稳定"""
        logger.info(f"等待电源稳定: 通道 {self.channel}")
        
        try:
            self._start_voltage = self.power.read_voltage(self.channel)
            self._stable_start = time.time()
            
            while not self.check_stop():
                elapsed = time.time() - self._stable_start
                if elapsed >= self.timeout:
                    return ActionResult.timeout(message="电源稳定超时")
                
                current_voltage = self.power.read_voltage(self.channel)
                diff = abs(current_voltage - self._start_voltage)
                
                if diff <= self.tolerance:
                    if time.time() - self._stable_start >= self.stable_time:
                        return ActionResult.success(
                            message="电源稳定",
                            data={
                                'voltage': current_voltage,
                                'stable_time': self.stable_time,
                                'channel': self.channel
                            }
                        )
                else:
                    self._stable_start = time.time()
                    self._start_voltage = current_voltage
                
                time.sleep(0.1)
            
            return ActionResult.failed(message="等待稳定被停止")
            
        except Exception as e:
            logger.exception(f"等待稳定异常: {e}")
            return ActionResult.failed(f"等待稳定异常: {str(e)}", error_detail=str(e))
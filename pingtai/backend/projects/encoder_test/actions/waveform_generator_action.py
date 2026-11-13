"""
WaveformGeneratorAction - 波形发生器动作封装

所属层级：Action 层
职责：封装波形发生器的业务动作，隐藏底层协议细节

设计原则：
- 不直接操作寄存器
- 不关心通讯协议
- 只提供业务级别的动作接口

使用示例：
>>> wg = WaveformGeneratorAction(driver)
>>> wg.set_square_wave(frequency=1000, high_level=5.0, low_level=0.0)
>>> wg.turn_on(channel=1)
"""
import logging
from projects.encoder_test.actions.base.base_action import BaseAction
from projects.encoder_test.actions.base.action_result import ActionResult

logger = logging.getLogger(__name__)


class WaveformGeneratorAction(BaseAction):
    """波形发生器动作
    
    封装波形发生器的所有业务动作：
    - 设置波形
    - 打开/关闭输出
    - 设置频率/幅度/偏移
    """
    
    def __init__(self, driver, **kwargs):
        """
        Args:
            driver: 波形发生器Driver实例
        """
        super().__init__(action_id="waveform_generator_action", **kwargs)
        self.driver = driver
    
    def set_square_wave(
        self,
        frequency: float,
        high_level: float = 5.0,
        low_level: float = 0.0,
        duty_cycle: float = 50.0,
        channel: int = 1
    ) -> ActionResult:
        """设置方波
        
        Args:
            frequency: 频率（Hz）
            high_level: 高电平（V）
            low_level: 低电平（V）
            duty_cycle: 占空比（%）
            channel: 通道号
            
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("波形发生器未连接")

            if hasattr(self.driver, 'set_output_impedance'):
                self.driver.set_output_impedance('50', channel=channel)

            if hasattr(self.driver, 'set_waveform'):
                self.driver.set_waveform('SQU', frequency=frequency, channel=channel)
            else:
                return ActionResult.failed("波形发生器不支持设置波形")
            
            if hasattr(self.driver, 'set_high_low_level'):
                self.driver.set_high_low_level(high_level=high_level, low_level=low_level, channel=channel)
            
            if hasattr(self.driver, 'set_duty_cycle'):
                self.driver.set_duty_cycle(duty_cycle, channel=channel)
            
            return ActionResult.success(
                message=f"设置方波成功: {frequency}Hz, {high_level}~{low_level}V, {duty_cycle}%占空比",
                data={
                    'frequency': frequency,
                    'high_level': high_level,
                    'low_level': low_level,
                    'duty_cycle': duty_cycle,
                    'channel': channel
                }
            )
            
        except Exception as e:
            logger.exception(f"设置方波异常: {e}")
            return ActionResult.failed(f"设置方波异常: {str(e)}", error_detail=str(e))
    
    def turn_on(self, channel: int = 1) -> ActionResult:
        """打开输出
        
        Args:
            channel: 通道号
            
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("波形发生器未连接")
            
            if hasattr(self.driver, 'output_on'):
                self.driver.output_on(channel=channel)
            elif hasattr(self.driver, 'turn_on'):
                self.driver.turn_on()
            else:
                return ActionResult.failed("波形发生器不支持打开输出")
            
            return ActionResult.success(
                message=f"打开输出成功: 通道{channel}",
                data={'channel': channel}
            )
            
        except Exception as e:
            logger.exception(f"打开输出异常: {e}")
            return ActionResult.failed(f"打开输出异常: {str(e)}", error_detail=str(e))
    
    def turn_off(self, channel: int = 1) -> ActionResult:
        """关闭输出
        
        Args:
            channel: 通道号
            
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("波形发生器未连接")
            
            if hasattr(self.driver, 'output_off'):
                self.driver.output_off(channel=channel)
            elif hasattr(self.driver, 'turn_off'):
                self.driver.turn_off()
            else:
                return ActionResult.failed("波形发生器不支持关闭输出")
            
            return ActionResult.success(
                message=f"关闭输出成功: 通道{channel}",
                data={'channel': channel}
            )
            
        except Exception as e:
            logger.exception(f"关闭输出异常: {e}")
            return ActionResult.failed(f"关闭输出异常: {str(e)}", error_detail=str(e))
    
    def get_frequency(self, channel: int = 1) -> ActionResult:
        """读取频率
        
        Args:
            channel: 通道号
            
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("波形发生器未连接")
            
            if hasattr(self.driver, 'get_frequency'):
                frequency = self.driver.get_frequency(channel=channel)
            else:
                return ActionResult.failed("波形发生器不支持读取频率")
            
            return ActionResult.success(
                message=f"读取频率成功: {frequency}Hz",
                data={'frequency': frequency, 'channel': channel}
            )
            
        except Exception as e:
            logger.exception(f"读取频率异常: {e}")
            return ActionResult.failed(f"读取频率异常: {str(e)}", error_detail=str(e))
    
    def run(self) -> ActionResult:
        """BaseAction抽象方法实现（此Action不直接使用）"""
        return ActionResult.success(message="WaveformGeneratorAction ready")
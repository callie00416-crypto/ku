"""
PowerAmplifierAction - 功率放大器动作封装

所属层级：Action 层
职责：封装功率放大器的业务动作，隐藏底层协议细节

设计原则：
- 不直接操作寄存器
- 不关心通讯协议
- 只提供业务级别的动作接口

使用示例：
>>> power = PowerAmplifierAction(driver)
>>> power.set_gain(0)
>>> power.turn_on()
"""
import logging
from projects.encoder_test.actions.base.base_action import BaseAction
from projects.encoder_test.actions.base.action_result import ActionResult

logger = logging.getLogger(__name__)


class PowerAmplifierAction(BaseAction):
    """功率放大器动作
    
    封装功率放大器的所有业务动作：
    - 设置增益
    - 打开/关闭输出
    - 读取状态
    """
    
    def __init__(self, driver, **kwargs):
        """
        Args:
            driver: 功率放大器Driver实例
        """
        super().__init__(action_id="power_amplifier_action", **kwargs)
        self.driver = driver
    
    def set_gain(self, gain: int) -> ActionResult:
        """设置增益
        
        Args:
            gain: 增益值（dB）
            
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("功率放大器未连接")
            
            if hasattr(self.driver, 'set_gain'):
                self.driver.set_gain(gain)
            else:
                return ActionResult.failed("功率放大器不支持设置增益")
            
            return ActionResult.success(
                message=f"设置增益成功: {gain}dB",
                data={'gain': gain}
            )
            
        except Exception as e:
            logger.exception(f"设置增益异常: {e}")
            return ActionResult.failed(f"设置增益异常: {str(e)}", error_detail=str(e))
    
    def turn_on(self) -> ActionResult:
        """打开输出
        
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("功率放大器未连接")
            
            if hasattr(self.driver, 'output_on'):
                self.driver.output_on()
            elif hasattr(self.driver, 'turn_on'):
                self.driver.turn_on()
            else:
                return ActionResult.failed("功率放大器不支持打开输出")
            
            return ActionResult.success(
                message="打开输出成功",
                data={}
            )
            
        except Exception as e:
            logger.exception(f"打开输出异常: {e}")
            return ActionResult.failed(f"打开输出异常: {str(e)}", error_detail=str(e))
    
    def turn_off(self) -> ActionResult:
        """关闭输出
        
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("功率放大器未连接")
            
            if hasattr(self.driver, 'output_off'):
                self.driver.output_off()
            elif hasattr(self.driver, 'turn_off'):
                self.driver.turn_off()
            else:
                return ActionResult.failed("功率放大器不支持关闭输出")
            
            return ActionResult.success(
                message="关闭输出成功",
                data={}
            )
            
        except Exception as e:
            logger.exception(f"关闭输出异常: {e}")
            return ActionResult.failed(f"关闭输出异常: {str(e)}", error_detail=str(e))
    
    def get_status(self) -> ActionResult:
        """读取状态
        
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("功率放大器未连接")
            
            if hasattr(self.driver, 'get_status'):
                status = self.driver.get_status()
            else:
                status = self.driver.read_data()
            
            return ActionResult.success(
                message="读取状态成功",
                data=status
            )
            
        except Exception as e:
            logger.exception(f"读取状态异常: {e}")
            return ActionResult.failed(f"读取状态异常: {str(e)}", error_detail=str(e))
    
    def set_output_resistance(self, resistance: float) -> ActionResult:
        """设置输出电阻
        
        Args:
            resistance: 输出电阻值（Ω），可选 1.5 或 50.0
            
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("功率放大器未连接")
            
            if hasattr(self.driver, 'set_output_resistance'):
                self.driver.set_output_resistance(resistance)
            else:
                return ActionResult.failed("功率放大器不支持设置输出电阻")
            
            return ActionResult.success(
                message=f"设置输出电阻成功: {resistance}Ω",
                data={'output_resistance': resistance}
            )
            
        except Exception as e:
            logger.exception(f"设置输出电阻异常: {e}")
            return ActionResult.failed(f"设置输出电阻异常: {str(e)}", error_detail=str(e))
    
    def run(self) -> ActionResult:
        """BaseAction抽象方法实现（此Action不直接使用）"""
        return ActionResult.success(message="PowerAmplifierAction ready")
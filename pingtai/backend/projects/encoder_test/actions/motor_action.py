"""
MotorAction - ASDB2电机动作封装

所属层级：Action 层
职责：封装ASDB2电机的业务动作，隐藏底层寄存器和协议细节

设计原则：
- 不直接操作寄存器
- 不关心通讯协议
- 只提供业务级别的动作接口

使用示例：
>>> motor = MotorAction(driver)
>>> motor.run_speed(1000, direction='CW', source='P1-11')
>>> motor.stop()
>>> motor.enable_servo()
"""
import time
import logging
from typing import Optional
from projects.encoder_test.actions.base.base_action import BaseAction
from projects.encoder_test.actions.base.action_result import ActionResult

logger = logging.getLogger(__name__)


class MotorAction(BaseAction):
    """ASDB2电机动作
    
    封装ASDB2电机的所有业务动作：
    - 使能/关闭伺服
    - 运行/停止电机
    - 设置速度和方向
    - 读取反馈速度
    """
    
    def __init__(self, driver, **kwargs):
        """
        Args:
            driver: ASDB2Driver实例
        """
        super().__init__(action_id="motor_action", **kwargs)
        self.driver = driver
    
    def enable_servo(self, enable: bool = True) -> ActionResult:
        """使能/关闭伺服
        
        Args:
            enable: True=使能，False=关闭
            
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("电机未连接")
            
            success = self.driver.enable_servo(enable)
            if success:
                return ActionResult.success(
                    message=f"伺服{'使能' if enable else '关闭'}成功",
                    data={'servo_enabled': enable}
                )
            else:
                return ActionResult.failed(f"伺服{'使能' if enable else '关闭'}失败")
                
        except Exception as e:
            logger.exception(f"伺服操作异常: {e}")
            return ActionResult.failed(f"伺服操作异常: {str(e)}", error_detail=str(e))
    
    def run_speed(self, rpm: float, direction: str = 'CW', source: str = 'P1-11') -> ActionResult:
        """运行电机
        
        Args:
            rpm: 速度（RPM）
            direction: 方向（'CW'或'CCW'）
            source: 速度源（'P1-09', 'P1-10', 'P1-11'）
            
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("电机未连接")
            
            success = self.driver.run_motor(speed_rpm=rpm, direction=direction, source=source)
            if success:
                return ActionResult.success(
                    message=f"电机运行: {rpm} RPM, {direction}, {source}",
                    data={'speed_rpm': rpm, 'direction': direction, 'source': source}
                )
            else:
                return ActionResult.failed(f"电机运行失败: {rpm} RPM")
                
        except Exception as e:
            logger.exception(f"运行电机异常: {e}")
            return ActionResult.failed(f"运行电机异常: {str(e)}", error_detail=str(e))
    
    def stop(self) -> ActionResult:
        """停止电机
        
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("电机未连接")
            
            success = self.driver.stop_motor()
            if success:
                return ActionResult.success(
                    message="电机停止成功",
                    data={'speed_rpm': 0.0}
                )
            else:
                return ActionResult.failed("电机停止失败")
                
        except Exception as e:
            logger.exception(f"停止电机异常: {e}")
            return ActionResult.failed(f"停止电机异常: {str(e)}", error_detail=str(e))
    
    def read_speed(self) -> ActionResult:
        """读取反馈速度
        
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("电机未连接")
            
            speed = self.driver.read_feedback_speed()
            if speed is not None:
                return ActionResult.success(
                    message=f"读取速度成功",
                    data={'feedback_speed': speed}
                )
            else:
                return ActionResult.failed("读取速度失败")
                
        except Exception as e:
            logger.exception(f"读取速度异常: {e}")
            return ActionResult.failed(f"读取速度异常: {str(e)}", error_detail=str(e))
    
    def set_speed(self, p1_09: Optional[float] = None, p1_10: Optional[float] = None, p1_11: Optional[float] = None) -> ActionResult:
        """设置速度值
        
        Args:
            p1_09: P1-09速度值
            p1_10: P1-10速度值
            p1_11: P1-11速度值
            
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("电机未连接")
            
            success = self.driver.set_speed(p1_09=p1_09, p1_10=p1_10, p1_11=p1_11)
            if success:
                return ActionResult.success(
                    message="设置速度成功",
                    data={'p1_09': p1_09, 'p1_10': p1_10, 'p1_11': p1_11}
                )
            else:
                return ActionResult.failed("设置速度失败")
                
        except Exception as e:
            logger.exception(f"设置速度异常: {e}")
            return ActionResult.failed(f"设置速度异常: {str(e)}", error_detail=str(e))
    
    def initialize(self) -> ActionResult:
        """初始化驱动器
        
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("电机未连接")
            
            success = self.driver.initialize_driver()
            if success:
                return ActionResult.success(
                    message="驱动器初始化成功",
                    data={}
                )
            else:
                return ActionResult.failed("驱动器初始化失败")
                
        except Exception as e:
            logger.exception(f"初始化驱动器异常: {e}")
            return ActionResult.failed(f"初始化驱动器异常: {str(e)}", error_detail=str(e))
    
    def run(self) -> ActionResult:
        """BaseAction抽象方法实现（此Action不直接使用）"""
        return ActionResult.success(message="MotorAction ready")
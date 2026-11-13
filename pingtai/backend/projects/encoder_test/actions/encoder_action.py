"""
EncoderAction - 编码器动作封装

所属层级：Action 层
职责：封装编码器的业务动作，隐藏底层协议细节

设计原则：
- 不直接操作寄存器
- 不关心通讯协议
- 只提供业务级别的动作接口

使用示例：
>>> encoder = EncoderAction(driver)
>>> encoder.read_angle()
>>> encoder.zero()
"""
import logging
from typing import Optional, Dict, Any
from projects.encoder_test.actions.base.base_action import BaseAction
from projects.encoder_test.actions.base.action_result import ActionResult

logger = logging.getLogger(__name__)


class EncoderAction(BaseAction):
    """编码器动作
    
    封装编码器的所有业务动作：
    - 读取角度
    - 清零
    - 读取双圈角度
    """
    
    def __init__(self, driver, **kwargs):
        """
        Args:
            driver: 编码器Driver实例
        """
        super().__init__(action_id="encoder_action", **kwargs)
        self.driver = driver
    
    def read_angle(self) -> ActionResult:
        """读取角度
        
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("编码器未连接")
            
            data = self.driver.read_data()
            
            return ActionResult.success(
                message="读取角度成功",
                data=data
            )
            
        except Exception as e:
            logger.exception(f"读取角度异常: {e}")
            return ActionResult.failed(f"读取角度异常: {str(e)}", error_detail=str(e))
    
    def read_both_angles(self) -> ActionResult:
        """读取双圈角度
        
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("编码器未连接")
            
            if hasattr(self.driver, 'read_both_angles'):
                data = self.driver.read_both_angles()
            else:
                data = self.driver.read_data()
            
            return ActionResult.success(
                message="读取双圈角度成功",
                data=data
            )
            
        except Exception as e:
            logger.exception(f"读取双圈角度异常: {e}")
            return ActionResult.failed(f"读取双圈角度异常: {str(e)}", error_detail=str(e))
    
    def zero(self) -> ActionResult:
        """清零编码器
        
        Returns:
            ActionResult
        """
        try:
            if not self.driver.is_connected:
                return ActionResult.failed("编码器未连接")
            
            if hasattr(self.driver, 'reset'):
                self.driver.reset()
            elif hasattr(self.driver, 'zero'):
                self.driver.zero()
            else:
                return ActionResult.failed("编码器不支持清零")
            
            return ActionResult.success(
                message="清零成功",
                data={'angle': 0.0}
            )
            
        except Exception as e:
            logger.exception(f"清零异常: {e}")
            return ActionResult.failed(f"清零异常: {str(e)}", error_detail=str(e))
    
    def run(self) -> ActionResult:
        """BaseAction抽象方法实现（此Action不直接使用）"""
        return ActionResult.success(message="EncoderAction ready")
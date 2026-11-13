"""
EncoderAction - 编码器动作

所属层级：Action 层
职责：标准编码器操作动作

使用示例：
>>> action = EncoderReadAction(encoder)
>>> result = action.execute()
"""
import logging
from shared.drivers.base.base_device import BaseDevice
from projects.encoder_test.actions.base.base_action import BaseAction
from projects.encoder_test.actions.base.action_result import ActionResult

logger = logging.getLogger(__name__)


class EncoderReadAction(BaseAction):
    """编码器读取动作"""
    
    def __init__(self, encoder: BaseDevice, **kwargs):
        super().__init__(action_id="encoder_read", timeout=10, **kwargs)
        self.encoder = encoder
    
    def run(self) -> ActionResult:
        """读取编码器数据"""
        logger.info("读取编码器")
        
        try:
            if not self.encoder.is_connected():
                if not self.encoder.connect():
                    return ActionResult.failed("编码器连接失败")
            
            data = self.encoder.read_data()
            
            return ActionResult.success(
                message="读取成功",
                data=data
            )
            
        except Exception as e:
            logger.exception(f"读取异常: {e}")
            return ActionResult.failed(f"读取异常: {str(e)}", error_detail=str(e))


class EncoderZeroAction(BaseAction):
    """编码器清零动作"""
    
    def __init__(self, encoder: BaseDevice, **kwargs):
        super().__init__(action_id="encoder_zero", timeout=10, **kwargs)
        self.encoder = encoder
    
    def run(self) -> ActionResult:
        """清零编码器"""
        logger.info("编码器清零")
        
        try:
            self.encoder.reset()
            
            return ActionResult.success(
                message="清零完成",
                data={'angle': 0.0}
            )
            
        except Exception as e:
            logger.exception(f"清零异常: {e}")
            return ActionResult.failed(f"清零异常: {str(e)}", error_detail=str(e))
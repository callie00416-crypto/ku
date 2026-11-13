"""
CommonAction - 通用动作

所属层级：Action 层
职责：通用动作（延时、重试、安全检查）

使用示例：
>>> action = DelayAction(delay=2.0)
>>> result = action.execute()
"""
import time
import logging
from typing import Dict, Any
from projects.encoder_test.actions.base.base_action import BaseAction
from projects.encoder_test.actions.base.action_result import ActionResult

logger = logging.getLogger(__name__)


class DelayAction(BaseAction):
    """延时动作"""
    
    def __init__(self, delay: float = 1.0, **kwargs):
        """
        Args:
            delay: 延时时间（秒）
        """
        super().__init__(action_id=f"delay_{delay}s", timeout=delay + 10, **kwargs)
        self.delay = delay
    
    def run(self) -> ActionResult:
        """执行延时"""
        logger.info(f"延时: {self.delay}秒")
        
        try:
            start = time.time()
            while time.time() - start < self.delay:
                if self.check_stop():
                    return ActionResult.failed(message="延时被停止")
                time.sleep(min(0.1, self.delay - (time.time() - start)))
            
            return ActionResult.success(
                message=f"延时完成: {self.delay}秒",
                data={'delay': self.delay}
            )
            
        except Exception as e:
            logger.exception(f"延时异常: {e}")
            return ActionResult.failed(f"延时异常: {str(e)}", error_detail=str(e))


class RetryAction(BaseAction):
    """重试动作"""
    
    def __init__(self, action: BaseAction, retries: int = 3, delay: float = 1.0, **kwargs):
        """
        Args:
            action: 要重试的动作
            retries: 最大重试次数
            delay: 重试间隔（秒）
        """
        super().__init__(action_id=f"retry_{action.action_id}", timeout=action.timeout * retries + delay * retries, **kwargs)
        self.action = action
        self.retries = retries
        self.delay = delay
    
    def run(self) -> ActionResult:
        """执行重试"""
        logger.info(f"开始重试: {self.action.action_id}, 次数={self.retries}")
        
        for attempt in range(1, self.retries + 1):
            if self.check_stop():
                return ActionResult.failed(message="重试被停止")
            
            logger.info(f"尝试 {attempt}/{self.retries}")
            
            result = self.action.execute()
            
            if result.is_success():
                data = result.data.copy()
                data['attempt'] = attempt
                return ActionResult.success(
                    message=f"重试成功: 第{attempt}次",
                    data=data
                )
            
            if attempt < self.retries:
                logger.warning(f"失败，等待{self.delay}秒后重试")
                time.sleep(self.delay)
        
        return ActionResult.failed(
            message=f"重试{self.retries}次后仍失败",
            error_code="RETRY_EXHAUSTED"
        )


class SafetyCheckAction(BaseAction):
    """安全检查动作"""
    
    def __init__(self, devices: Dict[str, Any], **kwargs):
        """
        Args:
            devices: 设备字典 {'power': xxx, 'motor': xxx, ...}
        """
        super().__init__(action_id="safety_check", timeout=30, **kwargs)
        self.devices = devices
        self._check_results: Dict[str, Any] = {}
    
    def run(self) -> ActionResult:
        """执行安全检查"""
        logger.info("开始安全检查")
        
        try:
            self._check_results.clear()
            
            for name, device in self.devices.items():
                try:
                    health = device.health_check()
                    self._check_results[name] = {
                        'ok': True,
                        'health': health
                    }
                    logger.info(f"设备 {name} 健康检查通过")
                except Exception as e:
                    self._check_results[name] = {
                        'ok': False,
                        'error': str(e)
                    }
                    logger.error(f"设备 {name} 健康检查失败: {e}")
            
            failed = [k for k, v in self._check_results.items() if not v['ok']]
            
            if failed:
                return ActionResult.failed(
                    message=f"安全检查失败: {failed}",
                    error_code="SAFETY_CHECK_FAILED",
                    error_detail=f"设备 {failed} 检查不通过"
                )
            
            return ActionResult.success(
                message="安全检查通过",
                data={'checks': self._check_results}
            )
            
        except Exception as e:
            logger.exception(f"安全检查异常: {e}")
            return ActionResult.failed(f"安全检查异常: {str(e)}", error_detail=str(e))
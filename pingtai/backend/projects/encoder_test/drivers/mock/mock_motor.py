"""
Mock 电机驱动 - 模拟电机运动控制

【架构】
MockMotor(BaseDevice) - 继承自 BaseDevice，模拟电机设备

支持：
- 位置/速度控制
- 运行状态模拟
- 错误模式（模拟电机故障）
- 限位开关模拟
"""
import logging
from typing import Dict, Any
from shared.drivers.base.base_device import BaseDevice

logger = logging.getLogger(__name__)


class MockMotor(BaseDevice):
    """Mock 电机驱动"""
    
    def __init__(self, driver_id: str = 'mock_motor', protocol=None,
                 mode: str = 'normal', **kwargs):
        """
        初始化 Mock 电机
        
        Args:
            driver_id: 驱动唯一标识
            protocol: 协议层实例（可选）
            mode: 工作模式
                - normal: 正常模式
                - error: 错误模式（操作时抛出异常）
                - stall: 堵转模式（无法运动）
            **kwargs: 其他配置参数
                - position_limit: 位置限制（度），默认 ±360
                - max_speed: 最大速度（度/秒），默认 180
        """
        super().__init__(driver_id, protocol, **kwargs)
        self.mode = mode
        self.running = False
        self.speed = 0.0
        self.position = 0.0
        self._position_limit = kwargs.get('position_limit', 360.0)
        self._max_speed = kwargs.get('max_speed', 180.0)
        self._homing = False
        self._left_limit = False
        self._right_limit = False
    
    def connect(self) -> bool:
        """连接设备"""
        self._is_connected = True
        logger.info(f"Mock 电机已连接: mode={self.mode}")
        return True
    
    def disconnect(self):
        """断开连接"""
        self._is_connected = False
        self.running = False
        logger.info(f"Mock 电机已断开")
    
    def is_connected(self) -> bool:
        """检查是否连接"""
        return self._is_connected
    
    def read_data(self) -> Dict[str, Any]:
        """
        读取电机状态数据
        
        Returns:
            包含位置、速度、运行状态的字典
        """
        return {
            'position': self.position,
            'speed': self.speed,
            'running': self.running,
            'homing': self._homing,
            'left_limit': self._left_limit,
            'right_limit': self._right_limit
        }
    
    def write_data(self, data: Dict[str, Any]) -> bool:
        """
        写入数据（设置速度等参数）
        
        Args:
            data: 包含 'speed' 等键的字典
            
        Returns:
            写入是否成功
        """
        if 'speed' in data:
            self.speed = max(-self._max_speed, min(self._max_speed, data['speed']))
        
        logger.debug(f"Mock 电机写入数据: {data}")
        return True
    
    def reset(self):
        """重置电机（位置、速度归零，停止运行）"""
        self.position = 0.0
        self.speed = 0.0
        self.running = False
        self._homing = False
        self._left_limit = False
        self._right_limit = False
        logger.debug("Mock 电机已重置")
    
    def start(self):
        """启动电机"""
        if self.mode == 'error':
            raise RuntimeError("电机故障")
        
        if self.mode == 'stall':
            raise RuntimeError("电机堵转")
        
        self.running = True
        logger.info(f"Mock 电机已启动: speed={self.speed}")
    
    def stop(self):
        """停止电机"""
        self.running = False
        self.speed = 0.0
        logger.info("Mock 电机已停止")
    
    def move_to(self, position: float):
        """
        移动到指定位置
        
        Args:
            position: 目标位置（度）
            
        Raises:
            RuntimeError: 错误模式或堵转模式时
        """
        if self.mode == 'error':
            raise RuntimeError("电机故障")
        
        if self.mode == 'stall':
            raise RuntimeError("电机堵转")
        
        if position < -self._position_limit:
            self._left_limit = True
            self.position = -self._position_limit
            self.running = False
            logger.warning(f"Mock 电机到达左限位: {self.position}")
            return
        
        if position > self._position_limit:
            self._right_limit = True
            self.position = self._position_limit
            self.running = False
            logger.warning(f"Mock 电机到达右限位: {self.position}")
            return
        
        self.position = position
        self._left_limit = False
        self._right_limit = False
        logger.debug(f"Mock 电机移动到: {self.position}")
    
    def move_by(self, delta: float):
        """
        相对移动
        
        Args:
            delta: 移动增量（度）
        """
        self.move_to(self.position + delta)
    
    def set_position(self, position: float):
        """
        直接设置位置（不带动画）
        
        Args:
            position: 位置值（度）
        """
        self.position = max(-self._max_speed, min(self._max_speed, position))
        logger.debug(f"Mock 电机位置设置为: {self.position}")
    
    def set_speed(self, speed: float):
        """
        设置速度
        
        Args:
            speed: 速度值（度/秒）
        """
        self.speed = max(-self._max_speed, min(self._max_speed, speed))
        logger.debug(f"Mock 电机速度设置为: {self.speed}")
    
    def start_homing(self):
        """开始回零"""
        self._homing = True
        logger.info("Mock 电机开始回零")
        
        self.position = 0.0
        self._homing = False
        self._left_limit = False
        self._right_limit = False
        logger.info("Mock 电机回零完成")
    
    def set_position_limit(self, limit: float):
        """
        设置位置限制
        
        Args:
            limit: 位置限制（度）
        """
        self._position_limit = abs(limit)
        self.position = max(-self._position_limit, min(self._position_limit, self.position))
        logger.debug(f"Mock 电机位置限制设置为: ±{self._position_limit}")
    
    def set_max_speed(self, speed: float):
        """
        设置最大速度
        
        Args:
            speed: 最大速度（度/秒）
        """
        self._max_speed = abs(speed)
        self.speed = max(-self._max_speed, min(self._max_speed, self.speed))
        logger.debug(f"Mock 电机最大速度设置为: {self._max_speed}")
    
    def simulate_limit_switch(self, side: str):
        """
        模拟限位开关触发
        
        Args:
            side: 'left' 或 'right'
        """
        if side == 'left':
            self._left_limit = True
            self.position = -self._position_limit
        elif side == 'right':
            self._right_limit = True
            self.position = self._position_limit
        
        self.running = False
        logger.warning(f"Mock 电机{side}限位触发")
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        base = super().health_check()
        base.update({
            'mock': True,
            'running': self.running,
            'position': self.position,
            'speed': self.speed,
            'position_limit': self._position_limit,
            'max_speed': self._max_speed,
            'homing': self._homing,
            'left_limit': self._left_limit,
            'right_limit': self._right_limit
        })
        return base
"""
Mock 编码器驱动 - 模拟编码器角度/速度数据

【架构】
MockEncoder(BaseDevice) - 继承自 BaseDevice，模拟编码器设备

支持：
- 角度/速度数据模拟
- 错误模式（模拟设备故障）
- 噪声模拟
- 角度范围限制
"""
import random
import logging
from typing import Dict, Any
from shared.drivers.base.base_device import BaseDevice

logger = logging.getLogger(__name__)


class MockEncoder(BaseDevice):
    """Mock 编码器驱动"""
    
    def __init__(self, driver_id: str = 'mock_encoder', protocol=None,
                 resolution: int = 4096, mode: str = 'normal', **kwargs):
        """
        初始化 Mock 编码器
        
        Args:
            driver_id: 驱动唯一标识
            protocol: 协议层实例（可选）
            resolution: 编码器分辨率，默认 4096
            mode: 工作模式
                - normal: 正常模式
                - error: 错误模式（读取时抛出异常）
                - noisy: 噪声模式（数据带有随机噪声）
            **kwargs: 其他配置参数
        """
        super().__init__(driver_id, protocol, **kwargs)
        self.resolution = resolution
        self.mode = mode
        self.angle = 0.0
        self.speed = 0.0
        self._noise_level = kwargs.get('noise_level', 0.0)
        self._angle_limit = kwargs.get('angle_limit', 360.0)
    
    def connect(self) -> bool:
        """连接设备"""
        self._is_connected = True
        logger.info(f"Mock 编码器已连接: resolution={self.resolution}, mode={self.mode}")
        return True
    
    def disconnect(self):
        """断开连接"""
        self._is_connected = False
        logger.info(f"Mock 编码器已断开")
    
    def is_connected(self) -> bool:
        """检查是否连接"""
        return self._is_connected
    
    def read_data(self) -> Dict[str, Any]:
        """
        读取编码器数据
        
        Returns:
            包含角度和速度的字典
            
        Raises:
            ConnectionError: 错误模式时
        """
        if self.mode == 'error':
            raise ConnectionError("模拟编码器错误")
        
        angle = self.angle
        speed = self.speed
        
        if self.mode == 'noisy' and self._noise_level > 0:
            noise = (random.random() - 0.5) * 2 * self._noise_level
            angle += noise
        
        return {'angle': angle, 'speed': speed}
    
    def write_data(self, data: Dict[str, Any]) -> bool:
        """
        写入数据（设置角度或速度）
        
        Args:
            data: 包含 'angle' 或 'speed' 的字典
            
        Returns:
            写入是否成功
        """
        if 'angle' in data:
            self.angle = max(-self._angle_limit, min(self._angle_limit, data['angle']))
        
        if 'speed' in data:
            self.speed = data['speed']
        
        logger.debug(f"Mock 编码器写入数据: {data}")
        return True
    
    def reset(self):
        """重置编码器（角度和速度归零）"""
        self.angle = 0.0
        self.speed = 0.0
        logger.debug("Mock 编码器已重置")
    
    def set_angle(self, angle: float):
        """
        设置角度值
        
        Args:
            angle: 角度值（度）
        """
        self.angle = max(-self._angle_limit, min(self._angle_limit, angle))
        logger.debug(f"Mock 编码器角度设置为: {self.angle}")
    
    def set_speed(self, speed: float):
        """
        设置速度值
        
        Args:
            speed: 速度值（度/秒）
        """
        self.speed = speed
        logger.debug(f"Mock 编码器速度设置为: {self.speed}")
    
    def set_noise_level(self, level: float):
        """
        设置噪声级别（用于 noisy 模式）
        
        Args:
            level: 噪声幅度（度），默认 0
        """
        self._noise_level = max(0.0, level)
        logger.debug(f"Mock 编码器噪声级别设置为: {self._noise_level}")
    
    def set_angle_limit(self, limit: float):
        """
        设置角度范围限制
        
        Args:
            limit: 角度限制（度），默认 360
        """
        self._angle_limit = abs(limit)
        self.angle = max(-self._angle_limit, min(self._angle_limit, self.angle))
        logger.debug(f"Mock 编码器角度限制设置为: ±{self._angle_limit}")
    
    def increment_angle(self, delta: float):
        """
        增量调整角度
        
        Args:
            delta: 角度增量（度）
        """
        self.set_angle(self.angle + delta)
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        base = super().health_check()
        base.update({
            'mock': True,
            'resolution': self.resolution,
            'mode': self.mode,
            'angle': self.angle,
            'speed': self.speed,
            'noise_level': self._noise_level,
            'angle_limit': self._angle_limit
        })
        return base
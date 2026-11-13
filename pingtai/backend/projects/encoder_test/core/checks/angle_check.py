"""
AngleCheck - 角度断言层

所属层级：Check 层
职责：提供角度相关的断言方法

设计原则：
- 静态方法，无状态
- 提供清晰的断言消息
- 支持容忍度配置

使用示例：
>>> AngleCheck.stable(actual=90.1, target=90.0, tolerance=0.5)
>>> AngleCheck.in_range(angle=45.0, min_angle=0.0, max_angle=360.0)
"""
import logging

logger = logging.getLogger(__name__)


class AngleCheck:
    """角度断言类
    
    提供角度相关的断言方法：
    - 稳定性检查
    - 范围检查
    - CRC有效性检查
    """
    
    @staticmethod
    def stable(actual: float, target: float, tolerance: float = 0.5) -> bool:
        """检查角度是否稳定（在容忍度范围内）
        
        Args:
            actual: 实际角度
            target: 目标角度
            tolerance: 容忍度（度）
            
        Returns:
            bool: 是否稳定
            
        Raises:
            AssertionError: 如果角度不稳定
        """
        error = abs(actual - target)
        passed = error <= tolerance
        
        if not passed:
            raise AssertionError(
                f"角度不稳定: 实际={actual:.4f}°, 目标={target:.4f}°, "
                f"误差={error:.4f}°, 容忍度={tolerance}°"
            )
        
        logger.info(f"角度稳定: {actual:.4f}° (目标={target:.4f}°, 误差={error:.4f}°)")
        return True
    
    @staticmethod
    def in_range(angle: float, min_angle: float = 0.0, max_angle: float = 360.0) -> bool:
        """检查角度是否在范围内
        
        Args:
            angle: 角度
            min_angle: 最小角度
            max_angle: 最大角度
            
        Returns:
            bool: 是否在范围内
            
        Raises:
            AssertionError: 如果角度超出范围
        """
        passed = min_angle <= angle <= max_angle
        
        if not passed:
            raise AssertionError(
                f"角度超出范围: {angle:.4f}°, "
                f"范围=[{min_angle:.4f}, {max_angle:.4f}]°"
            )
        
        logger.info(f"角度在范围内: {angle:.4f}°")
        return True
    
    @staticmethod
    def crc_valid(data: dict) -> bool:
        """检查CRC是否有效
        
        Args:
            data: 编码器数据
            
        Returns:
            bool: CRC是否有效
            
        Raises:
            AssertionError: 如果CRC无效
        """
        if not data:
            raise AssertionError("编码器数据为空")
        
        crc_valid = data.get('crc_valid', False)
        
        if not crc_valid:
            raise AssertionError("编码器CRC校验失败")
        
        logger.info("CRC校验通过")
        return True
    
    @staticmethod
    def data_not_none(data: dict, name: str = "数据") -> bool:
        """检查数据不为空
        
        Args:
            data: 数据
            name: 数据名称
            
        Returns:
            bool: 数据是否不为空
            
        Raises:
            AssertionError: 如果数据为空
        """
        if data is None:
            raise AssertionError(f"{name}为空")
        
        logger.info(f"{name}不为空")
        return True
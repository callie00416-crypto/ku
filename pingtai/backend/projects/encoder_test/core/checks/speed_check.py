"""
SpeedCheck - 速度断言层

所属层级：Check 层
职责：提供速度相关的断言方法

设计原则：
- 静态方法，无状态
- 提供清晰的断言消息
- 支持容忍度配置

使用示例：
>>> SpeedCheck.stable(actual=998, target=1000, tolerance=5)
>>> SpeedCheck.in_range(speed=500, min_speed=0, max_speed=3000)
"""
import logging

logger = logging.getLogger(__name__)


class SpeedCheck:
    """速度断言类
    
    提供速度相关的断言方法：
    - 稳定性检查
    - 范围检查
    - 方向检查
    """
    
    @staticmethod
    def stable(actual: float, target: float, tolerance: float = 5.0) -> bool:
        """检查速度是否稳定（在容忍度范围内）
        
        Args:
            actual: 实际速度
            target: 目标速度
            tolerance: 容忍度（RPM）
            
        Returns:
            bool: 是否稳定
            
        Raises:
            AssertionError: 如果速度不稳定
        """
        error = abs(actual - target)
        passed = error <= tolerance
        
        if not passed:
            raise AssertionError(
                f"速度不稳定: 实际={actual} RPM, 目标={target} RPM, "
                f"误差={error} RPM, 容忍度={tolerance} RPM"
            )
        
        logger.info(f"速度稳定: {actual} RPM (目标={target} RPM, 误差={error} RPM)")
        return True
    
    @staticmethod
    def in_range(speed: float, min_speed: float = 0.0, max_speed: float = 3000.0) -> bool:
        """检查速度是否在范围内
        
        Args:
            speed: 速度
            min_speed: 最小速度
            max_speed: 最大速度
            
        Returns:
            bool: 是否在范围内
            
        Raises:
            AssertionError: 如果速度超出范围
        """
        passed = min_speed <= speed <= max_speed
        
        if not passed:
            raise AssertionError(
                f"速度超出范围: {speed} RPM, "
                f"范围=[{min_speed}, {max_speed}] RPM"
            )
        
        logger.info(f"速度在范围内: {speed} RPM")
        return True
    
    @staticmethod
    def zero(speed: float, tolerance: float = 1.0) -> bool:
        """检查速度是否为零
        
        Args:
            speed: 速度
            tolerance: 容忍度（RPM）
            
        Returns:
            bool: 是否为零
            
        Raises:
            AssertionError: 如果速度不为零
        """
        passed = abs(speed) <= tolerance
        
        if not passed:
            raise AssertionError(
                f"速度不为零: {speed} RPM, "
                f"容忍度={tolerance} RPM"
            )
        
        logger.info(f"速度为零: {speed} RPM")
        return True
    
    @staticmethod
    def positive(speed: float) -> bool:
        """检查速度是否为正值（逆时针）
        
        Args:
            speed: 速度
            
        Returns:
            bool: 是否为正值
            
        Raises:
            AssertionError: 如果速度不为正值
        """
        passed = speed > 0
        
        if not passed:
            raise AssertionError(
                f"速度不为正值: {speed} RPM"
            )
        
        logger.info(f"速度为正值: {speed} RPM")
        return True
    
    @staticmethod
    def negative(speed: float) -> bool:
        """检查速度是否为负值（顺时针）
        
        Args:
            speed: 速度
            
        Returns:
            bool: 是否为负值
            
        Raises:
            AssertionError: 如果速度不为负值
        """
        passed = speed < 0
        
        if not passed:
            raise AssertionError(
                f"速度不为负值: {speed} RPM"
            )
        
        logger.info(f"速度为负值: {speed} RPM")
        return True
    
    @staticmethod
    def direction_match(speed: float, direction: str) -> bool:
        """检查速度方向是否匹配
        
        Args:
            speed: 速度
            direction: 方向（'CW'或'CCW'）
            
        Returns:
            bool: 方向是否匹配
            
        Raises:
            AssertionError: 如果方向不匹配
        """
        if direction == 'CW':
            passed = speed < 0
        elif direction == 'CCW':
            passed = speed > 0
        else:
            raise ValueError(f"无效方向: {direction}")
        
        if not passed:
            raise AssertionError(
                f"方向不匹配: 速度={speed} RPM, 期望方向={direction}"
            )
        
        logger.info(f"方向匹配: {speed} RPM, {direction}")
        return True
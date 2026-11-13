"""
SpeedCollector - 速度数据采集

所属层级：Collector 层
职责：采集速度数据，用于测试分析和报告

设计原则：
- 支持连续采样
- 支持指定采样间隔
- 返回结构化数据

使用示例：
>>> collector = SpeedCollector(motor_action)
>>> data = collector.collect(duration=10, interval=0.1)
>>> # data = [(time, speed), (time, speed), ...]
"""
import time
import logging
from typing import List, Tuple, Optional
from projects.encoder_test.actions.motor_action import MotorAction

logger = logging.getLogger(__name__)


class SpeedCollector:
    """速度数据采集器
    
    采集速度数据，返回时间序列数据
    """
    
    def __init__(self, motor: MotorAction):
        """
        Args:
            motor: MotorAction实例
        """
        self.motor = motor
    
    def collect(self, duration: float = 10.0, interval: float = 0.1) -> List[Tuple[float, float]]:
        """采集速度数据
        
        Args:
            duration: 采集时长（秒）
            interval: 采样间隔（秒）
            
        Returns:
            List[Tuple[float, float]]: [(时间, 速度), ...]
        """
        data = []
        start_time = time.time()
        end_time = start_time + duration
        
        logger.info(f"开始采集速度数据: 时长={duration}s, 间隔={interval}s")
        
        while time.time() < end_time:
            current_time = time.time()
            
            # 读取速度
            result = self.motor.read_speed()
            if result.is_success:
                speed = result.data.get('feedback_speed', 0.0)
                data.append((current_time - start_time, speed))
            else:
                logger.warning(f"读取速度失败: {result.message}")
                data.append((current_time - start_time, 0.0))
            
            # 等待下一次采样
            elapsed = time.time() - current_time
            if elapsed < interval:
                time.sleep(interval - elapsed)
        
        logger.info(f"采集完成: 共{len(data)}个数据点")
        return data
    
    def collect_single(self) -> Optional[float]:
        """采集单个速度数据点
        
        Returns:
            Optional[float]: 速度值
        """
        result = self.motor.read_speed()
        if result.is_success:
            return result.data.get('feedback_speed', 0.0)
        return None
    
    def get_statistics(self, data: List[Tuple[float, float]]) -> dict:
        """获取速度统计数据
        
        Args:
            data: 速度数据 [(时间, 速度), ...]
            
        Returns:
            dict: 统计数据
        """
        if not data:
            return {}
        
        speeds = [speed for _, speed in data]
        
        return {
            'count': len(speeds),
            'min': min(speeds),
            'max': max(speeds),
            'mean': sum(speeds) / len(speeds),
            'std': (sum((s - sum(speeds) / len(speeds)) ** 2 for s in speeds) / len(speeds)) ** 0.5
        }
"""
时间处理模块 - Temporal Utilities

【职责】
- 处理工业系统中的时间概念
- 支持不同时间语义
- 提供时间戳管理
"""
from typing import Union
import time
from dataclasses import dataclass


@dataclass
class Timestamp:
    """时间戳值对象
    
    【工业时间语义】
    - event_time: 事件真实发生时间
    - process_time: 系统处理时间  
    - persisted_time: 数据持久化时间
    """
    event_time: float  # 事件发生时间
    process_time: float = None  # 处理时间，默认当前时间
    persisted_time: float = None  # 持久化时间，默认当前时间
    
    def __post_init__(self):
        if self.process_time is None:
            self.process_time = time.time()
        if self.persisted_time is None:
            self.persisted_time = time.time()


def get_current_timestamp() -> float:
    """获取当前时间戳"""
    return time.time()


def format_timestamp(timestamp: float, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化时间戳"""
    import datetime
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime(fmt)


def parse_datetime_to_timestamp(dt_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> float:
    """将日期时间字符串解析为时间戳"""
    import datetime
    dt = datetime.datetime.strptime(dt_str, fmt)
    return dt.timestamp()


class TimeRange:
    """时间范围值对象"""
    
    def __init__(self, start_time: float, end_time: float):
        if start_time > end_time:
            raise ValueError(f"开始时间({start_time})不能大于结束时间({end_time})")
        self._start_time = start_time
        self._end_time = end_time
    
    @property
    def start_time(self) -> float:
        return self._start_time
    
    @property
    def end_time(self) -> float:
        return self._end_time
    
    @property
    def duration(self) -> float:
        """获取持续时间（秒）"""
        return self._end_time - self._start_time
    
    def contains(self, timestamp: float) -> bool:
        """判断时间戳是否在范围内"""
        return self._start_time <= timestamp <= self._end_time
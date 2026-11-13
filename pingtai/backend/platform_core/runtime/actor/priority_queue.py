"""
优先级队列实现
"""
import heapq
from typing import Any, Tuple
import time


class PriorityQueue:
    """自定义优先级队列，支持时间戳排序"""
    
    def __init__(self, max_size: int = 0):
        self._queue = []
        self._index = 0  # 稳定排序的索引
        self.max_size = max_size
        
    def put(self, item: Tuple[int, float, Any]):
        """添加项目 (priority, timestamp, item)"""
        if self.max_size > 0 and len(self._queue) >= self.max_size:
            raise Exception("Queue is full")
            
        # 使用负优先级值以实现最小堆（优先级数值越小优先级越高）
        # 时间戳用于相同优先级时的先进先出
        heapq.heappush(self._queue, (item[0], item[1], self._index, item[2]))
        self._index += 1
        
    def get(self) -> Tuple[int, float, Any]:
        """获取项目"""
        if self.empty():
            raise Exception("Queue is empty")
            
        priority, timestamp, index, item = heapq.heappop(self._queue)
        return priority, timestamp, item
        
    def get_nowait(self) -> Tuple[int, float, Any]:
        """非阻塞获取项目"""
        return self.get()
        
    def empty(self) -> bool:
        """检查队列是否为空"""
        return len(self._queue) == 0
        
    def full(self) -> bool:
        """检查队列是否已满"""
        return self.max_size > 0 and len(self._queue) >= self.max_size
        
    def qsize(self) -> int:
        """获取队列大小"""
        return len(self._queue)
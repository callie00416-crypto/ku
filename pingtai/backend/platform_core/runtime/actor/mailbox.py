"""
Actor邮箱治理 - 负责消息优先级和溢出策略
"""
from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional
import asyncio
import time
import logging
from queue import PriorityQueue, Queue, Full, Empty


class MessagePriority(Enum):
    """消息优先级"""
    CRITICAL = 1    # 不可丢弃，阻塞等待，优先级最高 - 急停、NG结果、安全联锁
    NORMAL = 2       # DROP_OLD - 普通状态同步、普通流程推进
    TRANSIENT = 3    # 新值覆盖旧值 - 心跳、温度、电流、Load


@dataclass
class ActorMessage:
    """Actor消息"""
    message_id: str
    priority: MessagePriority
    content: Any
    timestamp: float
    sender: Optional[str] = None
    correlation_id: Optional[str] = None


class PriorityMailbox:
    """优先级邮箱"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.critical_queue = PriorityQueue()  # 优先级1 - CRITICAL
        self.normal_queue = PriorityQueue()    # 优先级2 - NORMAL  
        self.transient_queue = Queue(maxsize=max_size)  # 优先级3 - TRANSIENT
        self.logger = logging.getLogger(__name__)
        self.stats = {
            'critical_count': 0,
            'normal_count': 0,
            'transient_count': 0,
            'dropped_normal': 0,
            'overwritten_transient': 0
        }
        
    def put(self, message: ActorMessage):
        """放入消息"""
        if message.priority == MessagePriority.CRITICAL:
            # CRITICAL: 不可丢弃，阻塞等待
            self.critical_queue.put((message.priority.value, time.time(), message))
            self.stats['critical_count'] += 1
        elif message.priority == MessagePriority.NORMAL:
            # NORMAL: DROP_OLD 策略
            try:
                self.normal_queue.put((message.priority.value, time.time(), message), block=False)
                self.stats['normal_count'] += 1
            except Full:
                self.logger.warning(f"NORMAL消息队列已满，丢弃消息: {message.message_id}")
                self.stats['dropped_normal'] += 1
        else:  # TRANSIENT
            # TRANSIENT: 新值覆盖旧值，只保留最新值
            try:
                self.transient_queue.put(message, block=False)
                # 如果队列满了，移除最旧的消息，添加新消息
                if self.transient_queue.full():
                    try:
                        self.transient_queue.get_nowait()  # 移除最旧消息
                        self.transient_queue.put(message, block=False)  # 添加新消息
                        self.stats['overwritten_transient'] += 1
                    except:
                        pass  # 如果移除失败，静默处理
                self.stats['transient_count'] += 1
            except Full:
                # 队列已满，直接替换
                try:
                    self.transient_queue.get_nowait()
                    self.transient_queue.put(message, block=False)
                    self.stats['overwritten_transient'] += 1
                except:
                    pass
                    
    def get(self) -> Optional[ActorMessage]:
        """获取消息 - 按优先级顺序"""
        # 首先检查CRITICAL队列
        try:
            priority, timestamp, message = self.critical_queue.get_nowait()
            return message
        except Empty:
            pass
            
        # 然后检查NORMAL队列
        try:
            priority, timestamp, message = self.normal_queue.get_nowait()
            return message
        except Empty:
            pass
            
        # 最后检查TRANSIENT队列
        try:
            message = self.transient_queue.get_nowait()
            return message
        except Empty:
            pass
            
        return None  # 所有队列都为空
        
    def size(self) -> int:
        """获取邮箱总大小"""
        return (self.critical_queue.qsize() + 
                self.normal_queue.qsize() + 
                self.transient_queue.qsize())
                
    def is_empty(self) -> bool:
        """检查邮箱是否为空"""
        return self.size() == 0
        
    def get_stats(self) -> dict:
        """获取统计信息"""
        stats = self.stats.copy()
        stats['total_size'] = self.size()
        stats['critical_size'] = self.critical_queue.qsize()
        stats['normal_size'] = self.normal_queue.qsize()
        stats['transient_size'] = self.transient_queue.qsize()
        return stats
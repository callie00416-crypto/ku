"""
邮箱溢出策略
"""
from enum import Enum
from typing import Any
import logging


class OverflowPolicy(Enum):
    """溢出策略枚举"""
    DROP_OLDEST = "DROP_OLDEST"      # 丢弃最老的消息
    DROP_NEWEST = "DROP_NEWEST"      # 丢弃最新的消息
    BLOCK = "BLOCK"                  # 阻塞直到有空间
    OVERWRITE = "OVERWRITE"          # 覆盖现有消息


class OverflowHandler:
    """溢出处理器"""
    
    def __init__(self, policy: OverflowPolicy = OverflowPolicy.DROP_OLDEST):
        self.policy = policy
        self.logger = logging.getLogger(__name__)
        
    def handle_overflow(self, queue, new_item: Any):
        """处理队列溢出"""
        if self.policy == OverflowPolicy.DROP_OLDEST:
            # 丢弃最老的消息
            try:
                old_item = queue.get_nowait()
                self.logger.warning(f"队列溢出，丢弃最老消息")
                return queue.put(new_item)
            except:
                return queue.put(new_item)
                
        elif self.policy == OverflowPolicy.DROP_NEWEST:
            # 丢弃最新消息
            self.logger.warning(f"队列溢出，丢弃最新消息")
            return
            
        elif self.policy == OverflowPolicy.BLOCK:
            # 阻塞直到有空间 - 队列put操作本身就会阻塞
            return queue.put(new_item)
            
        elif self.policy == OverflowPolicy.OVERWRITE:
            # 覆盖现有消息
            try:
                queue.get_nowait()  # 移除一个消息
            except:
                pass  # 队列可能为空
            return queue.put(new_item)
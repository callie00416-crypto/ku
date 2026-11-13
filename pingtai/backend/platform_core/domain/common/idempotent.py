"""
幂等性处理机制
"""
import asyncio
import hashlib
import time
from typing import Any, Dict, Set
import logging
from datetime import datetime, timedelta


class IdempotentCommand:
    """幂等命令基类"""
    
    def __init__(self, command_id: str = None, content: Any = None):
        self.command_id = command_id or self._generate_command_id(content)
        self.content = content
        self.timestamp = datetime.now()
        
    def _generate_command_id(self, content: Any) -> str:
        """生成命令ID"""
        content_str = str(content) if content is not None else ""
        timestamp_str = str(time.time())
        combined = f"{content_str}:{timestamp_str}".encode('utf-8')
        return hashlib.sha256(combined).hexdigest()[:16]


class IdempotencyManager:
    """幂等性管理器"""
    
    def __init__(self, retention_minutes: int = 1440):  # 默认保留24小时
        self.processed_commands: Set[str] = set()
        self.command_timestamps: Dict[str, datetime] = {}
        self.retention_delta = timedelta(minutes=retention_minutes)
        self.logger = logging.getLogger(__name__)
        self.lock = asyncio.Lock()
        
    async def is_already_processed(self, command_id: str) -> bool:
        """检查命令是否已处理"""
        async with self.lock:
            # 清理过期记录
            await self._cleanup_expired_records()
            
            return command_id in self.processed_commands
            
    async def mark_as_processed(self, command_id: str) -> bool:
        """标记命令为已处理，返回是否为首次处理"""
        async with self.lock:
            # 清理过期记录
            await self._cleanup_expired_records()
            
            if command_id in self.processed_commands:
                return False  # 已处理过
                
            self.processed_commands.add(command_id)
            self.command_timestamps[command_id] = datetime.now()
            return True  # 首次处理
            
    async def execute_if_not_processed(self, command: IdempotentCommand, handler) -> Any:
        """如果命令未处理，则执行"""
        is_new = await self.mark_as_processed(command.command_id)
        if is_new:
            self.logger.debug(f"执行新命令: {command.command_id}")
            return await handler(command)
        else:
            self.logger.debug(f"命令已处理，跳过执行: {command.command_id}")
            return None  # 或者返回上次执行的结果
            
    async def _cleanup_expired_records(self):
        """清理过期记录"""
        now = datetime.now()
        expired_commands = [
            cmd_id for cmd_id, timestamp in self.command_timestamps.items()
            if now - timestamp > self.retention_delta
        ]
        
        for cmd_id in expired_commands:
            self.processed_commands.discard(cmd_id)
            self.command_timestamps.pop(cmd_id, None)
            
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'processed_count': len(self.processed_commands),
            'retention_minutes': self.retention_delta.total_seconds() / 60
        }


# 全局幂等性管理器实例
_idempotency_manager = None


def get_idempotency_manager() -> IdempotencyManager:
    """获取幂等性管理器单例"""
    global _idempotency_manager
    if _idempotency_manager is None:
        _idempotency_manager = IdempotencyManager()
    return _idempotency_manager
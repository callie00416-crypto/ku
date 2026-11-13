"""
任务管理模块 - 测试任务创建、暂停、停止、恢复、状态监控
"""
import uuid
import time
import threading
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class TaskInfo:
    """任务信息"""
    task_id: str
    task_name: str
    station_id: int
    product_sn: str
    status: TaskStatus = TaskStatus.CREATED
    priority: int = 1  # 1=高, 2=中, 3=低
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    paused_at: Optional[float] = None
    pause_duration: float = 0.0  # 暂停累计时长
    progress: float = 0.0  # 进度 0-100
    result: Optional[Dict[str, Any]] = None
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def duration(self) -> float:
        """获取任务执行时长（秒）"""
        if self.started_at is None:
            return 0.0
        
        end_time = self.completed_at or self.paused_at or time.time()
        total = end_time - self.started_at
        
        # 减去暂停时间
        return total - self.pause_duration
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'task_id': self.task_id,
            'task_name': self.task_name,
            'station_id': self.station_id,
            'product_sn': self.product_sn,
            'status': self.status.value,
            'priority': self.priority,
            'progress': self.progress,
            'duration': self.duration(),
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'error_message': self.error_message,
            'metadata': self.metadata
        }


class TaskManager:
    """任务管理器 - 负责任务生命周期管理"""
    
    def __init__(self):
        self._tasks: Dict[str, TaskInfo] = {}
        self._lock = threading.RLock()
        self._status_callbacks: List[Callable] = []
    
    def create_task(self, task_name: str, station_id: int, product_sn: str,
                    priority: int = 1, tags: List[str] = None,
                    metadata: Dict[str, Any] = None) -> str:
        """
        创建测试任务
        
        Args:
            task_name: 任务名称
            station_id: 工位ID
            product_sn: 产品SN码
            priority: 优先级
            tags: 标签列表
            metadata: 元数据
            
        Returns:
            task_id
        """
        task_id = str(uuid.uuid4())
        
        task_info = TaskInfo(
            task_id=task_id,
            task_name=task_name,
            station_id=station_id,
            product_sn=product_sn,
            status=TaskStatus.CREATED,
            priority=priority,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        with self._lock:
            self._tasks[task_id] = task_info
        
        logger.info(f"创建任务: {task_id} ({task_name}), 工位{station_id}")
        self._notify_status_change(task_id, TaskStatus.CREATED)
        
        return task_id
    
    def start_task(self, task_id: str) -> bool:
        """
        启动任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            if task.status not in [TaskStatus.CREATED, TaskStatus.QUEUED, TaskStatus.PAUSED]:
                logger.warning(f"任务状态不允许启动: {task_id}, 当前状态: {task.status.value}")
                return False
            
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            
            logger.info(f"启动任务: {task_id}")
            self._notify_status_change(task_id, TaskStatus.RUNNING)
            
            return True
    
    def pause_task(self, task_id: str) -> bool:
        """
        暂停任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            if task.status != TaskStatus.RUNNING:
                logger.warning(f"任务状态不允许暂停: {task_id}, 当前状态: {task.status.value}")
                return False
            
            task.status = TaskStatus.PAUSED
            task.paused_at = time.time()
            
            logger.info(f"暂停任务: {task_id}")
            self._notify_status_change(task_id, TaskStatus.PAUSED)
            
            return True
    
    def resume_task(self, task_id: str) -> bool:
        """
        恢复任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            if task.status != TaskStatus.PAUSED:
                logger.warning(f"任务状态不允许恢复: {task_id}, 当前状态: {task.status.value}")
                return False
            
            # 累计暂停时间
            if task.paused_at:
                task.pause_duration += time.time() - task.paused_at
                task.paused_at = None
            
            task.status = TaskStatus.RUNNING
            
            logger.info(f"恢复任务: {task_id}")
            self._notify_status_change(task_id, TaskStatus.RUNNING)
            
            return True
    
    def complete_task(self, task_id: str, result: Dict[str, Any] = None) -> bool:
        """
        完成任务
        
        Args:
            task_id: 任务ID
            result: 任务结果
            
        Returns:
            是否成功
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            if task.status != TaskStatus.RUNNING:
                logger.warning(f"任务状态不允许完成: {task_id}, 当前状态: {task.status.value}")
                return False
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            task.result = result or {}
            task.progress = 100.0
            
            logger.info(f"任务完成: {task_id}")
            self._notify_status_change(task_id, TaskStatus.COMPLETED)
            
            return True
    
    def fail_task(self, task_id: str, error_message: str = "") -> bool:
        """
        标记任务失败
        
        Args:
            task_id: 任务ID
            error_message: 错误信息
            
        Returns:
            是否成功
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            task.status = TaskStatus.FAILED
            task.completed_at = time.time()
            task.error_message = error_message
            task.progress = 100.0
            
            logger.warning(f"任务失败: {task_id}, {error_message}")
            self._notify_status_change(task_id, TaskStatus.FAILED)
            
            return True
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return False
            
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                logger.warning(f"任务状态不允许取消: {task_id}, 当前状态: {task.status.value}")
                return False
            
            task.status = TaskStatus.CANCELLED
            task.completed_at = time.time()
            
            logger.info(f"任务取消: {task_id}")
            self._notify_status_change(task_id, TaskStatus.CANCELLED)
            
            return True
    
    def update_progress(self, task_id: str, progress: float):
        """
        更新任务进度
        
        Args:
            task_id: 任务ID
            progress: 进度值 (0-100)
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.progress = max(0.0, min(100.0, progress))
    
    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            TaskInfo或None
        """
        return self._tasks.get(task_id)
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[TaskInfo]:
        """
        按状态获取任务列表
        
        Args:
            status: 任务状态
            
        Returns:
            任务列表
        """
        with self._lock:
            return [t for t in self._tasks.values() if t.status == status]
    
    def get_tasks_by_station(self, station_id: int) -> List[TaskInfo]:
        """
        按工位获取任务列表
        
        Args:
            station_id: 工位ID
            
        Returns:
            任务列表
        """
        with self._lock:
            return [t for t in self._tasks.values() if t.station_id == station_id]
    
    def get_tasks_by_product(self, product_sn: str) -> List[TaskInfo]:
        """
        按产品SN获取任务列表
        
        Args:
            product_sn: 产品SN码
            
        Returns:
            任务列表
        """
        with self._lock:
            return [t for t in self._tasks.values() if t.product_sn == product_sn]
    
    def get_running_tasks(self) -> List[TaskInfo]:
        """获取正在运行的任务"""
        return self.get_tasks_by_status(TaskStatus.RUNNING)
    
    def get_all_tasks(self) -> List[TaskInfo]:
        """获取所有任务"""
        with self._lock:
            return list(self._tasks.values())
    
    def get_task_count(self, status: TaskStatus = None) -> int:
        """
        获取任务数量
        
        Args:
            status: 按状态筛选，None表示所有
            
        Returns:
            任务数量
        """
        if status:
            return len(self.get_tasks_by_status(status))
        return len(self._tasks)
    
    def add_status_callback(self, callback: Callable[[str, TaskStatus], None]):
        """
        添加状态变化回调
        
        Args:
            callback: 回调函数，接收 (task_id, new_status)
        """
        with self._lock:
            self._status_callbacks.append(callback)
    
    def _notify_status_change(self, task_id: str, new_status: TaskStatus):
        """
        通知状态变化
        
        Args:
            task_id: 任务ID
            new_status: 新状态
        """
        for callback in self._status_callbacks:
            try:
                callback(task_id, new_status)
            except Exception as e:
                logger.error(f"状态回调执行失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取任务统计信息
        
        Returns:
            统计信息
        """
        with self._lock:
            stats = {
                'total': len(self._tasks),
                'created': 0,
                'running': 0,
                'paused': 0,
                'completed': 0,
                'failed': 0,
                'cancelled': 0
            }
            
            for task in self._tasks.values():
                status_key = task.status.value
                if status_key in stats:
                    stats[status_key] += 1
            
            return stats
    
    def clear_completed_tasks(self, keep_failed: bool = False):
        """
        清空已完成的任务
        
        Args:
            keep_failed: 是否保留失败的任务
        """
        with self._lock:
            to_remove = []
            
            for task_id, task in self._tasks.items():
                if task.status == TaskStatus.COMPLETED:
                    to_remove.append(task_id)
                elif not keep_failed and task.status == TaskStatus.FAILED:
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self._tasks[task_id]
            
            logger.info(f"清空完成任务: {len(to_remove)} 个")
    
    def clear_all(self):
        """清空所有任务"""
        with self._lock:
            self._tasks.clear()
        logger.info("任务管理器已清空")

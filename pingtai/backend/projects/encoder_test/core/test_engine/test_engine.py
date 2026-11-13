"""
测试引擎核心 - 多工位并行调度、任务隔离、上下文管理
"""
import threading
import uuid
import time
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, Future
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class EngineStatus(Enum):
    """引擎状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"


@dataclass
class Context:
    """任务上下文 - 确保多工位任务完全隔离"""
    task_id: str
    station_id: int
    product_sn: str
    config: Dict[str, Any] = field(default_factory=dict)
    local_storage: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取本地存储数据"""
        return self.local_storage.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置本地存储数据"""
        self.local_storage[key] = value


# 向后兼容别名
TaskContext = Context


class Engine:
    """测试引擎核心 - 支持多工位并行调度"""
    
    def __init__(self, max_workers: int = 4):
        """
        Args:
            max_workers: 最大并行工位数
        """
        self.max_workers = max_workers
        self.status = EngineStatus.IDLE
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks: Dict[str, Future] = {}
        self._contexts: Dict[str, TaskContext] = {}
        self._lock = threading.RLock()
        self._pause_event = threading.Event()
        self._pause_event.set()  # 默认不暂停
        self._results: Dict[str, Dict[str, Any]] = {}
        self._callbacks: Dict[str, Callable] = {}
    
    def create_context(self, station_id: int, product_sn: str, 
                       config: Dict[str, Any] = None) -> TaskContext:
        """
        创建任务上下文（任务完全隔离）
        
        Args:
            station_id: 工位ID
            product_sn: 产品SN码
            config: 配置参数
            
        Returns:
            TaskContext实例
        """
        task_id = str(uuid.uuid4())
        context = TaskContext(
            task_id=task_id,
            station_id=station_id,
            product_sn=product_sn,
            config=config or {}
        )
        
        with self._lock:
            self._contexts[task_id] = context
        
        logger.info(f"创建任务上下文: {task_id} (工位{station_id}, SN:{product_sn})")
        return context
    
    def submit_task(self, context: TaskContext, test_func: Callable, 
                    callback: Callable = None) -> str:
        """
        提交测试任务到引擎
        
        Args:
            context: 任务上下文
            test_func: 测试函数
            callback: 完成回调函数
            
        Returns:
            task_id
        """
        if self.status == EngineStatus.STOPPING:
            raise RuntimeError("引擎正在停止，无法提交新任务")
        
        task_id = context.task_id
        
        def task_wrapper():
            """任务包装器 - 确保状态监控和回调执行"""
            try:
                # 等待暂停恢复
                self._pause_event.wait()
                
                if self.status == EngineStatus.STOPPING:
                    return {'status': 'stopped', 'task_id': task_id}
                
                logger.info(f"开始执行任务: {task_id}")
                result = test_func(context)
                
                with self._lock:
                    self._results[task_id] = {
                        'status': 'completed',
                        'result': result,
                        'task_id': task_id,
                        'station_id': context.station_id,
                        'product_sn': context.product_sn,
                        'completed_at': time.time()
                    }
                
                # 执行回调
                if callback:
                    try:
                        callback(task_id, result)
                    except Exception as e:
                        logger.error(f"任务回调执行失败: {e}")
                
                logger.info(f"任务执行完成: {task_id}")
                return {'status': 'completed', 'task_id': task_id}
                
            except Exception as e:
                logger.error(f"任务执行失败: {task_id}, 错误: {e}")
                with self._lock:
                    self._results[task_id] = {
                        'status': 'error',
                        'error': str(e),
                        'task_id': task_id,
                        'station_id': context.station_id,
                        'product_sn': context.product_sn,
                        'completed_at': time.time()
                    }
                return {'status': 'error', 'task_id': task_id, 'error': str(e)}
        
        with self._lock:
            future = self._executor.submit(task_wrapper)
            self._tasks[task_id] = future
            if callback:
                self._callbacks[task_id] = callback
        
        logger.info(f"任务已提交: {task_id}")
        return task_id
    
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务结果
        """
        with self._lock:
            return self._results.get(task_id)
    
    def is_task_completed(self, task_id: str) -> bool:
        """
        检查任务是否完成
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否完成
        """
        with self._lock:
            future = self._tasks.get(task_id)
            if future:
                return future.done()
            return task_id in self._results
    
    def get_station_context(self, station_id: int) -> Optional[TaskContext]:
        """
        获取指定工位的上下文
        
        Args:
            station_id: 工位ID
            
        Returns:
            TaskContext或None
        """
        with self._lock:
            for context in self._contexts.values():
                if context.station_id == station_id:
                    return context
        return None
    
    def pause(self):
        """暂停所有任务"""
        if self.status == EngineStatus.RUNNING:
            self.status = EngineStatus.PAUSED
            self._pause_event.clear()
            logger.info("引擎已暂停")
    
    def resume(self):
        """恢复所有任务"""
        if self.status == EngineStatus.PAUSED:
            self.status = EngineStatus.RUNNING
            self._pause_event.set()
            logger.info("引擎已恢复")
    
    def stop(self, timeout: float = 30.0):
        """
        停止所有任务
        
        Args:
            timeout: 等待超时时间（秒）
        """
        if self.status in [EngineStatus.STOPPING, EngineStatus.STOPPED]:
            return
        
        self.status = EngineStatus.STOPPING
        logger.info("引擎正在停止...")
        
        # 恢复暂停状态以便任务可以完成
        self._pause_event.set()
        
        # 等待所有任务完成
        futures = list(self._tasks.values())
        for future in futures:
            try:
                future.result(timeout=timeout / len(futures) if futures else timeout)
            except Exception as e:
                logger.warning(f"任务停止异常: {e}")
        
        self.status = EngineStatus.STOPPED
        logger.info("引擎已停止")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取引擎状态
        
        Returns:
            状态信息
        """
        with self._lock:
            running_tasks = sum(1 for f in self._tasks.values() if not f.done())
            completed_tasks = len(self._results)
            
            return {
                'status': self.status.value,
                'max_workers': self.max_workers,
                'running_tasks': running_tasks,
                'completed_tasks': completed_tasks,
                'total_tasks': len(self._tasks),
                'paused': not self._pause_event.is_set()
            }
    
    def reset(self):
        """重置引擎状态"""
        with self._lock:
            self._tasks.clear()
            self._contexts.clear()
            self._results.clear()
            self._callbacks.clear()
        
        self.status = EngineStatus.IDLE
        self._pause_event.set()
        logger.info("引擎已重置")
    
    def shutdown(self, wait: bool = True):
        """
        关闭引擎
        
        Args:
            wait: 是否等待所有任务完成
        """
        self.stop()
        self._executor.shutdown(wait=wait)
        logger.info("引擎已关闭")
    
    @staticmethod
    @contextmanager
    def run_context(max_workers: int = 4):
        """
        引擎运行上下文管理器
        
        Args:
            max_workers: 最大工位数
        """
        engine = Engine(max_workers=max_workers)
        try:
            engine.status = EngineStatus.RUNNING
            yield engine
        finally:
            engine.shutdown(wait=True)


# 向后兼容别名
TestEngine = Engine

"""
工业自动化测试平台 - 事件总线实现
实现运行时事件的发布订阅机制
"""
import asyncio
import threading
import queue
from typing import Type, Dict, List, Callable, Awaitable, Any
from abc import ABC, abstractmethod
from .events import RuntimeEvent
import logging
from concurrent.futures import ThreadPoolExecutor
import time


class IEventBus(ABC):
    """事件总线接口"""
    
    @abstractmethod
    async def publish(self, event: RuntimeEvent) -> None:
        """发布事件"""
        pass
    
    @abstractmethod
    def subscribe(self, event_type: Type[RuntimeEvent], handler: Callable[[RuntimeEvent], Awaitable[None]]) -> None:
        """订阅事件"""
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: Type[RuntimeEvent], handler: Callable[[RuntimeEvent], Awaitable[None]]) -> None:
        """取消订阅"""
        pass


class InMemoryEventBus(IEventBus):
    """内存事件总线实现"""
    
    def __init__(self, executor: ThreadPoolExecutor = None):
        self._subscribers: Dict[Type[RuntimeEvent], List[Callable[[RuntimeEvent], Awaitable[None]]]] = {}
        self._lock = threading.Lock()
        self._executor = executor or ThreadPoolExecutor(max_workers=10)
        self.logger = logging.getLogger(__name__)
        
        # 使用线程安全的队列，可以在任何线程中放入事件
        self._sync_queue = queue.Queue()  # 用于跨线程事件传递
        self._async_queue = None  # 用于asyncio处理，在事件循环中创建
        self._running = True
    
    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        """设置事件循环"""
        # 在事件循环中创建asyncio队列
        future = asyncio.run_coroutine_threadsafe(self._create_async_queue(), loop)
        future.result()  # 等待队列创建完成
    
    async def _create_async_queue(self):
        """在正确的事件循环中创建asyncio队列"""
        self._async_queue = asyncio.Queue()
        
        # 启动后台任务，将同步队列中的事件转移到异步队列
        asyncio.create_task(self._sync_to_async_bridge())
    
    async def _sync_to_async_bridge(self):
        """将同步队列中的事件转移到异步队列的桥接任务"""
        self.logger.info("桥接任务启动")
        while self._running:
            try:
                # 从同步队列获取事件，使用非阻塞方式
                try:
                    event = self._sync_queue.get_nowait()
                    self.logger.info(f"从同步队列获取事件: {type(event).__name__}")
                    # 等待异步队列准备好
                    start_time = time.time()
                    while self._running and self._async_queue is None:
                        if time.time() - start_time > 5:  # 5秒超时
                            self.logger.warning("异步队列初始化超时")
                            break
                        self.logger.debug("等待异步队列初始化...")
                        await asyncio.sleep(0.01)
                    
                    if self._async_queue and self._running:
                        await self._async_queue.put(event)
                        self.logger.info(f"事件已放入异步队列: {type(event).__name__}")
                except queue.Empty:
                    # 如果同步队列为空，短暂休眠后继续
                    await asyncio.sleep(0.01)
            except Exception as e:
                self.logger.error(f"桥接任务错误: {e}", exc_info=True)
                await asyncio.sleep(0.1)  # 错误后稍作休眠
        self.logger.info("桥接任务结束")
        
    async def publish(self, event: RuntimeEvent) -> None:
        """发布事件到队列"""
        # 将事件放入同步队列，这样可以从任何线程发布事件
        self._sync_queue.put(event)
    
    def subscribe(self, event_type: Type[RuntimeEvent], handler: Callable[[RuntimeEvent], Awaitable[None]]) -> None:
        """订阅事件"""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: Type[RuntimeEvent], handler: Callable[[RuntimeEvent], Awaitable[None]]) -> None:
        """取消订阅"""
        with self._lock:
            if event_type in self._subscribers:
                if handler in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(handler)
    
    async def start_processing(self):
        """开始处理事件队列"""
        self.logger.info("事件总线开始处理事件")
        while self._running:
            try:
                # 从异步队列获取事件，最多等待1秒
                event = await asyncio.wait_for(self._async_queue.get(), timeout=1.0)
                self.logger.info(f"从异步队列获取事件: {type(event).__name__}")
                
                # 并行处理所有订阅者
                await self._process_event(event)
                
            except asyncio.TimeoutError:
                # 超时是正常的，继续循环
                continue
            except Exception as e:
                self.logger.error(f"处理事件时发生错误: {e}", exc_info=True)
    
    def get_queue_size(self):
        """获取事件队列大小"""
        if self._async_queue:
            return self._async_queue.qsize()
        else:
            # 返回同步队列的近似大小
            return self._sync_queue.qsize()
    
    async def _process_event(self, event: RuntimeEvent):
        """处理单个事件"""
        # 查找所有匹配的订阅者
        handlers = []
        
        with self._lock:
            # 查找精确匹配的处理器
            if type(event) in self._subscribers:
                handlers.extend(self._subscribers[type(event)])
            
            # 查找父类匹配的处理器
            for event_type, subscribers in self._subscribers.items():
                if isinstance(event, event_type) and event_type != type(event):
                    handlers.extend(subscribers)
        
        if not handlers:
            return  # 没有处理器，直接返回
        
        # 并行执行所有处理器
        tasks = []
        for handler in handlers:
            try:
                task = asyncio.create_task(self._safe_call_handler(handler, event))
                tasks.append(task)
            except Exception as e:
                self.logger.error(f"创建处理器任务失败: {e}", exc_info=True)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _safe_call_handler(self, handler: Callable[[RuntimeEvent], Awaitable[None]], event: RuntimeEvent):
        """安全调用处理器，捕获异常"""
        try:
            start_time = time.time()
            await handler(event)
            duration = (time.time() - start_time) * 1000
            self.logger.debug(f"处理器 {handler.__name__} 处理事件 {type(event).__name__} 耗时 {duration:.2f}ms")
        except Exception as e:
            self.logger.error(f"处理器 {handler.__name__} 处理事件 {type(event).__name__} 时发生错误: {e}", exc_info=True)
    
    def stop_processing(self):
        """停止处理事件"""
        self._running = False
        self._executor.shutdown(wait=True)


class EventBusManager:
    """事件总线管理器 - 单例模式"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._event_bus = InMemoryEventBus()
            self._initialized = True
    
    def get_event_bus(self) -> IEventBus:
        """获取事件总线实例"""
        return self._event_bus
    
    async def publish_event(self, event: RuntimeEvent):
        """发布事件的便捷方法"""
        await self._event_bus.publish(event)
    
    def subscribe_to_event(self, event_type: type, handler: Callable[[RuntimeEvent], Awaitable[None]]):
        """订阅事件的便捷方法"""
        self._event_bus.subscribe(event_type, handler)


# 便捷函数
def get_event_bus() -> IEventBus:
    """获取事件总线实例"""
    manager = EventBusManager()
    return manager.get_event_bus()


async def publish_event(event: RuntimeEvent):
    """发布事件的便捷函数"""
    manager = EventBusManager()
    await manager.publish_event(event)


def subscribe_to_event(event_type: type, handler: Callable[[RuntimeEvent], Awaitable[None]]):
    """订阅事件的便捷函数"""
    manager = EventBusManager()
    manager.subscribe_to_event(event_type, handler)
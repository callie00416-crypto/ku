"""
工业自动化测试平台 - 运行时事件处理主循环
用于启动和管理事件总线处理循环
"""
import asyncio
import threading
from typing import Optional
from .event_bus import get_event_bus, InMemoryEventBus
from .persistence_worker import start_persistence_worker
import logging


class RuntimeEventManager:
    """运行时事件管理器"""
    
    def __init__(self):
        self._event_bus: Optional[InMemoryEventBus] = None
        self._processing_task: Optional[asyncio.Task] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """启动事件管理器"""
        if self._running:
            return
        
        self._running = True
        
        # 在新线程中启动事件循环和组件
        self._thread = threading.Thread(target=self._run_event_loop_and_components)
        self._thread.daemon = True
        self._thread.start()
        
        # 等待组件启动
        import time
        time.sleep(2)  # 等待组件初始化
        
        self.logger.info("运行时事件管理器已启动")
    
    def _run_event_loop_and_components(self):
        """在新线程中运行事件循环和初始化组件"""
        # 创建并设置事件循环
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        # 初始化组件
        self._loop.run_until_complete(self._initialize_components())
        
        # 保持事件循环运行
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self._loop.close()
    
    async def _initialize_components(self):
        """初始化组件"""
        # 获取事件总线
        event_bus = get_event_bus()
        if isinstance(event_bus, InMemoryEventBus):
            self._event_bus = event_bus
            # 设置正确的事件循环
            self._event_bus.set_event_loop(asyncio.get_running_loop())
        
        # 启动持久化工作器
        await start_persistence_worker()
        
        # 启动事件处理
        if self._event_bus:
            self._processing_task = asyncio.create_task(self._event_bus.start_processing())
    
    def stop(self):
        """停止事件管理器"""
        if not self._running:
            return
        
        self._running = False
        
        if self._loop and self._loop.is_running():
            # 在事件循环线程中安全地停止任务
            def stop_loop():
                if self._processing_task:
                    self._processing_task.cancel()
                self._loop.stop()
            
            self._loop.call_soon_threadsafe(stop_loop)
        
        if self._thread:
            self._thread.join(timeout=5.0)
        
        self.logger.info("运行时事件管理器已停止")
    
    def is_running(self):
        """检查是否正在运行"""
        return self._running


# 全局管理器实例
_runtime_event_manager = RuntimeEventManager()


def get_runtime_event_manager() -> RuntimeEventManager:
    """获取运行时事件管理器"""
    return _runtime_event_manager


def start_runtime_event_manager():
    """启动运行时事件管理器"""
    _runtime_event_manager.start()


def stop_runtime_event_manager():
    """停止运行时事件管理器"""
    _runtime_event_manager.stop()
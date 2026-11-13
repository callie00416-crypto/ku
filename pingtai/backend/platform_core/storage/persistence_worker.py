"""
持久化工作者 - 异步持久化处理器

【职责】
- 处理领域事件的持久化
- 管理异步数据存储
- 维护数据一致性

【设计原则】
- 事件驱动的持久化
- 异步处理避免阻塞
- 事务一致性保障
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
import asyncio
import threading
import queue
from datetime import datetime
import logging

from runtime.event_bus import EventBus
from encoder_test.domain.common.aggregate_root import AggregateRoot
from .repositories import (
    ITaskRepository, IReportRepository, 
    IAlarmRepository, IStationRepository, 
    IDeviceRepository
)


class IPersistenceWorker(ABC):
    """持久化工作者接口"""
    
    @abstractmethod
    async def start(self) -> None:
        """启动持久化工作者"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """停止持久化工作者"""
        pass

    @abstractmethod
    async def process_event(self, event_data: Dict[str, Any]) -> bool:
        """处理领域事件"""
        pass

    @abstractmethod
    async def flush_pending_operations(self) -> None:
        """刷新待处理操作"""
        pass


class PersistenceWorker(IPersistenceWorker):
    """持久化工作者实现"""
    
    def __init__(
        self,
        task_repository: ITaskRepository,
        report_repository: IReportRepository,
        alarm_repository: IAlarmRepository,
        station_repository: IStationRepository,
        device_repository: IDeviceRepository,
        event_bus: EventBus,
        batch_size: int = 100,
        flush_interval: float = 1.0  # 秒
    ):
        self._task_repository = task_repository
        self._report_repository = report_repository
        self._alarm_repository = alarm_repository
        self._station_repository = station_repository
        self._device_repository = device_repository
        
        self._event_bus = event_bus
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        
        self._queue = queue.Queue()
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        
        self._pending_operations = []
        self._last_flush_time = datetime.now()
        
        self._logger = logging.getLogger(__name__)

    async def start(self) -> None:
        """启动持久化工作者"""
        self._running = True
        self._loop = asyncio.get_event_loop()
        
        # 启动工作线程
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        
        # 订阅相关事件
        await self._subscribe_events()
        
        self._logger.info("PersistenceWorker started")

    async def stop(self) -> None:
        """停止持久化工作者"""
        self._running = False
        
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)  # 等待最多5秒
        
        # 确保所有待处理操作都被持久化
        await self.flush_pending_operations()
        
        self._logger.info("PersistenceWorker stopped")

    async def _subscribe_events(self) -> None:
        """订阅相关事件"""
        # 订阅任务相关的事件
        await self._event_bus.subscribe("task.created", self._handle_task_event)
        await self._event_bus.subscribe("task.updated", self._handle_task_event)
        await self._event_bus.subscribe("task.completed", self._handle_task_event)
        await self._event_bus.subscribe("task.failed", self._handle_task_event)
        
        # 订阅报告相关的事件
        await self._event_bus.subscribe("report.generated", self._handle_report_event)
        await self._event_bus.subscribe("report.archived", self._handle_report_event)
        await self._event_bus.subscribe("report.attachment_added", self._handle_report_event)
        
        # 订阅告警相关的事件
        await self._event_bus.subscribe("alarm.triggered", self._handle_alarm_event)
        await self._event_bus.subscribe("alarm.acknowledged", self._handle_alarm_event)
        await self._event_bus.subscribe("alarm.resolved", self._handle_alarm_event)
        await self._event_bus.subscribe("alarm.closed", self._handle_alarm_event)
        
        # 订阅工位相关的事件
        await self._event_bus.subscribe("station.created", self._handle_station_event)
        await self._event_bus.subscribe("station.updated", self._handle_station_event)
        await self._event_bus.subscribe("station.status_changed", self._handle_station_event)
        
        # 订阅设备相关的事件
        await self._event_bus.subscribe("device.created", self._handle_device_event)
        await self._event_bus.subscribe("device.updated", self._handle_device_event)
        await self._event_bus.subscribe("device.status_changed", self._handle_device_event)
        await self._event_bus.subscribe("device.connected", self._handle_device_event)
        await self._event_bus.subscribe("device.disconnected", self._handle_device_event)

    def _worker_loop(self) -> None:
        """工作线程主循环"""
        while self._running:
            try:
                # 检查是否需要刷新
                current_time = datetime.now()
                if (current_time - self._last_flush_time).total_seconds() >= self._flush_interval:
                    # 在工作线程中运行异步函数
                    asyncio.run_coroutine_threadsafe(
                        self.flush_pending_operations(),
                        self._loop
                    ).result(timeout=2.0)  # 等待最多2秒
                    
                    self._last_flush_time = current_time
                
                # 等待一段时间避免忙等待
                import time
                time.sleep(0.1)
                
            except Exception as e:
                self._logger.error(f"Error in persistence worker loop: {e}")

    async def process_event(self, event_data: Dict[str, Any]) -> bool:
        """处理领域事件"""
        try:
            event_type = event_data.get('event_type', '')
            
            if event_type.startswith('task.'):
                return await self._process_task_event(event_data)
            elif event_type.startswith('report.'):
                return await self._process_report_event(event_data)
            elif event_type.startswith('alarm.'):
                return await self._process_alarm_event(event_data)
            elif event_type.startswith('station.'):
                return await self._process_station_event(event_data)
            elif event_type.startswith('device.'):
                return await self._process_device_event(event_data)
            else:
                self._logger.warning(f"Unknown event type: {event_type}")
                return False
                
        except Exception as e:
            self._logger.error(f"Error processing event {event_data}: {e}")
            return False

    async def _handle_task_event(self, event_data: Dict[str, Any]) -> None:
        """处理任务事件"""
        await self.process_event(event_data)

    async def _handle_report_event(self, event_data: Dict[str, Any]) -> None:
        """处理报告事件"""
        await self.process_event(event_data)

    async def _handle_alarm_event(self, event_data: Dict[str, Any]) -> None:
        """处理告警事件"""
        await self.process_event(event_data)

    async def _handle_station_event(self, event_data: Dict[str, Any]) -> None:
        """处理工位事件"""
        await self.process_event(event_data)

    async def _handle_device_event(self, event_data: Dict[str, Any]) -> None:
        """处理设备事件"""
        await self.process_event(event_data)

    async def _process_task_event(self, event_data: Dict[str, Any]) -> bool:
        """处理任务事件"""
        try:
            # 从事件数据中提取任务信息并持久化
            # 这里应该是从某种缓存或特定位置获取完整的任务对象
            # 由于事件数据通常是精简的，我们需要通过其他方式获取完整对象
            task_id = event_data.get('aggregate_id')
            if task_id:
                # 获取最新的任务对象进行持久化
                # 这里简化处理，实际应用中可能需要从内存缓存或其他地方获取
                pass
            
            # 将操作加入待处理队列
            self._pending_operations.append(('task', event_data))
            
            # 如果达到批次大小，立即刷新
            if len(self._pending_operations) >= self._batch_size:
                await self.flush_pending_operations()
                
            return True
        except Exception as e:
            self._logger.error(f"Error processing task event: {e}")
            return False

    async def _process_report_event(self, event_data: Dict[str, Any]) -> bool:
        """处理报告事件"""
        try:
            self._pending_operations.append(('report', event_data))
            
            if len(self._pending_operations) >= self._batch_size:
                await self.flush_pending_operations()
                
            return True
        except Exception as e:
            self._logger.error(f"Error processing report event: {e}")
            return False

    async def _process_alarm_event(self, event_data: Dict[str, Any]) -> bool:
        """处理告警事件"""
        try:
            self._pending_operations.append(('alarm', event_data))
            
            if len(self._pending_operations) >= self._batch_size:
                await self.flush_pending_operations()
                
            return True
        except Exception as e:
            self._logger.error(f"Error processing alarm event: {e}")
            return False

    async def _process_station_event(self, event_data: Dict[str, Any]) -> bool:
        """处理工位事件"""
        try:
            self._pending_operations.append(('station', event_data))
            
            if len(self._pending_operations) >= self._batch_size:
                await self.flush_pending_operations()
                
            return True
        except Exception as e:
            self._logger.error(f"Error processing station event: {e}")
            return False

    async def _process_device_event(self, event_data: Dict[str, Any]) -> bool:
        """处理设备事件"""
        try:
            self._pending_operations.append(('device', event_data))
            
            if len(self._pending_operations) >= self._batch_size:
                await self.flush_pending_operations()
                
            return True
        except Exception as e:
            self._logger.error(f"Error processing device event: {e}")
            return False

    async def flush_pending_operations(self) -> None:
        """刷新待处理操作"""
        if not self._pending_operations:
            return

        operations_to_process = self._pending_operations.copy()
        self._pending_operations.clear()

        try:
            for op_type, event_data in operations_to_process:
                if op_type == 'task':
                    await self._flush_task_operation(event_data)
                elif op_type == 'report':
                    await self._flush_report_operation(event_data)
                elif op_type == 'alarm':
                    await self._flush_alarm_operation(event_data)
                elif op_type == 'station':
                    await self._flush_station_operation(event_data)
                elif op_type == 'device':
                    await self._flush_device_operation(event_data)

            self._logger.info(f"Flushed {len(operations_to_process)} pending operations")

        except Exception as e:
            self._logger.error(f"Error flushing pending operations: {e}")
            # 将失败的操作重新加入队列
            self._pending_operations.extend(operations_to_process)

    async def _flush_task_operation(self, event_data: Dict[str, Any]) -> None:
        """刷新任务操作"""
        # 实现具体的任务持久化逻辑
        pass

    async def _flush_report_operation(self, event_data: Dict[str, Any]) -> None:
        """刷新报告操作"""
        # 实现具体的报告持久化逻辑
        pass

    async def _flush_alarm_operation(self, event_data: Dict[str, Any]) -> None:
        """刷新告警操作"""
        # 实现具体的告警持久化逻辑
        pass

    async def _flush_station_operation(self, event_data: Dict[str, Any]) -> None:
        """刷新工位操作"""
        # 实现具体的工位持久化逻辑
        pass

    async def _flush_device_operation(self, event_data: Dict[str, Any]) -> None:
        """刷新设备操作"""
        # 实现具体的设备持久化逻辑
        pass
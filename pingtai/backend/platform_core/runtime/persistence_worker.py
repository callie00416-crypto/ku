"""
工业自动化测试平台 - 持久化工作器
将运行时事件持久化到数据库
"""
import asyncio
from typing import Dict, Type, Callable, Awaitable
from datetime import datetime
import logging
from .event_bus import get_event_bus, IEventBus
from .events import (
    RuntimeEvent, TaskStarted, TaskCompleted, TaskFailed,
    AlarmTriggered, AlarmResolved, DeviceConnected, DeviceDisconnected,
    WorkOrderStarted, WorkOrderCompleted
)
from ..application.workorder.repository import IWorkOrderRepository
from ..storage.models import TaskModel, AlarmModel, DeviceModel, WorkOrderModel
from sqlalchemy.orm import sessionmaker


class PersistenceWorker:
    """持久化工作器 - 将运行时事件持久化到数据库"""
    
    def __init__(self, session_factory: sessionmaker, workorder_repository: IWorkOrderRepository):
        self.session_factory = session_factory
        self.workorder_repository = workorder_repository
        self.logger = logging.getLogger(__name__)
        self._running = False
        self._task = None
        
        # 事件处理器映射
        self._handlers: Dict[Type[RuntimeEvent], Callable[[RuntimeEvent], Awaitable[None]]] = {
            TaskStarted: self._handle_task_started,
            TaskCompleted: self._handle_task_completed,
            TaskFailed: self._handle_task_failed,
            AlarmTriggered: self._handle_alarm_triggered,
            AlarmResolved: self._handle_alarm_resolved,
            DeviceConnected: self._handle_device_connected,
            DeviceDisconnected: self._handle_device_disconnected,
            WorkOrderStarted: self._handle_workorder_started,
            WorkOrderCompleted: self._handle_workorder_completed,
        }
    
    async def start(self):
        """启动持久化工作器"""
        if self._running:
            return
        
        self._running = True
        event_bus = get_event_bus()
        
        # 订阅所有感兴趣的事件
        for event_type, handler in self._handlers.items():
            event_bus.subscribe(event_type, handler)
        
        self.logger.info("持久化工作器已启动")
    
    async def stop(self):
        """停止持久化工作器"""
        if not self._running:
            return
        
        self._running = False
        event_bus = get_event_bus()
        
        # 取消订阅所有事件
        for event_type, handler in self._handlers.items():
            event_bus.unsubscribe(event_type, handler)
        
        self.logger.info("持久化工作器已停止")
    
    async def _handle_task_started(self, event: TaskStarted):
        """处理任务开始事件"""
        try:
            with self.session_factory() as session:
                task = session.query(TaskModel).filter(TaskModel.task_id == event.task_id).first()
                if task:
                    task.status = 'running'
                    task.actor_id = event.actor_id
                    task.start_time = datetime.utcnow()
                    session.commit()
                    self.logger.info(f"任务 {event.task_id} 状态已更新为运行中")
        except Exception as e:
            self.logger.error(f"处理任务开始事件失败: {e}", exc_info=True)
    
    async def _handle_task_completed(self, event: TaskCompleted):
        """处理任务完成事件"""
        try:
            with self.session_factory() as session:
                task = session.query(TaskModel).filter(TaskModel.task_id == event.task_id).first()
                if task:
                    task.status = 'completed'
                    task.result = event.result
                    task.duration_ms = event.duration_ms
                    task.end_time = datetime.utcnow()
                    session.commit()
                    self.logger.info(f"任务 {event.task_id} 状态已更新为完成，结果: {event.result}")
        except Exception as e:
            self.logger.error(f"处理任务完成事件失败: {e}", exc_info=True)
    
    async def _handle_task_failed(self, event: TaskFailed):
        """处理任务失败事件"""
        try:
            with self.session_factory() as session:
                task = session.query(TaskModel).filter(TaskModel.task_id == event.task_id).first()
                if task:
                    task.status = 'failed'
                    task.result = 'FAIL'
                    task.error_code = event.error_code
                    task.error_message = event.error_message
                    task.end_time = datetime.utcnow()
                    session.commit()
                    self.logger.info(f"任务 {event.task_id} 状态已更新为失败，错误: {event.error_code}")
        except Exception as e:
            self.logger.error(f"处理任务失败事件失败: {e}", exc_info=True)
    
    async def _handle_alarm_triggered(self, event: AlarmTriggered):
        """处理告警触发事件"""
        try:
            with self.session_factory() as session:
                # 检查是否已存在相同类型的活跃告警（去重）
                existing_alarm = session.query(AlarmModel).filter(
                    AlarmModel.alarm_code == event.alarm_code,
                    AlarmModel.status == 'active'
                ).first()
                
                if not existing_alarm:
                    alarm = AlarmModel(
                        alarm_id=event.alarm_id,
                        alarm_code=event.alarm_code,
                        alarm_level=event.alarm_level,
                        message=event.message,
                        status='active',
                        occurred_at=event.timestamp,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(alarm)
                    session.commit()
                    self.logger.info(f"告警 {event.alarm_id} 已创建")
                else:
                    self.logger.info(f"相同告警 {event.alarm_code} 已存在，已忽略")
        except Exception as e:
            self.logger.error(f"处理告警触发事件失败: {e}", exc_info=True)
    
    async def _handle_alarm_resolved(self, event: AlarmResolved):
        """处理告警解决事件"""
        try:
            with self.session_factory() as session:
                alarm = session.query(AlarmModel).filter(
                    AlarmModel.alarm_id == event.alarm_id
                ).first()
                
                if alarm:
                    alarm.status = 'resolved'
                    alarm.resolved_at = datetime.utcnow()
                    alarm.updated_at = datetime.utcnow()
                    session.commit()
                    self.logger.info(f"告警 {event.alarm_id} 状态已更新为已解决")
        except Exception as e:
            self.logger.error(f"处理告警解决事件失败: {e}", exc_info=True)
    
    async def _handle_device_connected(self, event: DeviceConnected):
        """处理设备连接事件"""
        try:
            with self.session_factory() as session:
                device = session.query(DeviceModel).filter(
                    DeviceModel.device_id == event.device_id
                ).first()
                
                if device:
                    device.connect_status = 'connected'
                    device.is_connected = True
                    device.updated_at = datetime.utcnow()
                    session.commit()
                    self.logger.info(f"设备 {event.device_id} 状态已更新为已连接")
        except Exception as e:
            self.logger.error(f"处理设备连接事件失败: {e}", exc_info=True)
    
    async def _handle_device_disconnected(self, event: DeviceDisconnected):
        """处理设备断开连接事件"""
        try:
            with self.session_factory() as session:
                device = session.query(DeviceModel).filter(
                    DeviceModel.device_id == event.device_id
                ).first()
                
                if device:
                    device.connect_status = 'disconnected'
                    device.is_connected = False
                    device.updated_at = datetime.utcnow()
                    session.commit()
                    self.logger.info(f"设备 {event.device_id} 状态已更新为已断开，原因: {event.reason}")
        except Exception as e:
            self.logger.error(f"处理设备断开连接事件失败: {e}", exc_info=True)
    
    async def _handle_workorder_started(self, event: WorkOrderStarted):
        """处理工单开始事件"""
        try:
            # 更新工单状态
            workorder = self.workorder_repository.find_by_id(event.workorder_id)
            if workorder:
                workorder.start()
                self.workorder_repository.save(workorder)
                self.logger.info(f"工单 {event.workorder_id} 状态已更新为运行中")
        except Exception as e:
            self.logger.error(f"处理工单开始事件失败: {e}", exc_info=True)
    
    async def _handle_workorder_completed(self, event: WorkOrderCompleted):
        """处理工单完成事件"""
        try:
            # 更新工单状态和统计数据
            workorder = self.workorder_repository.find_by_id(event.workorder_id)
            if workorder:
                workorder.complete()
                # 更新数量统计
                workorder.completed_quantity = event.completed_quantity
                workorder.ng_quantity = event.ng_quantity
                self.workorder_repository.save(workorder)
                self.logger.info(f"工单 {event.workorder_id} 状态已更新为已完成")
        except Exception as e:
            self.logger.error(f"处理工单完成事件失败: {e}", exc_info=True)


class PersistenceWorkerManager:
    """持久化工作器管理器"""
    
    def __init__(self):
        self._worker = None
        self._started = False
    
    def initialize(self, session_factory: sessionmaker, workorder_repository: IWorkOrderRepository):
        """初始化持久化工作器"""
        if self._worker is None:
            self._worker = PersistenceWorker(session_factory, workorder_repository)
    
    async def start(self):
        """启动持久化工作器"""
        if not self._started and self._worker:
            await self._worker.start()
            self._started = True
    
    async def stop(self):
        """停止持久化工作器"""
        if self._started and self._worker:
            await self._worker.stop()
            self._started = False
    
    def get_worker(self) -> PersistenceWorker:
        """获取持久化工作器实例"""
        return self._worker


# 全局管理器实例
_persistence_worker_manager = PersistenceWorkerManager()


def get_persistence_worker_manager() -> PersistenceWorkerManager:
    """获取持久化工作器管理器"""
    return _persistence_worker_manager


def initialize_persistence_worker(session_factory: sessionmaker, workorder_repository: IWorkOrderRepository):
    """初始化持久化工作器"""
    _persistence_worker_manager.initialize(session_factory, workorder_repository)


async def start_persistence_worker():
    """启动持久化工作器"""
    await _persistence_worker_manager.start()


async def stop_persistence_worker():
    """停止持久化工作器"""
    await _persistence_worker_manager.stop()
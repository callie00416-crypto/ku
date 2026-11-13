"""
工业自动化测试平台 - 事件总线调试测试
用于调试事件总线功能
"""
import asyncio
import threading
import time
from encoder_test.runtime.event_bus import get_event_bus, publish_event
from encoder_test.runtime.events import TaskStarted
from encoder_test.runtime.event_manager import RuntimeEventManager
from encoder_test.runtime.persistence_worker import initialize_persistence_worker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from encoder_test.storage.models import Base, TaskModel
from encoder_test.application.workorder.repository_impl import WorkOrderRepository


def debug_event_bus():
    print("开始事件总线调试...")
    
    # 创建数据库
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    # 创建工单仓库
    workorder_repo = WorkOrderRepository(Session)
    
    # 初始化持久化工作器
    initialize_persistence_worker(Session, workorder_repo)
    
    # 创建事件管理器
    event_manager = RuntimeEventManager()
    
    print("启动事件管理器...")
    event_manager.start()
    
    # 等待组件启动
    time.sleep(3)
    
    # 检查事件总线状态
    event_bus = get_event_bus()
    print(f"事件总线类型: {type(event_bus)}")
    print(f"队列大小: {event_bus.get_queue_size()}")
    
    # 创建测试任务
    from datetime import datetime
    now = datetime.utcnow()
    with Session() as session:
        task = TaskModel(
            id="DEBUG_TASK_001",
            task_id="DEBUG_TASK_001",
            workorder_id="WO001",
            station_id=1,
            device_id="DEV001",
            sn="SN001",
            task_type="DEBUG",
            status="pending",
            created_at=now,
            updated_at=now
        )
        session.add(task)
        session.commit()
        print("创建了测试任务")
    
    # 发布事件前检查状态
    print("发布事件前任务状态:")
    with Session() as session:
        task = session.query(TaskModel).filter(TaskModel.task_id == "DEBUG_TASK_001").first()
        print(f"  状态: {task.status}, 执行者: {task.actor_id}")
    
    # 发布事件
    print("发布TaskStarted事件...")
    event = TaskStarted(
        event_id="DEBUG_EVT_001",
        timestamp=datetime.utcnow(),
        source="Debug",
        payload={"debug": True},
        task_id="DEBUG_TASK_001",
        actor_id="DEBUG_ACTOR"
    )
    
    asyncio.run(publish_event(event))
    print("事件已发布")
    
    # 等待处理
    time.sleep(3)
    
    # 检查队列状态
    print(f"发布事件后队列大小: {event_bus.get_queue_size()}")
    
    # 检查任务状态
    print("事件处理后任务状态:")
    with Session() as session:
        task = session.query(TaskModel).filter(TaskModel.task_id == "DEBUG_TASK_001").first()
        print(f"  状态: {task.status}, 执行者: {task.actor_id}")
    
    # 停止事件管理器
    event_manager.stop()
    print("事件管理器已停止")


if __name__ == "__main__":
    debug_event_bus()
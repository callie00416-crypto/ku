"""
工业自动化测试平台 - 事件系统演示
展示完整的事件驱动架构
"""
import asyncio
import threading
import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from encoder_test.storage.models import Base, TaskModel
from encoder_test.storage.migration_manager import DatabaseMigrationManager
from encoder_test.application.workorder.repository_impl import WorkOrderRepository
from encoder_test.runtime.events import TaskStarted, TaskCompleted
from encoder_test.runtime.event_bus import get_event_bus, publish_event
from encoder_test.runtime.persistence_worker import initialize_persistence_worker
from encoder_test.runtime.event_manager import RuntimeEventManager


def demo_event_driven_architecture():
    """演示事件驱动架构"""
    print("开始工业自动化测试平台事件驱动架构演示")
    print("="*60)
    
    # 创建数据库
    temp_db_fd, temp_db_path = None, ":memory:"  # 使用内存数据库进行演示
    database_url = f"sqlite:///{temp_db_path}"
    
    # 创建数据库表
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    # 创建工单仓库
    workorder_repo = WorkOrderRepository(Session)
    
    # 初始化持久化工作器
    initialize_persistence_worker(Session, workorder_repo)
    
    # 创建并启动运行时事件管理器
    event_manager = RuntimeEventManager()
    print("启动运行时事件管理器...")
    event_manager.start()
    
    # 等待组件启动
    time.sleep(2)
    
    print("\n步骤1: 创建测试任务记录")
    with Session() as session:
        task = TaskModel(
            id="DEMO_TASK_001",
            task_id="DEMO_TASK_001",
            workorder_id="WO001",
            station_id=1,
            device_id="DEV001",
            sn="SN001",
            task_type="DEMO",
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(task)
        session.commit()
        print(f"创建了任务: {task.task_id}, 初始状态: {task.status}")
    
    print("\n步骤2: 发布任务开始事件")
    task_started_event = TaskStarted(
        event_id="EVT_DEMO_STARTED",
        timestamp=datetime.utcnow(),
        source="Demo",
        payload={"demo": True},
        task_id="DEMO_TASK_001",
        actor_id="DEMO_ACTOR"
    )
    asyncio.run(publish_event(task_started_event))
    
    print("等待事件处理...")
    time.sleep(3)  # 等待事件处理
    
    print("\n步骤3: 检查任务状态变化")
    with Session() as session:
        task = session.query(TaskModel).filter(TaskModel.task_id == "DEMO_TASK_001").first()
        print(f"任务状态更新为: {task.status}, 执行者: {task.actor_id}")
    
    print("\n步骤4: 发布任务完成事件")
    task_completed_event = TaskCompleted(
        event_id="EVT_DEMO_COMPLETED",
        timestamp=datetime.utcnow(),
        source="Demo",
        payload={"demo": True},
        task_id="DEMO_TASK_001",
        result="PASS",
        duration_ms=2500
    )
    asyncio.run(publish_event(task_completed_event))
    
    print("等待事件处理...")
    time.sleep(3)  # 等待事件处理
    
    print("\n步骤5: 检查任务完成状态")
    with Session() as session:
        task = session.query(TaskModel).filter(TaskModel.task_id == "DEMO_TASK_001").first()
        print(f"任务最终状态: {task.status}, 结果: {task.result}, 耗时: {task.duration_ms}ms")
    
    print("\n步骤6: 停止运行时事件管理器")
    event_manager.stop()
    
    print("\n事件驱动架构演示完成!")
    print("架构特点:")
    print("- 事件总线提供解耦的消息传递")
    print("- 持久化工作器异步处理事件并更新数据库")
    print("- 运行时事件管理器统一协调组件生命周期")
    print("- 支持工业系统的实时状态同步")


if __name__ == "__main__":
    demo_event_driven_architecture()
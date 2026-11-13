"""
工业自动化测试平台 - 简化版事件总线测试
用于调试事件总线功能
"""
import asyncio
import tempfile
import os
import unittest
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


class SimpleEventBusTest(unittest.TestCase):
    """简化版事件总线测试"""
    
    def setUp(self):
        # 创建临时数据库
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix='.db')
        self.database_url = f"sqlite:///" + self.temp_db_path
        
        # 使用迁移管理器创建数据库结构
        self.db_manager = DatabaseMigrationManager(self.database_url)
        self.db_manager.alembic_upgrade("head")
        
        # 创建会话
        self.Session = sessionmaker(bind=self.db_manager.engine)
        
        # 创建工单仓库
        self.workorder_repo = WorkOrderRepository(self.Session)
        
        # 初始化持久化工作器
        initialize_persistence_worker(self.Session, self.workorder_repo)
        
        # 创建运行时事件管理器
        self.event_manager = RuntimeEventManager()
    
    def tearDown(self):
        # 停止事件管理器
        self.event_manager.stop()
        
        try:
            os.close(self.temp_db_fd)
        except:
            pass
        try:
            os.unlink(self.temp_db_path)
        except:
            pass
    
    def test_event_bus_direct_publish(self):
        """直接测试事件总线功能"""
        # 启动事件管理器
        self.event_manager.start()
        
        # 等待组件启动
        asyncio.run(asyncio.sleep(2.0))
        
        # 检查事件总线是否真的在运行
        event_bus = get_event_bus()
        print(f"Event bus type: {type(event_bus)}")
        
        # 创建测试任务记录
        with self.Session() as session:
            task = TaskModel(
                id="SIMPLE_TEST_ID",
                task_id="SIMPLE_TEST",
                workorder_id="WO001",
                station_id=1,
                device_id="DEV001",
                sn="SN001",
                task_type="TEST",
                status="pending",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(task)
            session.commit()
        
        # 直接发布事件
        task_started_event = TaskStarted(
            event_id="SIMPLE_EVT_START",
            timestamp=datetime.utcnow(),
            source="SimpleTest",
            payload={},
            task_id="SIMPLE_TEST",
            actor_id="TEST_ACTOR"
        )
        
        # 使用 asyncio.run 发布事件
        asyncio.run(publish_event(task_started_event))
        
        # 检查队列大小
        if hasattr(event_bus, 'get_queue_size'):
            print(f"Queue size after publish: {event_bus.get_queue_size()}")
        
        # 等待事件处理
        asyncio.run(asyncio.sleep(2.0))
        
        # 检查任务状态是否已更新
        with self.Session() as session:
            task = session.query(TaskModel).filter(TaskModel.task_id == "SIMPLE_TEST").first()
            print(f"Task status after event: {task.status}")
            print(f"Task actor_id after event: {task.actor_id}")
        
        # 停止事件管理器
        self.event_manager.stop()


if __name__ == '__main__':
    test = SimpleEventBusTest()
    test.setUp()
    test.test_event_bus_direct_publish()
    test.tearDown()
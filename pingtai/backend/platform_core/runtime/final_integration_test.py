"""
工业自动化测试平台 - 改进的集成测试
使用共享数据库连接进行测试
"""
import asyncio
import tempfile
import os
import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from encoder_test.storage.models import Base, TaskModel, AlarmModel, DeviceModel, WorkOrderModel
from encoder_test.storage.migration_manager import DatabaseMigrationManager
from encoder_test.application.workorder.repository_impl import WorkOrderRepository
from encoder_test.application.workorder.domain import WorkOrder, WorkOrderStatus
from encoder_test.runtime.events import (
    TaskStarted, TaskCompleted, TaskFailed, 
    AlarmTriggered, DeviceConnected, DeviceDisconnected,
    WorkOrderStarted, WorkOrderCompleted
)
from encoder_test.runtime.event_bus import get_event_bus, publish_event, get_event_bus as get_global_event_bus
from encoder_test.runtime.persistence_worker import (
    initialize_persistence_worker, start_persistence_worker, 
    stop_persistence_worker
)
from encoder_test.runtime.event_manager import RuntimeEventManager


class ImprovedIntegrationTest(unittest.TestCase):
    """改进的集成测试"""
    
    def setUp(self):
        # 创建临时数据库文件而不是内存数据库，以便在不同连接间共享
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix='.db')
        self.database_url = f"sqlite:///" + self.temp_db_path
        
        # 使用迁移管理器创建数据库结构
        self.db_manager = DatabaseMigrationManager(self.database_url)
        self.db_manager.alembic_upgrade("head")
        
        # 创建会话 - 使用相同的引擎以确保数据共享
        self.engine = self.db_manager.engine
        self.Session = sessionmaker(bind=self.engine)
        
        # 创建工单仓库
        self.workorder_repo = WorkOrderRepository(self.Session)
        
        # 初始化持久化工作器 - 使用相同的session factory
        initialize_persistence_worker(self.Session, self.workorder_repo)
        
        # 创建运行时事件管理器
        self.event_manager = RuntimeEventManager()
        self.event_manager.start()
        
        # 等待组件启动
        asyncio.run(asyncio.sleep(1.0))
    
    def tearDown(self):
        # 停止事件管理器
        self.event_manager.stop()
        
        # 确保停止持久化工作器
        try:
            asyncio.run(stop_persistence_worker())
        except:
            pass
        
        try:
            os.close(self.temp_db_fd)
        except:
            pass
        try:
            os.unlink(self.temp_db_path)
        except:
            pass
    
    def wait_for_event_processing(self, timeout=5.0):
        """等待事件处理完成"""
        # 检查事件总线队列是否为空
        event_bus = get_global_event_bus()
        
        # 简单等待一段时间，让事件被处理
        import time
        start_time = time.time()
        
        while True:
            if hasattr(event_bus, 'get_queue_size'):
                queue_size = event_bus.get_queue_size()
                if queue_size == 0:
                    break
            
            current_time = time.time()
            if current_time - start_time > timeout:
                break
            
            time.sleep(0.1)
    
    def test_task_events_integration(self):
        """测试任务事件与持久化集成"""
        # 创建测试任务记录
        with self.Session() as session:
            task = TaskModel(
                id="TASK_EVT_TEST_ID",  # 添加主键ID
                task_id="TASK_EVT_TEST",
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
        
        # 发布任务开始事件
        task_started_event = TaskStarted(
            event_id="EVT_TASK_STARTED",
            timestamp=datetime.utcnow(),
            source="Test",
            payload={"test": True},
            task_id="TASK_EVT_TEST",
            actor_id="TEST_ACTOR"
        )
        asyncio.run(publish_event(task_started_event))
        
        # 等待事件处理
        self.wait_for_event_processing()
        asyncio.run(asyncio.sleep(1.0))  # 额外等待确保数据库提交
        
        # 验证任务状态已更新
        with self.Session() as session:
            task = session.query(TaskModel).filter(TaskModel.task_id == "TASK_EVT_TEST").first()
            print(f"Task status after START event: {task.status}, actor_id: {task.actor_id}")
            self.assertEqual(task.status, "running")
            self.assertEqual(task.actor_id, "TEST_ACTOR")
        
        # 发布任务完成事件
        task_completed_event = TaskCompleted(
            event_id="EVT_TASK_COMPLETED",
            timestamp=datetime.utcnow(),
            source="Test",
            payload={"test": True},
            task_id="TASK_EVT_TEST",
            result="PASS",
            duration_ms=1000
        )
        asyncio.run(publish_event(task_completed_event))
        
        # 等待事件处理
        self.wait_for_event_processing()
        asyncio.run(asyncio.sleep(1.0))  # 额外等待确保数据库提交
        
        # 验证任务状态已更新为完成
        with self.Session() as session:
            task = session.query(TaskModel).filter(TaskModel.task_id == "TASK_EVT_TEST").first()
            print(f"Task status after COMPLETED event: {task.status}, result: {task.result}, duration: {task.duration_ms}")
            self.assertEqual(task.status, "completed")
            self.assertEqual(task.result, "PASS")
            self.assertEqual(task.duration_ms, 1000)
    
    def test_alarm_events_integration(self):
        """测试告警事件与持久化集成"""
        # 发布告警触发事件
        alarm_event = AlarmTriggered(
            event_id="EVT_ALARM_TRIGGERED",
            timestamp=datetime.utcnow(),
            source="Test",
            payload={"test": True},
            alarm_id="ALM_EVT_TEST",
            alarm_code="TEST_ERROR",
            alarm_level="ERROR",
            message="Test alarm message"
        )
        asyncio.run(publish_event(alarm_event))
        
        # 等待事件处理
        self.wait_for_event_processing()
        asyncio.run(asyncio.sleep(1.0))  # 额外等待确保数据库提交
        
        # 验证告警已创建
        with self.Session() as session:
            alarm = session.query(AlarmModel).filter(AlarmModel.alarm_id == "ALM_EVT_TEST").first()
            print(f"Alarm found: {alarm is not None}")
            if alarm:
                print(f"Alarm details - code: {alarm.alarm_code}, level: {alarm.alarm_level}, msg: {alarm.message}, status: {alarm.status}")
            self.assertIsNotNone(alarm)
            self.assertEqual(alarm.alarm_code, "TEST_ERROR")
            self.assertEqual(alarm.alarm_level, "ERROR")
            self.assertEqual(alarm.message, "Test alarm message")
            self.assertEqual(alarm.status, "active")
    
    def test_device_events_integration(self):
        """测试设备事件与持久化集成"""
        # 创建测试设备记录
        with self.Session() as session:
            device = DeviceModel(
                id="DEV_EVT_TEST_ID",  # 添加主键ID
                device_id="DEV_EVT_TEST",
                station_id="ST001",
                code="DEV_EVT_TEST",
                name="Test Device",
                device_type="SENSOR",
                connect_status="disconnected",
                status="idle",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(device)
            session.commit()
        
        # 发布设备连接事件
        device_connected_event = DeviceConnected(
            event_id="EVT_DEVICE_CONNECTED",
            timestamp=datetime.utcnow(),
            source="Test",
            payload={"test": True},
            device_id="DEV_EVT_TEST",
            connection_info={"ip": "127.0.0.1", "port": 8080}
        )
        asyncio.run(publish_event(device_connected_event))
        
        # 等待事件处理
        self.wait_for_event_processing()
        asyncio.run(asyncio.sleep(1.0))  # 额外等待确保数据库提交
        
        # 验证设备状态已更新
        with self.Session() as session:
            device = session.query(DeviceModel).filter(DeviceModel.device_id == "DEV_EVT_TEST").first()
            print(f"Device connect_status after CONNECT event: {device.connect_status}, is_connected: {device.is_connected}")
            self.assertEqual(device.connect_status, "connected")
            self.assertTrue(device.is_connected)
        
        # 发布设备断开连接事件
        device_disconnected_event = DeviceDisconnected(
            event_id="EVT_DEVICE_DISCONNECTED",
            timestamp=datetime.utcnow(),
            source="Test",
            payload={"test": True},
            device_id="DEV_EVT_TEST",
            reason="Test disconnect"
        )
        asyncio.run(publish_event(device_disconnected_event))
        
        # 等待事件处理
        self.wait_for_event_processing()
        asyncio.run(asyncio.sleep(1.0))  # 额外等待确保数据库提交
        
        # 验证设备状态已更新为断开
        with self.Session() as session:
            device = session.query(DeviceModel).filter(DeviceModel.device_id == "DEV_EVT_TEST").first()
            print(f"Device connect_status after DISCONNECT event: {device.connect_status}, is_connected: {device.is_connected}")
            self.assertEqual(device.connect_status, "disconnected")
            self.assertFalse(device.is_connected)
    
    def test_workorder_events_integration(self):
        """测试工单事件与持久化集成"""
        # 创建测试工单
        workorder = WorkOrder(
            workorder_id="WO_EVT_TEST",
            product_model="TestProduct",
            planned_quantity=100,
            status=WorkOrderStatus.PENDING
        )
        saved_wo = self.workorder_repo.save(workorder)
        self.assertEqual(saved_wo.status, WorkOrderStatus.PENDING)
        
        # 发布工单开始事件
        wo_started_event = WorkOrderStarted(
            event_id="EVT_WO_STARTED",
            timestamp=datetime.utcnow(),
            source="Test",
            payload={"test": True},
            workorder_id="WO_EVT_TEST"
        )
        asyncio.run(publish_event(wo_started_event))
        
        # 等待事件处理
        self.wait_for_event_processing()
        asyncio.run(asyncio.sleep(1.0))  # 额外等待确保数据库提交
        
        # 验证工单状态已更新
        retrieved_wo = self.workorder_repo.find_by_id("WO_EVT_TEST")
        print(f"WorkOrder status after START event: {retrieved_wo.status}, start_time: {retrieved_wo.start_time}")
        self.assertEqual(retrieved_wo.status, WorkOrderStatus.RUNNING)
        self.assertIsNotNone(retrieved_wo.start_time)
        
        # 发布工单完成事件
        wo_completed_event = WorkOrderCompleted(
            event_id="EVT_WO_COMPLETED",
            timestamp=datetime.utcnow(),
            source="Test",
            payload={"test": True},
            workorder_id="WO_EVT_TEST",
            completed_quantity=50,
            ng_quantity=2
        )
        asyncio.run(publish_event(wo_completed_event))
        
        # 等待事件处理
        self.wait_for_event_processing()
        asyncio.run(asyncio.sleep(1.0))  # 额外等待确保数据库提交
        
        # 验证工单状态已更新为完成
        retrieved_wo = self.workorder_repo.find_by_id("WO_EVT_TEST")
        print(f"WorkOrder status after COMPLETED event: {retrieved_wo.status}, completed_qty: {retrieved_wo.completed_quantity}, ng_qty: {retrieved_wo.ng_quantity}")
        self.assertEqual(retrieved_wo.status, WorkOrderStatus.COMPLETED)
        self.assertEqual(retrieved_wo.completed_quantity, 50)
        self.assertEqual(retrieved_wo.ng_quantity, 2)


def run_improved_tests():
    """运行改进的集成测试"""
    print("开始工业自动化测试平台改进版集成测试...")
    print("="*70)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ImprovedIntegrationTest)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("="*70)
    print(f"测试结果: {'通过' if result.wasSuccessful() else '失败'}")
    print(f"运行测试数: {result.testsRun}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    
    if result.failures:
        print("\n失败详情:")
        for test, trace in result.failures:
            print(f"\n{test}:")
            print(trace)
    
    if result.errors:
        print("\n错误详情:")
        for test, trace in result.errors:
            print(f"\n{test}:")
            print(trace)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_improved_tests()
    exit(0 if success else 1)
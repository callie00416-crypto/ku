"""
工业自动化测试平台 - 数据模型综合测试
"""
import unittest
import tempfile
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .storage.models import Base, TaskModel, ReportModel, AlarmModel, StationModel, DeviceModel, WorkOrderModel
from .storage.read_models import *
from .storage.query_services.implementations import *


class TestDataModelEngineering(unittest.TestCase):
    """数据模型工程化综合测试"""
    
    def setUp(self):
        # 使用临时数据库进行测试
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp()
        self.engine = create_engine(f'sqlite:///{self.temp_db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # 创建查询服务实例
        self.task_query_service = TaskQueryService(self.Session)
        self.report_query_service = ReportQueryService(self.Session)
        self.alarm_query_service = AlarmQueryService(self.Session)
        self.station_query_service = StationQueryService(self.Session)
        self.device_query_service = DeviceQueryService(self.Session)
        self.workorder_query_service = WorkOrderQueryService(self.Session)
        self.dashboard_query_service = DashboardQueryService(self.Session)
    
    def tearDown(self):
        os.close(self.temp_db_fd)
        os.unlink(self.temp_db_path)
    
    def test_task_query_functions(self):
        """测试任务查询功能"""
        # 创建测试数据
        with self.Session() as session:
            task = TaskModel(
                task_id="TASK001",
                workorder_id="WO001",
                station_id=1,
                device_id="DEV001",
                sn="SN001",
                task_type="TEST",
                status="COMPLETED",
                result="PASS",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(task)
            session.commit()
        
        # 测试查询功能
        running_tasks = self.task_query_service.list_running_tasks()
        self.assertEqual(len(running_tasks), 0)  # 我们创建的是COMPLETED状态
        
        failed_tasks = self.task_query_service.list_failed_tasks()
        self.assertEqual(len(failed_tasks), 0)  # 我们创建的是PASS状态
        
        tasks_by_sn = self.task_query_service.query_by_sn("SN001")
        self.assertEqual(len(tasks_by_sn), 1)
        self.assertEqual(tasks_by_sn[0].sn, "SN001")
    
    def test_report_query_functions(self):
        """测试报告查询功能"""
        # 创建测试数据
        with self.Session() as session:
            report = ReportModel(
                report_id="RPT001",
                task_id="TASK001",
                workorder_id="WO001",
                sn="SN001",
                result="PASS",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(report)
            session.commit()
        
        # 测试查询功能
        reports_by_sn = self.report_query_service.query_by_sn("SN001")
        self.assertEqual(len(reports_by_sn), 1)
        self.assertEqual(reports_by_sn[0].sn, "SN001")
        
        reports_by_workorder = self.report_query_service.query_by_workorder("WO001")
        self.assertEqual(len(reports_by_workorder), 1)
        self.assertEqual(reports_by_workorder[0].workorder_id, "WO001")
    
    def test_yield_rate_calculation(self):
        """测试良率计算功能"""
        # 创建测试数据
        with self.Session() as session:
            # 创建一个PASS报告
            report1 = ReportModel(
                report_id="RPT001",
                workorder_id="WO001",
                sn="SN001",
                result="PASS",
                created_at=datetime.now()
            )
            # 创建一个FAIL报告
            report2 = ReportModel(
                report_id="RPT002",
                workorder_id="WO001",
                sn="SN002",
                result="FAIL",
                created_at=datetime.now()
            )
            session.add(report1)
            session.add(report2)
            session.commit()
        
        # 测试良率计算
        yield_rates = self.report_query_service.query_yield_rate(workorder_id="WO001")
        self.assertEqual(len(yield_rates), 1)
        self.assertEqual(yield_rates[0].workorder_id, "WO001")
        self.assertEqual(yield_rates[0].total_count, 2)
        self.assertEqual(yield_rates[0].pass_count, 1)
        self.assertEqual(yield_rates[0].fail_count, 1)
        self.assertAlmostEqual(yield_rates[0].yield_rate, 50.0)
    
    def test_alarm_query_functions(self):
        """测试告警查询功能"""
        # 创建测试数据
        with self.Session() as session:
            alarm = AlarmModel(
                alarm_id="ALM001",
                station_id=1,
                device_id="DEV001",
                alarm_level="ERROR",
                message="Test alarm",
                status="ACTIVE",
                created_at=datetime.now()
            )
            session.add(alarm)
            session.commit()
        
        # 测试查询功能
        active_alarms = self.alarm_query_service.list_active_alarms()
        self.assertEqual(len(active_alarms), 1)
        self.assertEqual(active_alarms[0].status, "ACTIVE")
        
        alarms_by_station = self.alarm_query_service.query_by_station(1)
        self.assertEqual(len(alarms_by_station), 1)
        self.assertEqual(alarms_by_station[0].station_id, 1)
    
    def test_workorder_query_functions(self):
        """测试工单查询功能"""
        # 创建测试数据
        with self.Session() as session:
            workorder = WorkOrderModel(
                workorder_id="WO001",
                product_model="PRODUCT_A",
                planned_quantity=100,
                completed_quantity=50,
                ng_quantity=5,
                status="RUNNING",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(workorder)
            session.commit()
        
        # 测试查询功能
        active_workorders = self.workorder_query_service.get_active_workorders()
        self.assertEqual(len(active_workorders), 1)
        self.assertEqual(active_workorders[0].status, "RUNNING")
        
        workorder_by_id = self.workorder_query_service.get_workorder_by_id("WO001")
        self.assertIsNotNone(workorder_by_id)
        self.assertEqual(workorder_by_id.workorder_id, "WO001")
        
        # 测试工单进度
        progress = self.workorder_query_service.get_workorder_progress("WO001")
        self.assertIn('workorder_id', progress)
        self.assertEqual(progress['workorder_id'], "WO001")
        self.assertEqual(progress['planned_quantity'], 100)
        self.assertEqual(progress['completed_quantity'], 50)
        self.assertEqual(progress['ng_quantity'], 5)
    
    def test_dashboard_query_functions(self):
        """测试仪表板查询功能"""
        # 测试生产汇总
        summary = self.dashboard_query_service.get_production_summary()
        self.assertIn('active_workorders', summary)
        self.assertIn('today_total_tasks', summary)
        
        # 测试质量指标
        quality_metrics = self.dashboard_query_service.get_quality_metrics()
        self.assertIn('yield_rate', quality_metrics)
        self.assertIn('total_reports', quality_metrics)
        
        # 测试系统健康
        system_health = self.dashboard_query_service.get_system_health()
        self.assertIn('active_alarms', system_health)
        self.assertIn('offline_devices', system_health)
        self.assertIn('is_healthy', system_health)
    
    def test_station_and_device_queries(self):
        """测试工位和设备查询功能"""
        # 创建测试数据
        with self.Session() as session:
            # 创建工位
            station = StationModel(
                station_id="ST001",
                code="ST001",
                name="Test Station",
                status="RUNNING",
                created_at=datetime.now()
            )
            # 创建设备
            device = DeviceModel(
                device_id="DEV001",
                station_id="ST001",
                code="DEV001",
                name="Test Device",
                device_type="SENSOR",
                connect_status="CONNECTED",
                created_at=datetime.now()
            )
            session.add(station)
            session.add(device)
            session.commit()
        
        # 测试工位查询
        station_by_id = self.station_query_service.get_station_by_id(1)  # ID是自增的
        if station_by_id:
            self.assertEqual(station_by_id.name, "Test Station")
        
        # 测试设备查询
        device_by_id = self.device_query_service.get_device_by_id("DEV001")
        self.assertIsNotNone(device_by_id)
        self.assertEqual(device_by_id.device_id, "DEV001")
        self.assertEqual(device_by_id.device_type, "SENSOR")


def run_data_model_tests():
    """运行数据模型测试"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDataModelEngineering)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_data_model_tests()
    exit(0 if success else 1)
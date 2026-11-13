"""
报告领域综合单元测试 - Report Domain Comprehensive Unit Tests

【职责】
- 测试报告聚合根所有功能
- 验证快照数据完整性
- 验证不可变性保证
- 验证工业追溯链路
- 测试边界条件和异常情况
"""
import pytest
import time
import json
from datetime import datetime

from encoder_test.domain.report import (
    Report, ReportMetrics,
    DeviceSnapshot, TaskSnapshot, StationSnapshot,
    TestRecord, AlarmSnapshot, SoftwareVersion, OperatorInfo,
    ReportType, ReportFormat, ReportStatus, RecordValueType,
    ReportException, ReportNotFoundException, ReportGenerationException,
    ReportArchiveException, ReportImmutableException, ReportValidationException
)
from encoder_test.domain.common.enums import EventType, TaskResult, TaskStatus
from encoder_test.domain.alarm import Alarm, AlarmLevel, AlarmStatus
from encoder_test.domain.task import Task, TaskMetrics
from encoder_test.domain.station import Station
from encoder_test.domain.device import Device


class TestReportAdvancedCreation:
    """高级报告创建测试"""
    
    def test_report_create_with_complex_metadata(self):
        """测试带复杂元数据的报告创建"""
        complex_metadata = {
            "environment": {
                "temperature": 25.5,
                "humidity": 60.0,
                "pressure": 1013.25
            },
            "operator": {
                "id": "OP-001",
                "name": "张三",
                "department": "测试部",
                "level": "senior"
            },
            "equipment": {
                "calibration_date": "2024-01-01",
                "next_calibration": "2024-07-01",
                "certificate": "CAL-2024-001"
            },
            "process": {
                "batch_id": "BATCH-2024-001",
                "recipe_id": "RECIPE-001",
                "step_count": 10
            }
        }
        
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456",
            metadata=complex_metadata
        )
        
        assert report._metadata == complex_metadata
        assert report.version == 0
        assert report.status == ReportStatus.DRAFT
    
    def test_report_create_with_special_characters(self):
        """测试带特殊字符的报告创建"""
        report = Report.create(
            task_id="TASK-特殊字符测试",
            workorder_id="WO-测试&@#$%",
            sn="SN测试中文123",
            metadata={"特殊字符": "测试&@#$%^*()", "emoji": "✅⚠️❌"}
        )
        
        assert "特殊字符测试" in report.task_id
        assert "WO-测试&@#$%" == report.workorder_id
        assert "SN测试中文123" == report.sn
        assert "测试&@#$%^*()" == report._metadata["特殊字符"]


class TestDeviceSnapshotAdvanced:
    """高级设备快照测试"""
    
    def test_device_snapshot_with_all_fields(self):
        """测试设备快照全字段创建"""
        snapshot = DeviceSnapshot(
            device_id="DEV-001",
            station_id="STATION-001",
            code="ENC-001",
            name="高精度编码器",
            device_type="encoder",
            protocol="modbus_rtu",
            connect_status="connected",
            status="idle",
            is_connected=True,
            is_busy=False,
            is_heartbeat_alive=True,
            config={
                "baudrate": 9600,
                "timeout": 1.0,
                "retries": 3,
                "parity": "none"
            },
            metrics={
                "read_count": 1000,
                "error_count": 5,
                "success_rate": 99.5,
                "avg_response_time": 12.5
            },
            calibration_info={
                "last_calibrated": time.time(),
                "calibration_cycle": 180,  # 180天
                "accuracy": "±0.01°",
                "calibrator": "CAL-001"
            },
            last_heartbeat=time.time(),
            created_at=time.time(),
            metadata={
                "location": "A-001",
                "installation_date": "2023-01-01",
                "warranty_expire": "2026-01-01"
            }
        )
        
        assert snapshot.name == "高精度编码器"
        assert snapshot.config["baudrate"] == 9600
        assert snapshot.metrics["success_rate"] == 99.5
        assert "location" in snapshot.metadata
    
    def test_device_snapshot_edge_cases(self):
        """测试设备快照边界情况"""
        # 测试空值情况
        snapshot = DeviceSnapshot(
            device_id="DEV-001",
            station_id="STATION-001",
            code="ENC-001",
            name="",
            device_type="",
            protocol="",
            connect_status="",
            status="",
            is_connected=False,
            is_busy=False,
            is_heartbeat_alive=False,
            config={},
            metrics={},
            calibration_info={},
            last_heartbeat=None,
            created_at=time.time(),
            metadata={}
        )
        
        assert snapshot.name == ""
        assert snapshot.device_type == ""
        assert snapshot.config == {}
        assert snapshot.metrics == {}


class TestTaskSnapshotAdvanced:
    """高级任务快照测试"""
    
    def test_task_snapshot_with_detailed_info(self):
        """测试详细任务快照"""
        snapshot = TaskSnapshot(
            task_id="TASK-001",
            workorder_id="WO-001",
            station_id=1,
            device_id="DEV-001",
            sn="SN123456",
            task_type="encoder_calibration",
            priority="high",
            status="completed",
            result="pass",
            error_code="",
            error_message="",
            retry_count=0,
            max_retries=3,
            actor_id="ACTOR-001",
            start_time=time.time() - 100,
            end_time=time.time(),
            duration_ms=100000,
            metrics={
                "steps_total": 10,
                "steps_completed": 10,
                "data_points": 1000,
                "processing_time": 50000,
                "verification_time": 50000
            },
            metadata={
                "test_plan": "PLAN-001",
                "procedure": "PROC-001",
                "standard": "ISO-XXXX"
            }
        )
        
        assert snapshot.task_type == "encoder_calibration"
        assert snapshot.metrics["data_points"] == 1000
        assert snapshot.metadata["test_plan"] == "PLAN-001"
        assert snapshot.duration_ms == 100000


class TestStationSnapshotAdvanced:
    """高级工位快照测试"""
    
    def test_station_snapshot_with_resource_details(self):
        """测试带资源详情的工位快照"""
        snapshot = StationSnapshot(
            station_id="STATION-001",
            code="STATION-001",
            name="编码器精密测试工位",
            line_code="LINE-A",
            area_code="AREA-PROD",
            status="idle",
            mode="auto",
            current_task_id="TASK-001",
            is_enabled=True,
            resource_state={
                "cpu_usage": 45.6,
                "memory_usage": 67.8,
                "disk_usage": 23.4,
                "network_latency": 2.3,
                "temperature": 25.5,
                "uptime_hours": 1234.5
            },
            alarm_state={
                "has_alarm": False,
                "active_alarms": 0,
                "last_alarm_time": None,
                "alarm_severity_avg": "low"
            },
            mounted_devices=[
                {"id": "DEV-001", "type": "encoder", "status": "online"},
                {"id": "DEV-002", "type": "power_supply", "status": "online"},
                {"id": "DEV-003", "type": "daq", "status": "offline"}
            ],
            metadata={
                "physical_location": "Building A, Floor 2, Bay 3",
                "environmental_specs": {"temp_range": "-10~50°C", "humidity_max": "85%"},
                "safety_rating": "IP65"
            }
        )
        
        assert snapshot.name == "编码器精密测试工位"
        assert snapshot.resource_state["cpu_usage"] == 45.6
        assert len(snapshot.mounted_devices) == 3
        assert snapshot.alarm_state["active_alarms"] == 0
        assert "physical_location" in snapshot.metadata


class TestTestRecordAdvanced:
    """高级测试记录测试"""
    
    def test_test_record_various_types(self):
        """测试各种类型的测试记录"""
        # 浮点数类型
        float_record = TestRecord(
            record_id="REC-FLOAT",
            step=1,
            name="角度测量",
            value_type="float",
            value_raw="123.456",
            expected="123.450",
            tolerance="0.01",
            is_pass=True
        )
        assert float_record.get_parsed_value() == 123.456
        
        # 整数类型
        int_record = TestRecord(
            record_id="REC-INT",
            step=2,
            name="计数值",
            value_type="int",
            value_raw="100",
            expected="100",
            tolerance="0",
            is_pass=True
        )
        assert int_record.get_parsed_value() == 100
        
        # 布尔类型
        bool_record = TestRecord(
            record_id="REC-BOOL",
            step=3,
            name="连接状态",
            value_type="bool",
            value_raw="true",
            is_pass=True
        )
        assert bool_record.get_parsed_value() is True
        
        # 字符串类型
        str_record = TestRecord(
            record_id="REC-STRING",
            step=4,
            name="序列号",
            value_type="string",
            value_raw="SN123456789",
            is_pass=True
        )
        assert str_record.get_parsed_value() == "SN123456789"
        
        # JSON类型
        json_data = {"key1": "value1", "nested": {"subkey": "subvalue"}}
        json_record = TestRecord(
            record_id="REC-JSON",
            step=5,
            name="配置检查",
            value_type="json",
            value_raw=json.dumps(json_data),
            is_pass=True
        )
        parsed_json = json_record.get_parsed_value()
        assert parsed_json["key1"] == "value1"
        assert parsed_json["nested"]["subkey"] == "subvalue"
        
        # 时间戳类型
        timestamp = time.time()
        time_record = TestRecord(
            record_id="REC-TIMESTAMP",
            step=6,
            name="事件时间",
            value_type="timestamp",
            value_raw=str(timestamp),
            is_pass=True
        )
        # 解析时间戳值，确保它被正确转换回浮点数
        parsed_timestamp = time_record.get_parsed_value()
        assert isinstance(parsed_timestamp, float)
        assert abs(parsed_timestamp - timestamp) < 0.001
    
    def test_test_record_binary_data(self):
        """测试二进制数据类型的测试记录"""
        binary_content = b"This is binary test data\x00\x01\x02"
        binary_record = TestRecord(
            record_id="REC-BINARY",
            step=10,
            name="原始数据",
            value_type="binary",
            value_raw=binary_content.hex(),  # Store as hex string
            is_pass=True
        )
        
        # For binary data, we store as hex string, so the raw value should be hex
        assert isinstance(binary_record.value_raw, str)
        # Verify it can be converted back
        reconstructed = bytes.fromhex(binary_record.value_raw)
        assert reconstructed == binary_content


class TestAlarmSnapshotAdvanced:
    """高级告警快照测试"""
    
    def test_alarm_snapshot_comprehensive(self):
        """测试全面的告警快照"""
        snapshot = AlarmSnapshot(
            alarm_id="ALARM-001",
            alarm_code="TEMP_HIGH",
            alarm_level="error",
            message="温度过高告警",
            status="resolved",
            occurred_at=time.time() - 300,  # 5分钟前
            acknowledged_at=time.time() - 240,  # 4分钟前
            resolved_at=time.time() - 60,  # 1分钟前
            closed_at=time.time(),  # 现在
            task_id="TASK-001",
            station_id="STATION-001",
            device_id="DEV-001",
            workorder_id="WO-001",
            metadata={
                "severity": "high",
                "category": "temperature",
                "response_time": 240,
                "resolution_time": 180,
                "operator": "OP-001"
            }
        )
        
        assert snapshot.alarm_code == "TEMP_HIGH"
        assert snapshot.message == "温度过高告警"
        assert snapshot.status == "resolved"
        assert "response_time" in snapshot.metadata
        assert snapshot.metadata["response_time"] == 240


class TestSoftwareVersionAdvanced:
    """高级软件版本测试"""
    
    def test_software_version_complete_info(self):
        """测试完整的软件版本信息"""
        version = SoftwareVersion(
            encoder_test_version="2.1.0",
            driver_version="3.2.1-build.123",
            firmware_version="1.8.5-rc2",
            os_version="Ubuntu 22.04.3 LTS",
            python_version="3.11.5"
        )
        
        assert version.encoder_test_version == "2.1.0"
        assert "build" in version.driver_version
        assert "rc" in version.firmware_version
        assert "Ubuntu" in version.os_version
        assert version.python_version == "3.11.5"


class TestOperatorInfoAdvanced:
    """高级操作员信息测试"""
    
    def test_operator_info_comprehensive(self):
        """测试全面的操作员信息"""
        operator = OperatorInfo(
            operator_id="OP-001",
            operator_name="张三",
            role="Senior Test Engineer",
            department="Quality Assurance",
            timestamp=time.time()
        )
        
        assert operator.operator_id == "OP-001"
        assert operator.operator_name == "张三"
        assert operator.role == "Senior Test Engineer"
        assert operator.department == "Quality Assurance"


class TestReportGenerationAdvanced:
    """高级报告生成测试"""
    
    def test_report_generation_multiple_records(self):
        """测试带多个测试记录的报告生成"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        # 创建多个不同类型的任务、工位、设备快照
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="comprehensive_test", priority="normal", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-100,
            end_time=time.time(), duration_ms=100000, metrics={"step_count": 5, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="多功能测试工位",
            line_code="LINE-A", area_code="AREA-001", status="idle", mode="auto",
            current_task_id="TASK-001", is_enabled=True, resource_state={"cpu_usage": 50.0},
            alarm_state={"has_alarm": False}, mounted_devices=[]
        )
        
        device_snapshot = DeviceSnapshot(
            device_id="DEV-001", station_id="STATION-001", code="ENC-001", name="编码器",
            device_type="encoder", protocol="modbus_rtu", connect_status="connected",
            status="idle", is_connected=True, is_busy=False, is_heartbeat_alive=True,
            config={"baudrate": 9600}, metrics={"read_count": 100},
            calibration_info={"last_calibrated": time.time()}, last_heartbeat=time.time(),
            created_at=time.time()
        )
        
        # 创建多个测试记录，包括通过和失败的
        test_records = []
        for i in range(10):  # 10个测试记录
            is_pass = i < 8  # 前8个通过，后2个失败
            record = TestRecord(
                record_id=f"REC-{i:03d}",
                step=i+1,
                name=f"测试项{i+1}",
                value_type="float",
                value_raw=str(10.0 + i),
                expected=str(10.0 + i * 0.1) if i < 8 else str(10.0 + i * 2),  # 故意让后2个失败
                tolerance="0.5",
                is_pass=is_pass
            )
            test_records.append(record)
        
        alarm_snapshot = AlarmSnapshot(
            alarm_id="ALARM-001", alarm_code="CONN_WARN", alarm_level="warn",
            message="连接警告", status="resolved", occurred_at=time.time()-100,
            acknowledged_at=time.time()-90, resolved_at=time.time()-80,
            closed_at=time.time()-70, task_id="TASK-001", station_id="STATION-001",
            device_id="DEV-001", workorder_id="WO-001", metadata={}
        )
        
        software_version = SoftwareVersion(
            encoder_test_version="1.0.0", driver_version="2.1.0",
            firmware_version="3.2.1", os_version="Linux 5.4", python_version="3.9.0"
        )
        
        operator_info = OperatorInfo(
            operator_id="OP-001", operator_name="张三", role="工程师", department="测试部"
        )
        
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=test_records,
            alarm_snapshots=[alarm_snapshot],
            software_version=software_version,
            operator_info=operator_info
        )
        
        # 验证结果计算：由于有2个失败记录，结果应该是FAIL
        assert report.result == TaskResult.FAIL
        assert len(report.test_records) == 10
        assert report.metrics.total_records == 10
        assert report.metrics.pass_records == 8  # 8个通过
        assert report.metrics.fail_records == 2  # 2个失败
        assert report.status == ReportStatus.GENERATED
        assert report.version == 1
    
    def test_report_generation_with_all_associations(self):
        """测试带所有关联信息的报告生成"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        # 创建完整的快照数据
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="comprehensive_test", priority="high", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-60,
            end_time=time.time(), duration_ms=60000, metrics={"step_count": 5, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="高精度测试工位",
            line_code="LINE-A", area_code="AREA-HIGH_PRECISION", status="idle", mode="auto",
            current_task_id="TASK-001", is_enabled=True,
            resource_state={"cpu_usage": 30.5, "memory_usage": 45.2},
            alarm_state={"has_alarm": False, "active_alarms": 0},
            mounted_devices=[
                {"id": "DEV-001", "type": "encoder", "status": "online"},
                {"id": "DEV-002", "type": "daq", "status": "online"}
            ],
            metadata={"environment": "clean_room_class_10K"}
        )
        
        device_snapshots = []
        for i in range(3):
            device_snapshot = DeviceSnapshot(
                device_id=f"DEV-{i+1:03d}",
                station_id="STATION-001",
                code=f"DEVICE-{i+1:03d}",
                name=f"设备{i+1}",
                device_type="generic" if i < 2 else "specialized",
                protocol="modbus_rtu",
                connect_status="connected",
                status="idle",
                is_connected=True,
                is_busy=False,
                is_heartbeat_alive=True,
                config={"param1": i, "param2": f"value{i}"},
                metrics={"usage": i * 10, "errors": 0},
                calibration_info={"last_calibrated": time.time()},
                last_heartbeat=time.time(),
                created_at=time.time(),
                metadata={"location": f"BAY-{i+1}"}
            )
            device_snapshots.append(device_snapshot)
        
        test_records = [
            TestRecord(
                record_id=f"REC-{i:03d}",
                step=i+1,
                name=f"全面测试项{i+1}",
                value_type="float" if i % 2 == 0 else "bool",
                value_raw=str(10.0 + i) if i % 2 == 0 else ("true" if i < 4 else "false"),
                is_pass=i < 4  # 前4个通过，后1个失败
            )
            for i in range(5)
        ]
        
        alarm_snapshots = [
            AlarmSnapshot(
                alarm_id=f"ALARM-{i:03d}",
                alarm_code="SYSTEM_EVENT",
                alarm_level="info",
                message=f"系统事件 {i+1}",
                status="closed",
                occurred_at=time.time() - (100 + i*10),
                acknowledged_at=time.time() - (90 + i*10),
                resolved_at=time.time() - (80 + i*10),
                closed_at=time.time() - (70 + i*10),
                task_id="TASK-001",
                station_id="STATION-001",
                device_id=f"DEV-{i+1:03d}",
                workorder_id="WO-001",
                metadata={"event_type": f"type_{i+1}"}
            )
            for i in range(2)
        ]
        
        software_version = SoftwareVersion(
            encoder_test_version="2.0.1", driver_version="3.1.2",
            firmware_version="1.5.0", os_version="RealTime Linux 5.15", python_version="3.11.0"
        )
        
        operator_info = OperatorInfo(
            operator_id="OP-SPECIALIST", operator_name="李专家", role="首席测试工程师", 
            department="研发部"
        )
        
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=device_snapshots,
            test_records=test_records,
            alarm_snapshots=alarm_snapshots,
            software_version=software_version,
            operator_info=operator_info
        )
        
        # 验证所有数据都被正确保存
        assert report.task_id == "TASK-001"
        assert report.workorder_id == "WO-001"
        assert report.sn == "SN123456"
        assert report.task_snapshot is not None
        assert len(report.device_snapshots) == 3
        assert len(report.test_records) == 5
        assert len(report.alarm_snapshots) == 2
        assert report.software_version is not None
        assert report.operator_info is not None
        assert report.result == TaskResult.FAIL  # 因为最后1个测试记录失败
        assert report.metrics.total_records == 5
        assert report.metrics.pass_records == 4
        assert report.metrics.fail_records == 1


class TestReportArchiveAdvanced:
    """高级报告归档测试"""
    
    def test_report_archive_after_generation(self):
        """测试生成后归档"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        # 准备快照数据
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="test", priority="normal", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-10,
            end_time=time.time(), duration_ms=10000, metrics={"step_count": 1, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="测试工位",
            line_code="LINE-A", area_code="AREA-001", status="idle", mode="auto",
            current_task_id="TASK-001", is_enabled=True, resource_state={"cpu_usage": 50.0},
            alarm_state={"has_alarm": False}, mounted_devices=[]
        )
        
        device_snapshot = DeviceSnapshot(
            device_id="DEV-001", station_id="STATION-001", code="ENC-001", name="编码器",
            device_type="encoder", protocol="modbus_rtu", connect_status="connected",
            status="idle", is_connected=True, is_busy=False, is_heartbeat_alive=True,
            config={"baudrate": 9600}, metrics={"read_count": 100},
            calibration_info={"last_calibrated": time.time()}, last_heartbeat=time.time(),
            created_at=time.time()
        )
        
        test_record = TestRecord(
            record_id="REC-001",
            step=1,
            name="基本测试",
            value_type="bool",
            value_raw="true",
            is_pass=True
        )
        
        # 生成报告
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=[test_record]
        )
        
        # 验证生成后的状态
        assert report.status == ReportStatus.GENERATED
        assert report.generated_at is not None
        version_after_generate = report.version
        
        # 归档报告
        archived_time_before = time.time()
        report.archive()
        archived_time_after = time.time()
        
        # 验证归档后的状态
        assert report.status == ReportStatus.ARCHIVED
        assert report.archived_at is not None
        assert archived_time_before <= report.archived_at <= archived_time_after
        assert report.version == version_after_generate + 1  # 版本应增加1
    
    def test_report_archive_twice_should_fail(self):
        """测试重复归档应该失败"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        # 准备并生成报告
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="test", priority="normal", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-10,
            end_time=time.time(), duration_ms=10000, metrics={"step_count": 1, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="测试工位",
            line_code="LINE-A", area_code="AREA-001", status="idle", mode="auto",
            current_task_id="TASK-001", is_enabled=True, resource_state={"cpu_usage": 50.0},
            alarm_state={"has_alarm": False}, mounted_devices=[]
        )
        
        device_snapshot = DeviceSnapshot(
            device_id="DEV-001", station_id="STATION-001", code="ENC-001", name="编码器",
            device_type="encoder", protocol="modbus_rtu", connect_status="connected",
            status="idle", is_connected=True, is_busy=False, is_heartbeat_alive=True,
            config={"baudrate": 9600}, metrics={"read_count": 100},
            calibration_info={"last_calibrated": time.time()}, last_heartbeat=time.time(),
            created_at=time.time()
        )
        
        test_record = TestRecord(
            record_id="REC-001",
            step=1,
            name="基本测试",
            value_type="bool",
            value_raw="true",
            is_pass=True
        )
        
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=[test_record]
        )
        report.archive()
        
        # 尝试再次归档（应该失败）
        with pytest.raises(ReportArchiveException):
            report.archive()


class TestReportAttachmentsAdvanced:
    """高级报告附件测试"""
    
    def test_report_attachments_functionality(self):
        """测试报告附件功能"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        # 准备并生成报告
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="test", priority="normal", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-10,
            end_time=time.time(), duration_ms=10000, metrics={"step_count": 1, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="测试工位",
            line_code="LINE-A", area_code="AREA-001", status="idle", mode="auto",
            current_task_id="TASK-001", is_enabled=True, resource_state={"cpu_usage": 50.0},
            alarm_state={"has_alarm": False}, mounted_devices=[]
        )
        
        device_snapshot = DeviceSnapshot(
            device_id="DEV-001", station_id="STATION-001", code="ENC-001", name="编码器",
            device_type="encoder", protocol="modbus_rtu", connect_status="connected",
            status="idle", is_connected=True, is_busy=False, is_heartbeat_alive=True,
            config={"baudrate": 9600}, metrics={"read_count": 100},
            calibration_info={"last_calibrated": time.time()}, last_heartbeat=time.time(),
            created_at=time.time()
        )
        
        test_record = TestRecord(
            record_id="REC-001",
            step=1,
            name="基本测试",
            value_type="bool",
            value_raw="true",
            is_pass=True
        )
        
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=[test_record]
        )
        report.archive()
        
        # 添加第一个附件
        image_content = b"fake png image data\x89PNG\r\n\x1a\n..."
        report.add_attachment(
            attachment_type="image/png",
            content=image_content,
            description="测试图像1"
        )
        
        # 验证第一个附件
        attachments = report._metadata.get('attachments', [])
        assert len(attachments) == 1
        assert attachments[0]['type'] == "image/png"
        assert attachments[0]['description'] == "测试图像1"
        assert attachments[0]['size'] == len(image_content)
        assert 'checksum' in attachments[0]
        assert 'timestamp' in attachments[0]
        
        # 添加第二个附件
        pdf_content = b"%PDF-1.4..."  # 简化的PDF头部
        report.add_attachment(
            attachment_type="application/pdf",
            content=pdf_content,
            description="测试报告PDF"
        )
        
        # 验证两个附件
        attachments = report._metadata.get('attachments', [])
        assert len(attachments) == 2
        assert attachments[1]['type'] == "application/pdf"
        assert attachments[1]['description'] == "测试报告PDF"
        assert attachments[1]['size'] == len(pdf_content)
        
        # 验证版本增加了
        assert report.version == 4  # 生成(0->1) + 归档(1->2) + 附件1(2->3) + 附件2(3->4) = 4
    
    def test_report_attachment_checksum_verification(self):
        """测试报告附件校验和验证"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        # 准备并生成报告
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="test", priority="normal", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-10,
            end_time=time.time(), duration_ms=10000, metrics={"step_count": 1, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="测试工位",
            line_code="LINE-A", area_code="AREA-001", status="idle", mode="auto",
            current_task_id="TASK-001", is_enabled=True, resource_state={"cpu_usage": 50.0},
            alarm_state={"has_alarm": False}, mounted_devices=[]
        )
        
        device_snapshot = DeviceSnapshot(
            device_id="DEV-001", station_id="STATION-001", code="ENC-001", name="编码器",
            device_type="encoder", protocol="modbus_rtu", connect_status="connected",
            status="idle", is_connected=True, is_busy=False, is_heartbeat_alive=True,
            config={"baudrate": 9600}, metrics={"read_count": 100},
            calibration_info={"last_calibrated": time.time()}, last_heartbeat=time.time(),
            created_at=time.time()
        )
        
        test_record = TestRecord(
            record_id="REC-001",
            step=1,
            name="基本测试",
            value_type="bool",
            value_raw="true",
            is_pass=True
        )
        
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=[test_record]
        )
        report.archive()
        
        # 添加附件
        content = b"important data that must not be corrupted"
        report.add_attachment(
            attachment_type="application/octet-stream",
            content=content
        )
        
        # 验证校验和
        attachments = report._metadata.get('attachments', [])
        assert len(attachments) == 1
        attachment = attachments[0]
        
        import hashlib
        expected_checksum = hashlib.md5(content).hexdigest()
        assert attachment['checksum'] == expected_checksum


class TestReportMetricsAdvanced:
    """高级报告指标测试"""
    
    def test_report_metrics_calculation_comprehensive(self):
        """测试全面的报告指标计算"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        # 准备快照数据
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="comprehensive_test", priority="high", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-120,
            end_time=time.time(), duration_ms=120000, metrics={"step_count": 10, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="综合测试工位",
            line_code="LINE-A", area_code="AREA-COMPREHENSIVE", status="idle", mode="auto",
            current_task_id="TASK-001", is_enabled=True, 
            resource_state={"cpu_usage": 65.5, "memory_usage": 72.3},
            alarm_state={"has_alarm": False, "active_alarms": 0},
            mounted_devices=[{"id": "DEV-001", "type": "encoder", "status": "online"}],
            metadata={}
        )
        
        device_snapshot = DeviceSnapshot(
            device_id="DEV-001", station_id="STATION-001", code="ENC-001", name="编码器",
            device_type="encoder", protocol="modbus_rtu", connect_status="connected",
            status="idle", is_connected=True, is_busy=False, is_heartbeat_alive=True,
            config={"baudrate": 9600}, metrics={"read_count": 5000, "error_count": 2},
            calibration_info={"last_calibrated": time.time()}, last_heartbeat=time.time(),
            created_at=time.time()
        )
        
        # 创建多个测试记录，模拟实际测试场景
        test_records = []
        for i in range(20):
            # 模拟一些测试通过，一些失败的情况
            is_pass = i < 17  # 前17个通过，后3个失败
            record = TestRecord(
                record_id=f"REC-{i+1:03d}",
                step=i+1,
                name=f"测试项{i+1}",
                value_type="float" if i % 3 == 0 else ("bool" if i % 3 == 1 else "string"),
                value_raw=str(10.0 + i) if i % 3 == 0 else ("true" if is_pass else "false"),
                expected=str(10.0 + i * 0.1) if i % 3 == 0 else None,
                tolerance="0.5" if i % 3 == 0 else None,
                is_pass=is_pass
            )
            test_records.append(record)
        
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=test_records
        )
        
        # 验证指标计算
        metrics = report.metrics
        assert metrics.total_records == 20
        assert metrics.pass_records == 17  # 17个通过
        assert metrics.fail_records == 3   # 3个失败
        assert metrics.duration_ms == 120000  # 从任务快照获取的持续时间
        
        # 验证结果计算
        assert report.result == TaskResult.FAIL  # 因为有失败的测试记录


class TestReportSerializationAdvanced:
    """高级报告序列化测试"""
    
    def test_report_to_dict_comprehensive(self):
        """测试全面的报告序列化"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456",
            metadata={"project": "Project Alpha", "phase": "Verification"}
        )
        
        # 准备完整的快照数据
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="final_test", priority="critical", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-EXPERT", start_time=time.time()-180,
            end_time=time.time(), duration_ms=180000, 
            metrics={"steps_total": 25, "steps_completed": 25, "verification_points": 100},
            metadata={"test_procedure": "TP-001", "quality_level": "A+"}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-HIGH_ACCURACY", name="高精度测试站",
            line_code="LINE-QUALITY", area_code="AREA-VERIFICATION", status="idle", mode="auto",
            current_task_id="TASK-001", is_enabled=True,
            resource_state={"cpu_usage": 25.3, "memory_usage": 38.7, "disk_usage": 15.2},
            alarm_state={"has_alarm": False, "active_alarms": 0, "last_alarm_clear": time.time()},
            mounted_devices=[
                {"id": "DEV-001", "type": "encoder", "status": "calibrated", "accuracy": "±0.001°"},
                {"id": "DEV-002", "type": "daq", "status": "online", "channels": 8}
            ],
            metadata={"environment": "controlled_temp_humidity", "certification": "ISO_17025"}
        )
        
        device_snapshots = [
            DeviceSnapshot(
                device_id="DEV-001", station_id="STATION-001", code="ENC-HIGH_PRECISION", 
                name="高精度编码器", device_type="encoder", protocol="ethercat", 
                connect_status="connected", status="calibrated", is_connected=True, 
                is_busy=False, is_heartbeat_alive=True,
                config={"resolution": 24, "bandwidth": "1MHz", "filter": "low_pass"},
                metrics={"position_accuracy": 0.001, "speed_accuracy": 0.01},
                calibration_info={"last_calibrated": time.time() - 86400*30, "due_in_days": 150},
                last_heartbeat=time.time(), created_at=time.time() - 86400*365,
                metadata={"manufacturer": "Precision Instruments Inc.", "model": "PI-2400"}
            ),
            DeviceSnapshot(
                device_id="DEV-002", station_id="STATION-001", code="DAQ-HIGH_SPEED",
                name="高速数据采集仪", device_type="daq", protocol="usb", 
                connect_status="connected", status="ready", is_connected=True,
                is_busy=False, is_heartbeat_alive=True,
                config={"sample_rate": "1MS/s", "channels": 8, "range": "±10V"},
                metrics={"samples_collected": 1000000, "error_rate": 0.001},
                calibration_info={"last_calibrated": time.time() - 86400*45, "due_in_days": 135},
                last_heartbeat=time.time(), created_at=time.time() - 86400*180,
                metadata={"manufacturer": "DAQ Systems Ltd.", "model": "DS-8CH-1M"}
            )
        ]
        
        test_records = [
            TestRecord(
                record_id="REC-PRECISION_ANGLE",
                step=1,
                name="精密角度测量",
                value_type="float",
                value_raw="45.12345",
                expected="45.12340",
                tolerance="0.00010",
                is_pass=True,
                metadata={"method": "optical_interpolation", "confidence": 0.999}
            ),
            TestRecord(
                record_id="REC-REPEATABILITY",
                step=2,
                name="重复性测试",
                value_type="float",
                value_raw="0.00095",
                expected="0.00100",
                tolerance="0.00050",
                is_pass=True,
                metadata={"cycles": 100, "std_dev": 0.00015}
            ),
            TestRecord(
                record_id="REC-CONNECTION_STABILITY",
                step=3,
                name="连接稳定性",
                value_type="bool",
                value_raw="true",
                is_pass=True,
                metadata={"test_duration": 3600, "dropouts": 0}
            )
        ]
        
        alarm_snapshots = [
            AlarmSnapshot(
                alarm_id="ALARM-WARMUP", 
                alarm_code="WARMUP_COMPLETE", 
                alarm_level="info",
                message="设备预热完成", 
                status="closed",
                occurred_at=time.time() - 300,  # 5分钟前
                acknowledged_at=time.time() - 290,
                resolved_at=time.time() - 280,
                closed_at=time.time() - 270,
                task_id="TASK-001",
                station_id="STATION-001",
                device_id="DEV-001",
                workorder_id="WO-001",
                metadata={"warmup_time": 300, "temperature_stable": True}
            )
        ]
        
        software_version = SoftwareVersion(
            encoder_test_version="3.0.0-release", 
            driver_version="4.2.1-stable",
            firmware_version="2.1.0-production", 
            os_version="RealTime Linux 6.1.0",
            python_version="3.11.6"
        )
        
        operator_info = OperatorInfo(
            operator_id="OP-SR-001",
            operator_name="王高级工程师", 
            role="Senior Quality Engineer",
            department="Quality Assurance Department"
        )
        
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=device_snapshots,
            test_records=test_records,
            alarm_snapshots=alarm_snapshots,
            software_version=software_version,
            operator_info=operator_info
        )
        report.archive()
        
        # 序列化报告
        report_dict = report.to_dict()
        
        # 验证关键字段存在且正确
        assert report_dict['id'].startswith('REPORT-')
        assert report_dict['task_id'] == 'TASK-001'
        assert report_dict['workorder_id'] == 'WO-001'
        assert report_dict['sn'] == 'SN123456'
        assert report_dict['status'] == 'archived'
        assert report_dict['result'] == 'pass'
        assert report_dict['generated_at'] is not None
        assert report_dict['archived_at'] is not None
        assert report_dict['version'] >= 2  # 生成+归档
        assert 'project' in report_dict['metadata']
        
        # 验证快照数据
        assert report_dict['task_snapshot']['task_type'] == 'final_test'
        assert report_dict['station_snapshot']['name'] == '高精度测试站'
        assert len(report_dict['device_snapshots']) == 2
        assert len(report_dict['test_records']) == 3
        assert len(report_dict['alarm_snapshots']) == 1
        assert report_dict['software_version']['encoder_test_version'] == '3.0.0-release'
        assert report_dict['operator_info']['operator_name'] == '王高级工程师'
        
        # 验证指标
        assert report_dict['metrics']['total_records'] == 3
        assert report_dict['metrics']['pass_records'] == 3
        assert report_dict['metrics']['fail_records'] == 0
        assert report_dict['metrics']['duration_ms'] == 180000
    
    def test_report_repr_meaningful_output(self):
        """测试报告的有意义的字符串表示"""
        report = Report.create(
            task_id="TASK-HIGH_QUALITY",
            workorder_id="WO-CRITICAL",
            sn="SN-PRODUCT-HIGH-GRADE"
        )
        
        repr_str = repr(report)
        assert "Report" in repr_str
        assert "PRODUCT-HIGH-GRADE" in repr_str  # sn is in repr
        assert "draft" in repr_str.lower()
        
        # 生成报告后再查看
        task_snapshot = TaskSnapshot(
            task_id="TASK-HIGH_QUALITY", workorder_id="WO-CRITICAL", station_id=1, device_id="DEV-001",
            sn="SN-PRODUCT-HIGH-GRADE", task_type="quality_test", priority="critical", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-10,
            end_time=time.time(), duration_ms=10000, metrics={"step_count": 1, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="质量测试工位",
            line_code="LINE-Q", area_code="AREA-QUALITY", status="idle", mode="auto",
            current_task_id="TASK-HIGH_QUALITY", is_enabled=True, resource_state={"cpu_usage": 50.0},
            alarm_state={"has_alarm": False}, mounted_devices=[]
        )
        
        device_snapshot = DeviceSnapshot(
            device_id="DEV-001", station_id="STATION-001", code="ENC-001", name="编码器",
            device_type="encoder", protocol="modbus_rtu", connect_status="connected",
            status="idle", is_connected=True, is_busy=False, is_heartbeat_alive=True,
            config={"baudrate": 9600}, metrics={"read_count": 100},
            calibration_info={"last_calibrated": time.time()}, last_heartbeat=time.time(),
            created_at=time.time()
        )
        
        test_record = TestRecord(
            record_id="REC-001",
            step=1,
            name="质量检查",
            value_type="bool",
            value_raw="true",
            is_pass=True
        )
        
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=[test_record]
        )
        
        repr_str_generated = repr(report)
        assert "generated" in repr_str_generated.lower()
        assert "pass" in repr_str_generated.lower()


class TestReportExceptionsAdvanced:
    """高级报告异常测试"""
    
    def test_report_generation_exception_scenarios(self):
        """测试报告生成的各种异常场景"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        # 测试在非DRAFT状态下尝试生成（虽然正常情况下状态就是DRAFT，但我们可以通过直接修改来测试）
        # 实际测试中，我们会测试试图多次生成的情况
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="test", priority="normal", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-10,
            end_time=time.time(), duration_ms=10000, metrics={"step_count": 1, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="测试工位",
            line_code="LINE-A", area_code="AREA-001", status="idle", mode="auto",
            current_task_id="TASK-001", is_enabled=True, resource_state={"cpu_usage": 50.0},
            alarm_state={"has_alarm": False}, mounted_devices=[]
        )
        
        device_snapshot = DeviceSnapshot(
            device_id="DEV-001", station_id="STATION-001", code="ENC-001", name="编码器",
            device_type="encoder", protocol="modbus_rtu", connect_status="connected",
            status="idle", is_connected=True, is_busy=False, is_heartbeat_alive=True,
            config={"baudrate": 9600}, metrics={"read_count": 100},
            calibration_info={"last_calibrated": time.time()}, last_heartbeat=time.time(),
            created_at=time.time()
        )
        
        test_record = TestRecord(
            record_id="REC-001",
            step=1,
            name="基本测试",
            value_type="bool",
            value_raw="true",
            is_pass=True
        )
        
        # 正常生成一次
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=[test_record]
        )
        
        # 尝试再次生成（应该失败，因为状态已经不是DRAFT）
        with pytest.raises(Exception):  # Should raise some kind of exception
            report.generate(
                task_snapshot=task_snapshot,
                station_snapshot=station_snapshot,
                device_snapshots=[device_snapshot],
                test_records=[test_record]
            )
    
    def test_report_archive_exception_scenarios(self):
        """测试报告归档的异常场景"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        # 尝试在DRAFT状态下直接归档（应该失败）
        with pytest.raises(ReportArchiveException):
            report.archive()
        
        # 准备快照但不生成报告
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="test", priority="normal", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-10,
            end_time=time.time(), duration_ms=10000, metrics={"step_count": 1, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="测试工位",
            line_code="LINE-A", area_code="AREA-001", status="idle", mode="auto",
            current_task_id="TASK-001", is_enabled=True, resource_state={"cpu_usage": 50.0},
            alarm_state={"has_alarm": False}, mounted_devices=[]
        )
        
        device_snapshot = DeviceSnapshot(
            device_id="DEV-001", station_id="STATION-001", code="ENC-001", name="编码器",
            device_type="encoder", protocol="modbus_rtu", connect_status="connected",
            status="idle", is_connected=True, is_busy=False, is_heartbeat_alive=True,
            config={"baudrate": 9600}, metrics={"read_count": 100},
            calibration_info={"last_calibrated": time.time()}, last_heartbeat=time.time(),
            created_at=time.time()
        )
        
        test_record = TestRecord(
            record_id="REC-001",
            step=1,
            name="基本测试",
            value_type="bool",
            value_raw="true",
            is_pass=True
        )
        
        # 生成报告
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=[test_record]
        )
        
        # 正常归档
        report.archive()
        
        # 尝试再次归档（应该失败）
        with pytest.raises(ReportArchiveException):
            report.archive()


class TestReportEnumsAdvanced:
    """高级报告枚举测试"""
    
    def test_all_enum_values_exist_and_correct(self):
        """测试所有枚举值存在且正确"""
        # ReportType枚举
        assert ReportType.TEST_RESULT.value == "test_result"
        assert ReportType.CALIBRATION.value == "calibration"
        assert ReportType.QUALIFICATION.value == "qualification"
        assert ReportType.COMPLIANCE.value == "compliance"
        assert ReportType.DEBUG.value == "debug"
        assert len(list(ReportType)) == 5
        
        # ReportFormat枚举
        assert ReportFormat.PDF.value == "pdf"
        assert ReportFormat.EXCEL.value == "excel"
        assert ReportFormat.JSON.value == "json"
        assert ReportFormat.XML.value == "xml"
        assert ReportFormat.CSV.value == "csv"
        assert len(list(ReportFormat)) == 5
        
        # ReportStatus枚举
        assert ReportStatus.DRAFT.value == "draft"
        assert ReportStatus.GENERATED.value == "generated"
        assert ReportStatus.ARCHIVED.value == "archived"
        assert len(list(ReportStatus)) == 3
        
        # RecordValueType枚举
        assert RecordValueType.FLOAT.value == "float"
        assert RecordValueType.INT.value == "int"
        assert RecordValueType.BOOL.value == "bool"
        assert RecordValueType.STRING.value == "string"
        assert RecordValueType.JSON.value == "json"
        assert RecordValueType.WAVEFORM.value == "waveform"
        assert RecordValueType.BINARY.value == "binary"
        assert RecordValueType.TIMESTAMP.value == "timestamp"
        assert RecordValueType.IMAGE.value == "image"
        assert len(list(RecordValueType)) == 9


class TestReportEventGeneration:
    """测试报告事件生成"""
    
    def test_report_generates_correct_events(self):
        """测试报告生成正确的领域事件"""
        report = Report.create(
            task_id="TASK-EVENT_TEST",
            workorder_id="WO-EVENT_TEST",
            sn="SN-EVENT-001"
        )
        
        # 验证创建事件（通过内部机制）
        assert len(report._domain_events) == 0  # 创建时不添加事件，生成时才添加
        
        # 准备快照数据
        task_snapshot = TaskSnapshot(
            task_id="TASK-EVENT_TEST", workorder_id="WO-EVENT_TEST", station_id=1, device_id="DEV-001",
            sn="SN-EVENT-001", task_type="event_test", priority="normal", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-10,
            end_time=time.time(), duration_ms=10000, metrics={"step_count": 1, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="事件测试工位",
            line_code="LINE-A", area_code="AREA-001", status="idle", mode="auto",
            current_task_id="TASK-EVENT_TEST", is_enabled=True, resource_state={"cpu_usage": 50.0},
            alarm_state={"has_alarm": False}, mounted_devices=[]
        )
        
        device_snapshot = DeviceSnapshot(
            device_id="DEV-001", station_id="STATION-001", code="ENC-001", name="编码器",
            device_type="encoder", protocol="modbus_rtu", connect_status="connected",
            status="idle", is_connected=True, is_busy=False, is_heartbeat_alive=True,
            config={"baudrate": 9600}, metrics={"read_count": 100},
            calibration_info={"last_calibrated": time.time()}, last_heartbeat=time.time(),
            created_at=time.time()
        )
        
        test_record = TestRecord(
            record_id="REC-001",
            step=1,
            name="事件测试",
            value_type="bool",
            value_raw="true",
            is_pass=True
        )
        
        # 清空之前的事件（如果有）
        report._domain_events.clear()
        
        # 生成报告，这应该产生一个事件
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=[test_record]
        )
        
        # 验证生成了REPORT_GENERATED事件
        generated_events = [event for event in report._domain_events 
                           if event['event_type'] == EventType.REPORT_GENERATED]
        assert len(generated_events) == 1
        event_data = generated_events[0]['data']
        assert event_data['task_id'] == 'TASK-EVENT_TEST'
        assert event_data['result'] == 'pass'
        assert 'generated_at' in event_data
        
        # 清空事件列表准备下一个测试
        prev_events_count = len(report._domain_events)
        
        # 归档报告，这应该产生另一个事件
        report.archive()
        
        # 验证归档产生了REPORT_ARCHIVED事件
        archived_events = [event for event in report._domain_events 
                          if event['event_type'] == EventType.REPORT_ARCHIVED]
        assert len(archived_events) == 1
        archived_event_data = archived_events[0]['data']
        assert 'archived_at' in archived_event_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
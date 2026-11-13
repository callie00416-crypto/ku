"""
报告领域单元测试 - Report Domain Unit Tests

【职责】
- 测试报告聚合根行为
- 测试快照数据固化
- 测试不可变性保证
- 测试工业追溯链路
"""
import pytest
import time
import json

from platform.domain.report import (
    Report, ReportMetrics,
    DeviceSnapshot, TaskSnapshot, StationSnapshot,
    TestRecord, AlarmSnapshot, SoftwareVersion, OperatorInfo,
    ReportType, ReportFormat, ReportStatus, RecordValueType,
    ReportException, ReportNotFoundException, ReportGenerationException,
    ReportArchiveException, ReportImmutableException
)
from platform.domain.common.enums import EventType, TaskResult


class TestReportCreation:
    """报告创建测试"""
    
    def test_report_create_basic(self):
        """测试基本报告创建"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        assert report.id.startswith("REPORT-")
        assert report.task_id == "TASK-001"
        assert report.workorder_id == "WO-001"
        assert report.sn == "SN123456"
        assert report.status == ReportStatus.DRAFT
        assert report.result is None
        assert report.version == 0
    
    def test_report_create_with_metadata(self):
        """测试带元数据的报告创建"""
        metadata = {"test_env": "production", "operator": "OP-001"}
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456",
            metadata=metadata
        )
        
        assert report._metadata == metadata


class TestDeviceSnapshot:
    """设备快照测试"""
    
    def test_device_snapshot_creation(self):
        """测试设备快照创建"""
        snapshot = DeviceSnapshot(
            device_id="DEV-001",
            station_id="STATION-001",
            code="ENC-001",
            name="编码器",
            device_type="encoder",
            protocol="modbus_rtu",
            connect_status="connected",
            status="idle",
            is_connected=True,
            is_busy=False,
            is_heartbeat_alive=True,
            config={"baudrate": 9600, "timeout": 1.0},
            metrics={"read_count": 100, "error_count": 0},
            calibration_info={"last_calibrated": time.time()},
            last_heartbeat=time.time(),
            created_at=time.time()
        )
        
        assert snapshot.device_id == "DEV-001"
        assert snapshot.name == "编码器"
        assert snapshot.is_connected is True
        assert snapshot.config["baudrate"] == 9600


class TestTaskSnapshot:
    """任务快照测试"""
    
    def test_task_snapshot_creation(self):
        """测试任务快照创建"""
        snapshot = TaskSnapshot(
            task_id="TASK-001",
            workorder_id="WO-001",
            station_id=1,
            device_id="DEV-001",
            sn="SN123456",
            task_type="encoder_test",
            priority="normal",
            status="completed",
            result="pass",
            error_code=None,
            error_message=None,
            retry_count=0,
            max_retries=3,
            actor_id="ACTOR-001",
            start_time=time.time() - 10,
            end_time=time.time(),
            duration_ms=10000,
            metrics={"step_count": 5, "retry_count": 0}
        )
        
        assert snapshot.task_id == "TASK-001"
        assert snapshot.sn == "SN123456"
        assert snapshot.result == "pass"


class TestStationSnapshot:
    """工位快照测试"""
    
    def test_station_snapshot_creation(self):
        """测试工位快照创建"""
        snapshot = StationSnapshot(
            station_id="STATION-001",
            code="STATION-001",
            name="编码器测试工位",
            line_code="LINE-A",
            area_code="AREA-001",
            status="idle",
            mode="auto",
            current_task_id="TASK-001",
            is_enabled=True,
            resource_state={
                "cpu_usage": 50.0,
                "memory_usage": 60.0,
                "disk_usage": 70.0
            },
            alarm_state={
                "has_alarm": False,
                "alarm_level": "",
                "alarm_message": ""
            },
            mounted_devices=[]
        )
        
        assert snapshot.station_id == "STATION-001"
        assert snapshot.name == "编码器测试工位"
        assert snapshot.is_enabled is True


class TestTestRecord:
    """测试记录测试"""
    
    def test_test_record_creation_float(self):
        """测试浮点数类型测试记录创建"""
        record = TestRecord(
            record_id="REC-001",
            step=1,
            name="角度精度测试",
            value_type="float",
            value_raw="12.56",
            expected="12.50",
            tolerance="0.1",
            is_pass=True
        )
        
        assert record.name == "角度精度测试"
        assert record.value_type == "float"
        assert record.value_raw == "12.56"
        assert record.get_parsed_value() == 12.56
    
    def test_test_record_creation_bool(self):
        """测试布尔类型测试记录创建"""
        record = TestRecord(
            record_id="REC-002",
            step=2,
            name="连接状态检查",
            value_type="bool",
            value_raw="true",
            is_pass=True
        )
        
        assert record.value_type == "bool"
        assert record.get_parsed_value() is True
    
    def test_test_record_creation_json(self):
        """测试JSON类型测试记录创建"""
        json_data = {"key": "value", "number": 123}
        record = TestRecord(
            record_id="REC-003",
            step=3,
            name="配置检查",
            value_type="json",
            value_raw=json.dumps(json_data),
            is_pass=True
        )
        
        assert record.value_type == "json"
        parsed = record.get_parsed_value()
        assert parsed["key"] == "value"
        assert parsed["number"] == 123


class TestAlarmSnapshot:
    """告警快照测试"""
    
    def test_alarm_snapshot_creation(self):
        """测试告警快照创建"""
        snapshot = AlarmSnapshot(
            alarm_id="ALARM-001",
            alarm_code="CONN_ERR",
            alarm_level="error",
            message="连接失败",
            status="resolved",
            occurred_at=time.time() - 100,
            acknowledged_at=time.time() - 50,
            resolved_at=time.time() - 10,
            closed_at=time.time(),
            task_id="TASK-001",
            station_id="STATION-001",
            device_id="DEV-001",
            workorder_id="WO-001",
            metadata={"retry_count": 3}
        )
        
        assert snapshot.alarm_id == "ALARM-001"
        assert snapshot.alarm_code == "CONN_ERR"
        assert snapshot.status == "resolved"


class TestSoftwareVersion:
    """软件版本测试"""
    
    def test_software_version_creation(self):
        """测试软件版本创建"""
        version = SoftwareVersion(
            encoder_test_version="1.0.0",
            driver_version="2.1.0",
            firmware_version="3.2.1",
            os_version="Linux 5.4",
            python_version="3.9.0"
        )
        
        assert version.encoder_test_version == "1.0.0"
        assert version.driver_version == "2.1.0"


class TestOperatorInfo:
    """操作员信息测试"""
    
    def test_operator_info_creation(self):
        """测试操作员信息创建"""
        operator = OperatorInfo(
            operator_id="OP-001",
            operator_name="张三",
            role="工程师",
            department="测试部"
        )
        
        assert operator.operator_id == "OP-001"
        assert operator.operator_name == "张三"
        assert operator.role == "工程师"


class TestReportGeneration:
    """报告生成测试"""
    
    def test_report_generation_success(self):
        """测试报告成功生成"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        # 创建快照数据
        task_snapshot = TaskSnapshot(
            task_id="TASK-001",
            workorder_id="WO-001",
            station_id=1,
            device_id="DEV-001",
            sn="SN123456",
            task_type="encoder_test",
            priority="normal",
            status="completed",
            result="pass",
            error_code=None,
            error_message=None,
            retry_count=0,
            max_retries=3,
            actor_id="ACTOR-001",
            start_time=time.time() - 10,
            end_time=time.time(),
            duration_ms=10000,
            metrics={"step_count": 5, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001",
            code="STATION-001",
            name="编码器测试工位",
            line_code="LINE-A",
            area_code="AREA-001",
            status="idle",
            mode="auto",
            current_task_id="TASK-001",
            is_enabled=True,
            resource_state={"cpu_usage": 50.0},
            alarm_state={"has_alarm": False},
            mounted_devices=[]
        )
        
        device_snapshot = DeviceSnapshot(
            device_id="DEV-001",
            station_id="STATION-001",
            code="ENC-001",
            name="编码器",
            device_type="encoder",
            protocol="modbus_rtu",
            connect_status="connected",
            status="idle",
            is_connected=True,
            is_busy=False,
            is_heartbeat_alive=True,
            config={"baudrate": 9600},
            metrics={"read_count": 100},
            calibration_info={"last_calibrated": time.time()},
            last_heartbeat=time.time(),
            created_at=time.time()
        )
        
        test_record = TestRecord(
            record_id="REC-001",
            step=1,
            name="角度测试",
            value_type="float",
            value_raw="12.56",
            is_pass=True
        )
        
        alarm_snapshot = AlarmSnapshot(
            alarm_id="ALARM-001",
            alarm_code="CONN_ERR",
            alarm_level="warn",
            message="连接警告",
            status="resolved",
            occurred_at=time.time() - 10,
            acknowledged_at=time.time() - 5,
            resolved_at=time.time() - 1,
            closed_at=time.time(),
            task_id="TASK-001",
            station_id="STATION-001",
            device_id="DEV-001",
            workorder_id="WO-001",
            metadata={}
        )
        
        software_version = SoftwareVersion(
            encoder_test_version="1.0.0",
            driver_version="2.1.0",
            firmware_version="3.2.1",
            os_version="Linux 5.4",
            python_version="3.9.0"
        )
        
        operator_info = OperatorInfo(
            operator_id="OP-001",
            operator_name="张三",
            role="工程师",
            department="测试部"
        )
        
        # 生成报告
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=[test_record],
            alarm_snapshots=[alarm_snapshot],
            software_version=software_version,
            operator_info=operator_info
        )
        
        assert report.status == ReportStatus.GENERATED
        assert report.result == TaskResult.PASS
        assert report.generated_at is not None
        assert report.task_snapshot is not None
        assert len(report.device_snapshots) == 1
        assert len(report.test_records) == 1
        assert report.version == 1
    
    def test_report_generation_with_fail_result(self):
        """测试报告生成（失败结果）"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="encoder_test", priority="normal", status="failed",
            result="fail", error_code="ERR001", error_message="测试失败", retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-10,
            end_time=time.time(), duration_ms=10000, metrics={"step_count": 5, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="编码器测试工位",
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
        
        # 包含失败的测试记录
        pass_record = TestRecord(record_id="REC-001", step=1, name="测试1", value_type="bool", value_raw="true", is_pass=True)
        fail_record = TestRecord(record_id="REC-002", step=2, name="测试2", value_type="bool", value_raw="false", is_pass=False)
        
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=[pass_record, fail_record]  # 一个通过一个失败
        )
        
        # 应该是FAIL，因为有失败的记录
        assert report.result == TaskResult.FAIL
        assert report.status == ReportStatus.GENERATED


class TestReportArchive:
    """报告归档测试"""
    
    def test_report_archive_success(self):
        """测试报告成功归档"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        # 先生成报告
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="encoder_test", priority="normal", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-10,
            end_time=time.time(), duration_ms=10000, metrics={"step_count": 5, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="编码器测试工位",
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
            name="角度测试",
            value_type="float",
            value_raw="12.56",
            is_pass=True
        )
        
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=[test_record]
        )
        
        # 归档报告
        report.archive()
        
        assert report.status == ReportStatus.ARCHIVED
        assert report.archived_at is not None
        assert report.version == 2  # 生成+归档 = 2次版本增加
    
    def test_report_archive_from_wrong_status(self):
        """测试从错误状态归档报告"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        # 尝试直接归档草稿状态的报告（应该失败）
        with pytest.raises(ReportArchiveException):
            report.archive()


class TestReportAttachments:
    """报告附件测试"""
    
    def test_report_add_attachment(self):
        """测试报告添加附件"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        # 先生成再归档报告
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="encoder_test", priority="normal", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-10,
            end_time=time.time(), duration_ms=10000, metrics={"step_count": 5, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="编码器测试工位",
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
            name="角度测试",
            value_type="float",
            value_raw="12.56",
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
        content = b"test image content"
        report.add_attachment(
            attachment_type="image/png",
            content=content,
            description="测试图像"
        )
        
        # 验证附件被添加到元数据中
        attachments = report._metadata.get('attachments', [])
        assert len(attachments) == 1
        assert attachments[0]['type'] == "image/png"
        assert attachments[0]['description'] == "测试图像"
        assert attachments[0]['size'] == len(content)
        assert report.version == 3  # 生成+归档+添加附件 = 3次版本增加
    
    def test_report_add_attachment_to_draft(self):
        """测试给草稿状态报告添加附件（应该失败）"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        # 尝试给草稿状态的报告添加附件（应该失败）
        with pytest.raises(ReportException):
            report.add_attachment("image/png", b"content")


class TestReportMetrics:
    """报告指标测试"""
    
    def test_report_metrics_calculation(self):
        """测试报告指标计算"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="encoder_test", priority="normal", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-10,
            end_time=time.time(), duration_ms=10000, metrics={"step_count": 5, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="编码器测试工位",
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
        
        # 创建多个测试记录
        records = [
            TestRecord(record_id="REC-001", step=1, name="测试1", value_type="bool", value_raw="true", is_pass=True),
            TestRecord(record_id="REC-002", step=2, name="测试2", value_type="bool", value_raw="true", is_pass=True),
            TestRecord(record_id="REC-003", step=3, name="测试3", value_type="bool", value_raw="false", is_pass=False),
        ]
        
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=records
        )
        
        metrics = report.metrics
        assert metrics.total_records == 3
        assert metrics.pass_records == 2  # 两个通过
        assert metrics.fail_records == 1  # 一个失败
        # Duration would depend on the actual start/end times in the task snapshot


class TestReportSerialization:
    """报告序列化测试"""
    
    def test_report_to_dict(self):
        """测试报告转字典"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        task_snapshot = TaskSnapshot(
            task_id="TASK-001", workorder_id="WO-001", station_id=1, device_id="DEV-001",
            sn="SN123456", task_type="encoder_test", priority="normal", status="completed",
            result="pass", error_code=None, error_message=None, retry_count=0,
            max_retries=3, actor_id="ACTOR-001", start_time=time.time()-10,
            end_time=time.time(), duration_ms=10000, metrics={"step_count": 5, "retry_count": 0}
        )
        
        station_snapshot = StationSnapshot(
            station_id="STATION-001", code="STATION-001", name="编码器测试工位",
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
            name="角度测试",
            value_type="float",
            value_raw="12.56",
            is_pass=True
        )
        
        report.generate(
            task_snapshot=task_snapshot,
            station_snapshot=station_snapshot,
            device_snapshots=[device_snapshot],
            test_records=[test_record]
        )
        
        report_dict = report.to_dict()
        
        # 检查关键字段存在
        assert 'id' in report_dict
        assert 'task_id' in report_dict
        assert 'workorder_id' in report_dict
        assert 'sn' in report_dict
        assert 'status' in report_dict
        assert 'result' in report_dict
        assert 'task_snapshot' in report_dict
        assert 'station_snapshot' in report_dict
        assert 'device_snapshots' in report_dict
        assert 'test_records' in report_dict
        assert 'metrics' in report_dict
        
        # 检查值是否正确
        assert report_dict['task_id'] == "TASK-001"
        assert report_dict['status'] == "generated"
        assert report_dict['result'] == "pass"
        assert len(report_dict['test_records']) == 1
        assert report_dict['test_records'][0]['name'] == "角度测试"
    
    def test_report_repr(self):
        """测试报告字符串表示"""
        report = Report.create(
            task_id="TASK-001",
            workorder_id="WO-001",
            sn="SN123456"
        )
        
        repr_str = repr(report)
        assert "Report" in repr_str
        assert "SN123456" in repr_str
        assert "draft" in repr_str  # 初始状态是draft


class TestReportEnums:
    """报告枚举测试"""
    
    def test_report_status_values(self):
        """测试报告状态值"""
        assert ReportStatus.DRAFT.value == "draft"
        assert ReportStatus.GENERATED.value == "generated"
        assert ReportStatus.ARCHIVED.value == "archived"
    
    def test_record_value_type_values(self):
        """测试记录值类型值"""
        assert RecordValueType.FLOAT.value == "float"
        assert RecordValueType.BOOL.value == "bool"
        assert RecordValueType.JSON.value == "json"
        assert RecordValueType.WAVEFORM.value == "waveform"
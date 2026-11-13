"""
Django系统测试配置
提供Mock设备和测试工具
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from django.test import TestCase, Client
from django.contrib.auth.models import User
from encoder_test.models import TestCase, TestTask, TestReport


@pytest.fixture
def mock_encoder_device():
    """Mock编码器设备"""
    device = Mock()
    device.read_angle = Mock(return_value=45.0)
    device.write_angle = Mock(return_value=True)
    device.reset = Mock(return_value=True)
    device.health_check = Mock(return_value={"status": "healthy"})
    return device


@pytest.fixture
def mock_motor_device():
    """Mock电机设备"""
    device = Mock()
    device.move_to = Mock(return_value=True)
    device.stop = Mock(return_value=True)
    device.get_position = Mock(return_value=100.0)
    device.home = Mock(return_value=True)
    device.health_check = Mock(return_value={"status": "healthy"})
    return device


@pytest.fixture
def mock_power_supply():
    """Mock电源设备"""
    device = Mock()
    device.set_voltage = Mock(return_value=True)
    device.set_current = Mock(return_value=True)
    device.get_voltage = Mock(return_value=24.0)
    device.get_current = Mock(return_value=2.5)
    device.turn_on = Mock(return_value=True)
    device.turn_off = Mock(return_value=True)
    device.health_check = Mock(return_value={"status": "healthy"})
    return device


@pytest.fixture
def mock_rs485_comm():
    """Mock RS485通讯"""
    comm = Mock()
    comm.connect = Mock(return_value=True)
    comm.disconnect = Mock(return_value=True)
    comm.send = Mock(return_value=True)
    comm.recv = Mock(return_value=b'response')
    return comm


@pytest.fixture
def mock_tcp_comm():
    """Mock TCP通讯"""
    comm = Mock()
    comm.connect = Mock(return_value=True)
    comm.disconnect = Mock(return_value=True)
    comm.send = Mock(return_value=True)
    comm.recv = Mock(return_value=b'response')
    return comm


@pytest.fixture
def test_user(db):
    """创建测试用户"""
    user = User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    """认证的测试客户端"""
    client.force_login(test_user)
    return client


@pytest.fixture
def sample_test_case(db):
    """示例测试用例"""
    test_case = TestCase.objects.create(
        name="示例测试用例",
        description="这是一个示例测试用例",
        test_type="unit",
        script_path="/test/cases/sample.py",
        parameters={"param1": "value1"},
        status="active"
    )
    return test_case


@pytest.fixture
def sample_test_task(db, sample_test_case):
    """示例测试任务"""
    task = TestTask.objects.create(
        name="示例测试任务",
        test_case=sample_test_case,
        status="pending",
        executed_by="testuser"
    )
    return task


@pytest.fixture
def sample_test_report(db, sample_test_task):
    """示例测试报告"""
    report = TestReport.objects.create(
        task=sample_test_task,
        report_name="示例测试报告",
        report_path="/reports/sample.html",
        summary={"total_tests": 10, "passed_tests": 8}
    )
    return report


class DjangoTestCase(TestCase):
    """Django测试基类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def create_test_case(self, **kwargs):
        """创建测试用例"""
        defaults = {
            'name': '测试用例',
            'test_type': 'unit',
            'script_path': '/test/cases/test.py',
            'status': 'active'
        }
        defaults.update(kwargs)
        return TestCase.objects.create(**defaults)
    
    def create_test_task(self, test_case, **kwargs):
        """创建测试任务"""
        defaults = {
            'name': '测试任务',
            'test_case': test_case,
            'status': 'pending',
            'executed_by': 'testuser'
        }
        defaults.update(kwargs)
        return TestTask.objects.create(**defaults)
    
    def create_test_report(self, task, **kwargs):
        """创建测试报告"""
        defaults = {
            'task': task,
            'report_name': '测试报告',
            'report_path': '/reports/test.html',
            'summary': {}
        }
        defaults.update(kwargs)
        return TestReport.objects.create(**defaults)
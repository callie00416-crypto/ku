"""
测试结果构建器 - 工业测试平台标准结果格式
"""
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class TestStatus(str, Enum):
    """测试状态"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


class TestResult:
    """测试结果 - 工业标准格式"""
    
    def __init__(self, test_id: str, test_name: str):
        self.test_id = test_id
        self.test_name = test_name
        self.status = TestStatus.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.duration: float = 0.0
        self.data: Dict[str, Any] = {}
        self.error: Optional[str] = None
        self.traceback: Optional[str] = None
        self.measurements: list = []
        self.assertions: list = []
        self.logs: list = []
    
    def start(self):
        """开始测试"""
        self.status = TestStatus.RUNNING
        self.start_time = datetime.now()
    
    def finish(self, status: TestStatus, error: Optional[str] = None, traceback: Optional[str] = None):
        """完成测试"""
        self.status = status
        self.end_time = datetime.now()
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
        self.error = error
        self.traceback = traceback
    
    def add_measurement(self, name: str, value: Any, unit: Optional[str] = None):
        """添加测量数据"""
        measurement = {
            'name': name,
            'value': value,
            'unit': unit,
            'timestamp': datetime.now().isoformat()
        }
        self.measurements.append(measurement)
    
    def add_assertion(self, assertion: str, passed: bool, expected: Any, actual: Any):
        """添加断言结果"""
        assertion_result = {
            'assertion': assertion,
            'passed': passed,
            'expected': expected,
            'actual': actual,
            'timestamp': datetime.now().isoformat()
        }
        self.assertions.append(assertion_result)
    
    def add_log(self, level: str, message: str):
        """添加日志"""
        log_entry = {
            'level': level,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.logs.append(log_entry)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'test_id': self.test_id,
            'test_name': self.test_name,
            'status': self.status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'data': self.data,
            'error': self.error,
            'traceback': self.traceback,
            'measurements': self.measurements,
            'assertions': self.assertions,
            'logs': self.logs
        }
    
    def is_passed(self) -> bool:
        """是否通过"""
        return self.status == TestStatus.PASSED
    
    def is_failed(self) -> bool:
        """是否失败"""
        return self.status in [TestStatus.FAILED, TestStatus.ERROR, TestStatus.TIMEOUT]


class ResultBuilder:
    """测试结果构建器 - 工业测试平台标准构建器"""
    
    @staticmethod
    def create_success(test_id: str, test_name: str, data: Optional[Dict[str, Any]] = None) -> TestResult:
        """创建成功结果"""
        result = TestResult(test_id, test_name)
        result.start()
        result.finish(TestStatus.PASSED)
        if data:
            result.data = data
        return result
    
    @staticmethod
    def create_failure(test_id: str, test_name: str, error: str, 
                      traceback: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> TestResult:
        """创建失败结果"""
        result = TestResult(test_id, test_name)
        result.start()
        result.finish(TestStatus.FAILED, error, traceback)
        if data:
            result.data = data
        return result
    
    @staticmethod
    def create_error(test_id: str, test_name: str, error: str, 
                    traceback: Optional[str] = None) -> TestResult:
        """创建错误结果"""
        result = TestResult(test_id, test_name)
        result.start()
        result.finish(TestStatus.ERROR, error, traceback)
        return result
    
    @staticmethod
    def create_timeout(test_id: str, test_name: str, timeout: float) -> TestResult:
        """创建超时结果"""
        result = TestResult(test_id, test_name)
        result.start()
        result.finish(TestStatus.TIMEOUT, f"Test timeout after {timeout}s")
        return result
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> TestResult:
        """从字典创建结果"""
        result = TestResult(data['test_id'], data['test_name'])
        result.status = TestStatus(data['status'])
        result.duration = data.get('duration', 0.0)
        result.data = data.get('data', {})
        result.error = data.get('error')
        result.traceback = data.get('traceback')
        result.measurements = data.get('measurements', [])
        result.assertions = data.get('assertions', [])
        result.logs = data.get('logs', [])
        
        if data.get('start_time'):
            result.start_time = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            result.end_time = datetime.fromisoformat(data['end_time'])
        
        return result
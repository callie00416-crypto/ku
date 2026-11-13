"""
测试执行器 - 负责执行单个测试用例
"""
import time
from typing import Dict, Any, Callable
from enum import Enum

from projects.encoder_test.utils.result_builder import ResultBuilder, TestResult
from datetime import datetime


class Status(Enum):
    """测试状态"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


# 向后兼容别名
TestStatus = Status


class Executor:
    """测试执行器"""
    
    def __init__(self, test_case: Dict[str, Any], driver_manager=None):
        """
        Args:
            test_case: 测试用例配置
            driver_manager: 驱动管理器
        """
        self.test_case = test_case
        self.driver_manager = driver_manager
        self.status = TestStatus.PENDING
        self.result = {}
        self.duration = 0.0
    
    def execute(self) -> Dict[str, Any]:
        """
        执行测试用例
        
        Returns:
            测试结果字典
        """
        start_time = time.time()
        self.status = TestStatus.RUNNING
        
        try:
            # 获取测试函数
            test_func = self.test_case.get('test_func')
            if not test_func or not callable(test_func):
                raise ValueError("测试用例未配置 test_func")
            
            # 执行测试
            result = test_func(self.driver_manager)
            
            # 判断结果
            if isinstance(result, bool):
                self.status = TestStatus.PASSED if result else TestStatus.FAILED
            elif isinstance(result, dict):
                self.status = TestStatus.PASSED if result.get('passed', False) else TestStatus.FAILED
                self.result.update(result)
            else:
                self.status = TestStatus.PASSED
            
        except Exception as e:
            self.status = TestStatus.ERROR
            self.result['error'] = str(e)
        
        self.duration = time.time() - start_time
        
        # 使用结果构建器创建标准化的结果
        test_result = ResultBuilder.create_result(
            case_code=self.test_case.get('case_code', ''),
            case_name=self.test_case.get('case_name', ''),
            status=self.status.value,
            duration=self.duration,
            error_message=self.result.get('error', ''),
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.now(),
            **{k: v for k, v in self.result.items() if k != 'error'}
        )
        
        self.result = test_result.to_dict()
        return self.result
    
    def get_result(self) -> Dict[str, Any]:
        """获取测试结果"""
        return self.result


# 向后兼容别名
TestExecutor = Executor
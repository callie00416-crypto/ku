"""
TestCase 模块 - 测试用例框架

【核心组件】
- BaseCase: 测试用例基类，支持 pytest 断言
- CaseResult: 测试结果
- CaseContext: 测试上下文

【使用示例】
from projects.encoder_test.core.testcase import BaseCase, CaseResult

class MyTestCase(BaseCase):
    def setup(self):
        self.encoder = self.get_device('encoder')
    
    def run(self):
        # 直接使用 assert
        assert self.encoder.is_connected(), "编码器未连接"
"""
from projects.encoder_test.core.testcase.base.base_case import BaseCase
from projects.encoder_test.core.testcase.base.case_result import CaseResult, CaseStatus, AssertResult
from projects.encoder_test.core.testcase.base.case_context import CaseContext
from projects.encoder_test.core.testcase.base.decorator import test_case, TestCaseMeta, get_case_meta
from projects.encoder_test.core.testcase.base.config import TestConfig, PrecisionTestConfig, RepeatabilityTestConfig, get_config

from projects.encoder_test.core.testcase.encoder import (
    EncoderPowerCycleCase,
    EncoderSinglePowerCycleCase
)

__all__ = [
    'BaseCase',
    'CaseResult',
    'CaseStatus', 
    'AssertResult',
    'CaseContext',
    'test_case',
    'TestCaseMeta',
    'get_case_meta',
    'TestConfig',
    'PrecisionTestConfig',
    'RepeatabilityTestConfig',
    'get_config',
    'EncoderPowerCycleCase',
    'EncoderSinglePowerCycleCase',
]
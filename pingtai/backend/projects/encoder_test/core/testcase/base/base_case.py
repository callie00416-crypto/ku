"""
BaseCase - 测试用例基类

【核心特性】
直接使用 pytest 断言语法：
    assert actual == expected, "失败消息"
    assert value < threshold
    assert 0 <= value <= 100

【为什么这样设计】
- pytest 是 Python 最流行的测试框架
- assert 语句自带详细的错误报告
- 支持 pytest 插件生态（覆盖率、并行等）

【使用示例】
class EncoderAccuracyCase(BaseCase):
    def setup(self):
        self.encoder = self.get_device('encoder')
        self.tolerance = 0.1
    
    def run(self):
        # 直接用 assert，就像写普通 pytest 测试！
        angle = self.encoder.read_angle()
        assert abs(angle) <= self.tolerance, f"角度 {angle} 超过容忍度 {self.tolerance}"

# 两种执行方式都支持
case = EncoderAccuracyCase()
result = case.execute()  # 独立运行

# 或直接用 pytest
# pytest test_case.py::test_encoder_accuracy  # 会失败
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging
import time
from datetime import datetime

from projects.encoder_test.core.testcase.base.case_result import CaseResult, CaseStatus, AssertResult, AssertLevel
from projects.encoder_test.core.testcase.base.case_context import CaseContext

logger = logging.getLogger(__name__)


class BaseCase(ABC):
    """测试用例基类 - 原生支持 pytest 断言
    
    设计原则：
    1. run() 方法中直接使用 Python assert 语句
    2. 断言失败自动捕获并记录到 CaseResult
    3. 支持独立运行和 pytest 运行
    """
    
    def __init__(self, case_id: str = None, description: str = "", timeout: float = 600.0, **kwargs):
        self.case_id = case_id or self.__class__.__name__
        self.description = description
        self.timeout = timeout
        
        self._flows: List[Any] = []
        self._context: Optional[CaseContext] = None
        self._result: Optional[CaseResult] = None
        
        self._start_time: float = 0.0
        self._end_time: float = 0.0
        
        self._setup_complete = False
        
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def result(self) -> Optional[CaseResult]:
        """获取测试结果"""
        return self._result
    
    @property
    def context(self) -> Optional[CaseContext]:
        """获取上下文"""
        return self._context
    
    @abstractmethod
    def setup(self):
        """设置用例（子类实现）
        
        在此方法中：
        1. 添加 Flow（可选）
        2. 设置测试参数
        3. 注册设备
        
        示例：
        def setup(self):
            self.add_flow(StartupFlow(power=self.power))
            self.set_parameter('voltage', 5.0)
            self.set_device('encoder', self.encoder)
        """
        pass
    
    def _ensure_setup(self):
        """确保 setup 已执行"""
        if not self._setup_complete:
            self._ensure_context()
            self.setup()
            self._setup_complete = True
    
    def _ensure_context(self):
        """确保上下文已创建"""
        if self._context is None:
            self._context = CaseContext()
            self._context.case_id = self.case_id
    
    def add_flow(self, flow) -> 'BaseCase':
        """添加 Flow（支持链式调用）"""
        self._flows.append(flow)
        return self
    
    def set_device(self, name: str, device: Any):
        """设置设备"""
        self._ensure_context()
        self._context.set_device(name, device)
    
    def get_device(self, name: str) -> Optional[Any]:
        """获取设备"""
        self._ensure_context()
        return self._context.get_device(name)
    
    def set_parameter(self, key: str, value: Any):
        """设置测试参数"""
        self._ensure_context()
        self._context.set_parameter(key, value)
    
    def get_parameter(self, key: str, default=None) -> Any:
        """获取测试参数"""
        self._ensure_context()
        return self._context.get_parameter(key, default)
    
    def set_runtime(self, key: str, value: Any):
        """设置运行时数据"""
        self._ensure_context()
        self._context.set_runtime(key, value)
    
    def get_runtime(self, key: str, default=None) -> Any:
        """获取运行时数据"""
        self._ensure_context()
        return self._context.get_runtime(key, default)
    
    def record_data(self, key: str, value: Any):
        """记录测试数据"""
        self._ensure_context()
        self._context.record_data(key, value)
    
    def execute(self, context: CaseContext = None) -> CaseResult:
        """执行测试用例
        
        完整流程：
        1. before_case() - 执行前准备
        2. setup() - 设置用例（子类实现）
        3. run() - 执行测试（使用 assert）
        4. after_case() - 执行后清理
        """
        logger.info(f"[{self.case_id}] 开始执行测试用例")
        
        self._start_time = time.time()
        
        if context:
            self._context = context
        elif self._context is None:
            self._context = CaseContext()
            self._context.case_id = self.case_id
        
        self._result = CaseResult(case_id=self.case_id)
        self._result.start_time = datetime.now()
        
        try:
            self.before_case()
            self._ensure_setup()
            self._result.status = CaseStatus.RUNNING
            
            self.run()
            
            self._result.status = CaseStatus.PASSED
            self._result.message = "测试通过"
            logger.info(f"[{self.case_id}] 测试通过")
            
        except AssertionError as e:
            self._result.status = CaseStatus.FAILED
            self._result.message = str(e)
            self._result.error_detail = str(e)
            self._record_assertion(False, "assert", expected="True", actual="False", message=str(e))
            logger.error(f"[{self.case_id}] 测试失败: {e}")
            
        except Exception as e:
            self._result.status = CaseStatus.ERROR
            self._result.message = f"执行异常: {str(e)}"
            self._result.error_detail = str(e)
            logger.exception(f"[{self.case_id}] 执行异常")
        
        finally:
            self._end_time = time.time()
            self._result.duration = self._end_time - self._start_time
            self._result.end_time = datetime.now()
            
            # 将测试数据传递到结果
            if self._context:
                self._result.data = self._context.get_all_data()
            
            self.after_case()
        
        return self._result
    
    def _record_assertion(self, passed: bool, name: str, expected: Any, actual: Any, message: str, level: str = AssertLevel.ERROR.value):
        """记录断言结果"""
        result = AssertResult(
            passed=passed,
            name=name,
            expected=expected,
            actual=actual,
            message=message,
            level=level
        )
        self._result.add_assertion(result)
    
    def run(self):
        """执行测试逻辑（子类实现）
        
        在此处直接使用 assert 语句，就像写普通 pytest 测试：
        
        def run(self):
            angle = self.encoder.read_angle()
            assert abs(angle) <= 0.1, f"角度误差 {abs(angle)} 过大"
        """
        self._ensure_setup()
        
        for flow in self._flows:
            logger.info(f"[{self.case_id}] 执行 Flow: {flow.flow_id}")
            flow_result = flow.execute()
            
            if not flow_result.success:
                raise AssertionError(f"Flow {flow.flow_id} 执行失败: {flow_result.message}")
    
    def before_case(self):
        """执行前钩子（可重写）"""
        logger.debug(f"[{self.case_id}] before_case")
    
    def after_case(self):
        """执行后钩子（可重写）"""
        logger.debug(f"[{self.case_id}] after_case")
    
    def assert_true(self, condition: bool, message: str = "条件应为 True"):
        """断言条件为 True（兼容旧代码）"""
        assert condition, message
    
    def assert_false(self, condition: bool, message: str = "条件应为 False"):
        """断言条件为 False（兼容旧代码）"""
        assert not condition, message
    
    def assert_equal(self, actual: Any, expected: Any, message: str = ""):
        """断言相等（兼容旧代码）"""
        assert actual == expected, message or f"期望 {expected}，实际 {actual}"
    
    def assert_not_equal(self, actual: Any, expected: Any, message: str = ""):
        """断言不相等（兼容旧代码）"""
        assert actual != expected, message or f"不应等于 {expected}"
    
    def assert_less(self, actual: float, threshold: float, message: str = ""):
        """断言 actual < threshold（兼容旧代码）"""
        assert actual < threshold, message or f"{actual} 应小于 {threshold}"
    
    def assert_less_or_equal(self, actual: float, threshold: float, message: str = ""):
        """断言 actual <= threshold（兼容旧代码）"""
        assert actual <= threshold, message or f"{actual} 应小于等于 {threshold}"
    
    def assert_greater(self, actual: float, threshold: float, message: str = ""):
        """断言 actual > threshold（兼容旧代码）"""
        assert actual > threshold, message or f"{actual} 应大于 {threshold}"
    
    def assert_range(self, actual: float, min_val: float, max_val: float, message: str = ""):
        """断言值在范围内（兼容旧代码）"""
        assert min_val <= actual <= max_val, message or f"{actual} 应在 [{min_val}, {max_val}] 范围内"
    
    def skip(self, message: str = "跳过测试"):
        """跳过测试"""
        self._result.status = CaseStatus.SKIPPED
        self._result.message = message
        logger.warning(f"[{self.case_id}] 跳过测试: {message}")
        raise AssertionError(message)
    
    def log(self, message: str):
        """记录日志"""
        logger.info(f"[{self.case_id}] {message}")
        if self._result is not None:
            self._result.add_log(message)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}[{self.case_id}]>"
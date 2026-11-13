"""
断言工具模块 - 精度/稳定性/通讯断言、阈值配置、异常判定
"""
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import time

from projects.encoder_test.utils.decorators import timer, call_with_timeout, TimeoutError

logger = logging.getLogger(__name__)


class AssertType(Enum):
    """断言类型"""
    PRECISION = "precision"  # 精度断言
    STABILITY = "stability"  # 稳定性断言
    RANGE = "range"  # 范围断言
    COMMUNICATION = "communication"  # 通讯断言
    THRESHOLD = "threshold"  # 阈值断言
    CUSTOM = "custom"  # 自定义断言


class AssertResultStatus(Enum):
    """断言结果状态"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class AssertConfig:
    """断言配置"""
    name: str
    assert_type: AssertType
    description: str = ""
    enabled: bool = True
    
    # 精度断言参数
    expected_value: float = 0.0
    tolerance: float = 0.0  # 允许误差
    tolerance_percent: float = 0.0  # 允许误差百分比
    
    # 范围断言参数
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    
    # 稳定性断言参数
    sample_count: int = 10
    max_variance: float = 0.0
    max_deviation: float = 0.0
    
    # 通讯断言参数
    timeout: float = 5.0
    retry_count: int = 3
    
    # 自定义断言
    custom_func: Optional[callable] = None
    
    # 标签
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """验证配置合法性"""
        if self.assert_type == AssertType.PRECISION:
            if self.tolerance == 0 and self.tolerance_percent == 0:
                raise ValueError("精度断言必须设置 tolerance 或 tolerance_percent")


@dataclass
class AssertResult:
    """断言结果"""
    config: AssertConfig
    result: str  # pass, fail, warning, error
    actual_value: Any = None
    expected_value: Any = None
    error_message: str = ""
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_pass(self) -> bool:
        return self.result == AssertResultStatus.PASS.value
    
    def is_fail(self) -> bool:
        return self.result == AssertResultStatus.FAIL.value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.config.name,
            'type': self.config.assert_type.value,
            'result': self.result,
            'actual_value': self.actual_value,
            'expected_value': self.expected_value,
            'error_message': self.error_message,
            'timestamp': self.timestamp,
            'duration': self.duration,
            'metadata': self.metadata
        }


class AssertTool:
    """断言工具 - 提供多种断言方法"""
    
    def __init__(self):
        self._results: List[AssertResult] = []
        self._configs: Dict[str, AssertConfig] = {}
    
    def _create_result(self, config: AssertConfig, result_status: AssertResultStatus,
                       actual_value: Any = None, expected_value: Any = None,
                       error_message: str = "", duration: float = 0.0,
                       metadata: Dict[str, Any] = None) -> AssertResult:
        """
        创建断言结果（内部辅助方法）
        
        Args:
            config: 断言配置
            result_status: 结果状态
            actual_value: 实际值
            expected_value: 期望值
            error_message: 错误信息
            duration: 执行时长
            metadata: 元数据
            
        Returns:
            AssertResult
        """
        assert_result = AssertResult(
            config=config,
            result=result_status.value,
            actual_value=actual_value,
            expected_value=expected_value,
            error_message=error_message,
            duration=duration,
            metadata=metadata or {}
        )
        
        self._results.append(assert_result)
        
        # 记录日志
        if result_status == AssertResultStatus.FAIL:
            logger.warning(f"断言失败: {config.name}, {error_message}")
        elif result_status == AssertResultStatus.ERROR:
            logger.error(f"断言异常: {config.name}, {error_message}")
        else:
            logger.debug(f"断言通过: {config.name}")
        
        return assert_result
    
    def add_config(self, config: AssertConfig):
        """
        添加断言配置
        
        Args:
            config: 断言配置
        """
        if not config.enabled:
            logger.debug(f"跳过禁用的断言配置: {config.name}")
            return
        
        self._configs[config.name] = config
        logger.debug(f"添加断言配置: {config.name} ({config.assert_type.value})")
    
    def add_configs(self, configs: List[AssertConfig]):
        """批量添加断言配置"""
        for config in configs:
            self.add_config(config)
    
    def get_config(self, name: str) -> Optional[AssertConfig]:
        """获取断言配置"""
        return self._configs.get(name)
    
    def assert_precision(self, actual: float, expected: float, 
                         tolerance: float = 0.0, tolerance_percent: float = 0.0,
                         name: str = "precision_assert",
                         description: str = "") -> AssertResult:
        """
        精度断言 - 检查实际值与期望值的误差是否在允许范围内
        
        Args:
            actual: 实际值
            expected: 期望值
            tolerance: 绝对误差容忍度
            tolerance_percent: 百分比误差容忍度（%）
            name: 断言名称
            description: 断言描述
            
        Returns:
            AssertResult
        """
        start_time = time.time()
        error = abs(actual - expected)
        
        # 计算允许的误差
        allowed_error = tolerance
        if tolerance_percent > 0:
            allowed_error = max(allowed_error, abs(expected) * tolerance_percent / 100.0)
        
        # 判断结果
        if error <= allowed_error:
            result_status = AssertResultStatus.PASS
            error_msg = ""
        else:
            result_status = AssertResultStatus.FAIL
            error_msg = f"误差超差: 实际误差={error:.6f}, 允许误差={allowed_error:.6f}"
        
        duration = time.time() - start_time
        
        return self._create_result(
            config=AssertConfig(
                name=name,
                assert_type=AssertType.PRECISION,
                expected_value=expected,
                tolerance=tolerance,
                tolerance_percent=tolerance_percent,
                description=description
            ),
            result_status=result_status,
            actual_value=actual,
            expected_value=expected,
            error_message=error_msg,
            duration=duration,
            metadata={'error': error, 'allowed_error': allowed_error}
        )
    
    def assert_range(self, value: float, min_val: float = None, max_val: float = None,
                     name: str = "range_assert", description: str = "") -> AssertResult:
        """
        范围断言 - 检查值是否在指定范围内
        
        Args:
            value: 待检查的值
            min_val: 最小值（None表示无下限）
            max_val: 最大值（None表示无上限）
            name: 断言名称
            description: 断言描述
            
        Returns:
            AssertResult
        """
        start_time = time.time()
        
        in_range = True
        error_msg = ""
        
        if min_val is not None and value < min_val:
            in_range = False
            error_msg = f"值 {value} 小于最小值 {min_val}"
        elif max_val is not None and value > max_val:
            in_range = False
            error_msg = f"值 {value} 大于最大值 {max_val}"
        
        result_status = AssertResultStatus.PASS if in_range else AssertResultStatus.FAIL
        duration = time.time() - start_time
        
        return self._create_result(
            config=AssertConfig(
                name=name,
                assert_type=AssertType.RANGE,
                min_value=min_val,
                max_value=max_val,
                description=description
            ),
            result_status=result_status,
            actual_value=value,
            expected_value={'min': min_val, 'max': max_val},
            error_message=error_msg,
            duration=duration
        )
    
    def assert_stability(self, values: List[float], 
                         max_variance: float = None,
                         max_deviation: float = None,
                         name: str = "stability_assert",
                         description: str = "") -> AssertResult:
        """
        稳定性断言 - 检查数据序列的稳定性
        
        Args:
            values: 数据序列
            max_variance: 最大方差
            max_deviation: 最大偏差（相对平均值）
            name: 断言名称
            description: 断言描述
            
        Returns:
            AssertResult
        """
        start_time = time.time()
        
        if len(values) < 2:
            return AssertResult(
                config=AssertConfig(name=name, assert_type=AssertType.STABILITY),
                result=AssertResultStatus.ERROR.value,
                error_message="数据样本不足（至少需要2个值）",
                duration=time.time() - start_time
            )
        
        # 计算统计值
        avg = sum(values) / len(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        max_val = max(values)
        min_val = min(values)
        deviation = max_val - min_val
        
        # 判断结果
        stable = True
        error_msg = ""
        
        if max_variance is not None and variance > max_variance:
            stable = False
            error_msg = f"方差 {variance:.6f} 超过阈值 {max_variance:.6f}"
        
        if max_deviation is not None and deviation > max_deviation:
            stable = False
            if error_msg:
                error_msg += "; "
            error_msg += f"偏差 {deviation:.6f} 超过阈值 {max_deviation:.6f}"
        
        result = AssertResultStatus.PASS if stable else AssertResultStatus.FAIL
        duration = time.time() - start_time
        
        assert_result = AssertResult(
            config=AssertConfig(
                name=name,
                assert_type=AssertType.STABILITY,
                max_variance=max_variance,
                max_deviation=max_deviation,
                description=description
            ),
            result=result.value,
            actual_value=values,
            expected_value={'variance': variance, 'std_dev': std_dev, 'deviation': deviation},
            error_message=error_msg,
            duration=duration,
            metadata={'average': avg, 'variance': variance, 'std_dev': std_dev}
        )
        
        self._results.append(assert_result)
        
        if not stable:
            logger.warning(f"稳定性断言失败: {name}, {error_msg}")
        
        return assert_result
    
    def assert_threshold(self, value: float, threshold: float, 
                         operator: str = "lt",  # lt, lte, gt, gte, eq
                         name: str = "threshold_assert",
                         description: str = "") -> AssertResult:
        """
        阈值断言 - 检查值是否满足阈值条件
        
        Args:
            value: 待检查的值
            threshold: 阈值
            operator: 比较操作符 (lt=小于, lte=小于等于, gt=大于, gte=大于等于, eq=等于)
            name: 断言名称
            description: 断言描述
            
        Returns:
            AssertResult
        """
        start_time = time.time()
        
        ops = {
            'lt': lambda a, b: a < b,
            'lte': lambda a, b: a <= b,
            'gt': lambda a, b: a > b,
            'gte': lambda a, b: a >= b,
            'eq': lambda a, b: a == b
        }
        
        if operator not in ops:
            return AssertResult(
                config=AssertConfig(name=name, assert_type=AssertType.THRESHOLD),
                result=AssertResultStatus.ERROR.value,
                error_message=f"不支持的操作符: {operator}",
                duration=time.time() - start_time
            )
        
        passed = ops[operator](value, threshold)
        result = AssertResultStatus.PASS if passed else AssertResultStatus.FAIL
        duration = time.time() - start_time
        
        error_msg = "" if passed else f"值 {value} 不满足条件 {operator} {threshold}"
        
        assert_result = AssertResult(
            config=AssertConfig(
                name=name,
                assert_type=AssertType.THRESHOLD,
                description=description
            ),
            result=result.value,
            actual_value=value,
            expected_value=threshold,
            error_message=error_msg,
            duration=duration,
            metadata={'operator': operator}
        )
        
        self._results.append(assert_result)
        
        if not passed:
            logger.warning(f"阈值断言失败: {name}, {error_msg}")
        
        return assert_result
    
    def assert_custom(self, test_func: callable, 
                      name: str = "custom_assert",
                      description: str = "",
                      *args, **kwargs) -> AssertResult:
        """
        自定义断言 - 执行自定义测试函数
        
        Args:
            test_func: 测试函数，返回 bool 或 (bool, message)
            name: 断言名称
            description: 断言描述
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            AssertResult
        """
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            
            if isinstance(result, tuple):
                passed, message = result
            else:
                passed = bool(result)
                message = ""
            
            result_type = AssertResultStatus.PASS if passed else AssertResultStatus.FAIL
            duration = time.time() - start_time
            
            assert_result = AssertResult(
                config=AssertConfig(
                    name=name,
                    assert_type=AssertType.CUSTOM,
                    description=description
                ),
                result=result_type.value,
                error_message=message if not passed else "",
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            assert_result = AssertResult(
                config=AssertConfig(
                    name=name,
                    assert_type=AssertType.CUSTOM,
                    description=description
                ),
                result=AssertResultStatus.ERROR.value,
                error_message=f"断言执行异常: {str(e)}",
                duration=duration
            )
        
        self._results.append(assert_result)
        
        if assert_result.is_fail():
            logger.warning(f"自定义断言失败: {name}, {assert_result.error_message}")
        elif assert_result.result == AssertResultStatus.ERROR.value:
            logger.error(f"自定义断言异常: {name}, {assert_result.error_message}")
        
        return assert_result
    
    def assert_communication(self, connect_func: callable, 
                             timeout: float = 5.0,
                             retry_count: int = 3,
                             name: str = "comm_assert",
                             description: str = "") -> AssertResult:
        """
        通讯断言 - 测试通讯连接的可靠性
        
        Args:
            connect_func: 连接测试函数，返回 bool
            timeout: 超时时间（秒）
            retry_count: 重试次数
            name: 断言名称
            description: 断言描述
            
        Returns:
            AssertResult
        """
        start_time = time.time()
        
        success_count = 0
        fail_count = 0
        
        for i in range(retry_count):
            try:
                result = call_with_timeout(connect_func, timeout)
                
                if result:
                    success_count += 1
                else:
                    fail_count += 1
                    
            except TimeoutError:
                fail_count += 1
                logger.debug(f"通讯测试超时 (尝试 {i+1}/{retry_count})")
            except Exception as e:
                fail_count += 1
                logger.debug(f"通讯测试异常 (尝试 {i+1}/{retry_count}): {e}")
        
        duration = time.time() - start_time
        success_rate = success_count / retry_count if retry_count > 0 else 0
        
        # 成功率 >= 80% 认为通过
        passed = success_rate >= 0.8
        result_status = AssertResultStatus.PASS if passed else AssertResultStatus.FAIL
        
        error_msg = "" if passed else f"通讯成功率 {success_rate:.1%} 低于阈值 80%"
        
        return self._create_result(
            config=AssertConfig(
                name=name,
                assert_type=AssertType.COMMUNICATION,
                timeout=timeout,
                retry_count=retry_count,
                description=description
            ),
            result_status=result_status,
            error_message=error_msg,
            duration=duration,
            metadata={
                'success_count': success_count,
                'fail_count': fail_count,
                'success_rate': success_rate
            }
        )
    
    def get_results(self, filter_type: AssertType = None) -> List[AssertResult]:
        """
        获取断言结果
        
        Args:
            filter_type: 按类型筛选
            
        Returns:
            断言结果列表
        """
        if filter_type:
            return [r for r in self._results if r.config.assert_type == filter_type]
        return self._results.copy()
    
    def get_failed_results(self) -> List[AssertResult]:
        """获取失败的断言结果"""
        return [r for r in self._results if r.is_fail() or r.result == AssertResultStatus.ERROR.value]
    
    def get_pass_count(self) -> int:
        """获取通过数量"""
        return sum(1 for r in self._results if r.is_pass())
    
    def get_fail_count(self) -> int:
        """获取失败数量"""
        return sum(1 for r in self._results if r.is_fail() or r.result == AssertResultStatus.ERROR.value)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self._results)
        passed = self.get_pass_count()
        failed = self.get_fail_count()
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': passed / total if total > 0 else 0.0
        }
    
    def clear_results(self):
        """清空结果"""
        self._results.clear()
    
    def clear_configs(self):
        """清空配置"""
        self._configs.clear()
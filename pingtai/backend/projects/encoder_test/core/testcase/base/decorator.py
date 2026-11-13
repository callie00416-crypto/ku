"""
测试用例装饰器

用于标记测试用例元信息，支持自动扫描和数据库同步

使用示例：
    @test_case(
        case_code="CASE-001",
        case_name="编码器零点测试",
        params={"tolerance": 0.1}
    )
    def test_zero_point(case: BaseCase):
        assert abs(angle) <= 0.1
"""
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class TestCaseMeta:
    """测试用例元数据"""
    case_code: str
    case_name: str
    description: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    category: str = "default"
    priority: int = 1
    enabled: bool = True
    tags: list = field(default_factory=list)


def test_case(
    case_code: str,
    case_name: str,
    description: str = "",
    params: Optional[Dict[str, Any]] = None,
    category: str = "default",
    priority: int = 1,
    enabled: bool = True,
    tags: Optional[list] = None
):
    """测试用例装饰器"""
    def decorator(func: Callable):
        func._test_case_meta = TestCaseMeta(
            case_code=case_code,
            case_name=case_name,
            description=description or func.__doc__ or "",
            params=params or {},
            category=category,
            priority=priority,
            enabled=enabled,
            tags=tags or []
        )
        return func
    return decorator


def get_case_meta(func: Callable) -> Optional[TestCaseMeta]:
    """获取用例元数据"""
    return getattr(func, '_test_case_meta', None)
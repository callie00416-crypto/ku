"""
自定义测试用例基类
用于业务自定义扩展用例的统一接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseTestCase(ABC):
    """自定义测试用例基类"""
    
    def __init__(self, name: str = "", description: str = ""):
        self.name = name
        self.description = description
        self.result = None
        self.status = "pending"  # pending, running, passed, failed, error
        
    @abstractmethod
    def setup(self) -> None:
        """测试前置条件"""
        pass
    
    @abstractmethod
    def execute(self) -> Any:
        """执行测试逻辑"""
        pass
    
    @abstractmethod
    def teardown(self) -> None:
        """测试后清理"""
        pass
    
    def run(self) -> Dict[str, Any]:
        """运行测试用例"""
        try:
            self.status = "running"
            self.setup()
            self.result = self.execute()
            self.status = "passed"
        except Exception as e:
            self.status = "failed"
            self.result = {"error": str(e)}
        finally:
            self.teardown()
        
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "result": self.result
        }
    
    def validate_result(self, expected: Any) -> bool:
        """验证测试结果"""
        return self.result == expected

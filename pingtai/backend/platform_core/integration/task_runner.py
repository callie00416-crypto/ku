"""
任务运行器
统一调度：内核用例/自定义用例
"""

import importlib
import inspect
from typing import Dict, List, Any, Optional
from django.conf import settings


class TaskRunner:
    """统一任务调度器"""
    
    def __init__(self):
        self.kernel_test_path = getattr(settings, 'KERNEL_TEST_PATH', 'backend.encoder_test.core.testcases')
        self.custom_test_path = getattr(settings, 'CUSTOM_TEST_PATH', 'test_cases')
    
    def run_kernel_test(self, test_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        运行内核测试用例
        
        Args:
            test_name: 测试用例名称
            params: 测试参数
            
        Returns:
            测试结果
        """
        try:
            # 动态导入内核测试模块
            module_path = f"{self.kernel_test_path}.{test_name}"
            module = importlib.import_module(module_path)
            
            # 查找测试类或函数
            test_item = self._find_test_item(module, test_name)
            
            if test_item is None:
                return {
                    'status': 'error',
                    'message': f'Test case {test_name} not found'
                }
            
            # 执行测试
            result = self._execute_test(test_item, params or {})
            
            return {
                'status': 'success',
                'test_name': test_name,
                'result': result
            }
            
        except ImportError as e:
            return {
                'status': 'error',
                'message': f'Failed to import test case {test_name}: {str(e)}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error running kernel test {test_name}: {str(e)}'
            }
    
    def run_custom_test(self, test_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        运行自定义测试用例
        
        Args:
            test_name: 测试用例名称
            params: 测试参数
            
        Returns:
            测试结果
        """
        try:
            # 动态导入自定义测试模块
            module_path = f"{self.custom_test_path}.{test_name}"
            module = importlib.import_module(module_path)
            
            # 查找测试类或函数
            test_item = self._find_test_item(module, test_name)
            
            if test_item is None:
                return {
                    'status': 'error',
                    'message': f'Custom test case {test_name} not found'
                }
            
            # 执行测试
            result = self._execute_test(test_item, params or {})
            
            return {
                'status': 'success',
                'test_name': test_name,
                'result': result
            }
            
        except ImportError as e:
            return {
                'status': 'error',
                'message': f'Failed to import custom test case {test_name}: {str(e)}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error running custom test {test_name}: {str(e)}'
            }
    
    def _find_test_item(self, module, test_name: str):
        """
        在模块中查找测试项（类或函数）
        
        Args:
            module: Python 模块
            test_name: 测试名称
            
        Returns:
            测试类或函数，如果未找到则返回 None
        """
        # 首先尝试按名称直接查找
        if hasattr(module, test_name):
            return getattr(module, test_name)
        
        # 查找包含测试名称的类或函数
        for name, obj in inspect.getmembers(module):
            if name.lower() == test_name.lower():
                return obj
        
        return None
    
    def _execute_test(self, test_item, params: Dict[str, Any]) -> Any:
        """
        执行测试项
        
        Args:
            test_item: 测试类或函数
            params: 测试参数
            
        Returns:
            测试结果
        """
        # 如果是类，实例化并调用 run 方法
        if inspect.isclass(test_item):
            instance = test_item(**params)
            if hasattr(instance, 'run'):
                return instance.run()
            else:
                raise AttributeError(f"Test class {test_item.__name__} does not have a 'run' method")
        
        # 如果是函数，直接调用
        elif inspect.isfunction(test_item):
            return test_item(**params)
        
        else:
            raise TypeError(f"Unsupported test item type: {type(test_item)}")
    
    def list_kernel_tests(self) -> List[str]:
        """列出所有可用的内核测试"""
        return self._list_tests_in_module(self.kernel_test_path)
    
    def list_custom_tests(self) -> List[str]:
        """列出所有可用的自定义测试"""
        return self._list_tests_in_module(self.custom_test_path)
    
    def _list_tests_in_module(self, module_path: str) -> List[str]:
        """
        列出模块中的所有测试
        
        Args:
            module_path: 模块路径
            
        Returns:
            测试名称列表
        """
        try:
            module = importlib.import_module(module_path)
            tests = []
            
            for name, obj in inspect.getmembers(module):
                # 检查是否是测试类或函数
                if (inspect.isclass(obj) or inspect.isfunction(obj)) and \
                   ('test' in name.lower() or hasattr(obj, '__test__')):
                    tests.append(name)
            
            return tests
        except ImportError:
            return []


# 全局任务运行器实例
task_runner = TaskRunner()


def run_kernel_test(test_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """快捷函数：运行内核测试"""
    return task_runner.run_kernel_test(test_name, params)


def run_custom_test(test_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """快捷函数：运行自定义测试"""
    return task_runner.run_custom_test(test_name, params)

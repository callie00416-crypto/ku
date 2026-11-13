"""
用例管理模块 - pytest用例加载、按标签筛选、批量执行、用例排序
"""
import os
import sys
import importlib
import inspect
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Case:
    """测试用例数据结构"""
    case_id: str
    case_code: str
    case_name: str
    test_func: Callable
    tags: List[str] = field(default_factory=list)
    priority: int = 1  # 1=高, 2=中, 3=低
    params: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    depends_on: List[str] = field(default_factory=list)  # 依赖的其他用例
    timeout: float = 30.0  # 超时时间（秒）
    description: str = ""
    
    def has_tag(self, tag: str) -> bool:
        """检查是否包含指定标签"""
        return tag in self.tags
    
    def has_any_tag(self, tags: List[str]) -> bool:
        """检查是否包含任意一个标签"""
        return any(tag in self.tags for tag in tags)
    
    def has_all_tags(self, tags: List[str]) -> bool:
        """检查是否包含所有标签"""
        return all(tag in self.tags for tag in tags)


# 向后兼容别名
TestCase = Case


class CaseManager:
    """用例管理器 - 负责用例加载、筛选、排序、批量执行"""
    
    def __init__(self):
        self.cases: Dict[str, Case] = {}
        self._case_order: List[str] = []  # 维护用例顺序
        self._lock = threading.RLock()
    
    def add_case(self, case: Case):
        """
        添加测试用例
        
        Args:
            case: Case实例
        """
        if not case.enabled:
            logger.debug(f"跳过禁用的用例: {case.case_code}")
            return
        
        with self._lock:
            self.cases[case.case_id] = case
            if case.case_id not in self._case_order:
                self._case_order.append(case.case_id)
        
        logger.debug(f"添加用例: {case.case_code} ({case.case_name})")
    
    def add_cases(self, cases: List[Case]):
        """批量添加用例"""
        for case in cases:
            self.add_case(case)
    
    def remove_case(self, case_id: str):
        """移除用例"""
        if case_id in self.cases:
            del self.cases[case_id]
            self._case_order.remove(case_id)
            logger.debug(f"移除用例: {case_id}")
    
    def get_case(self, case_id: str) -> Optional[Case]:
        """获取单个用例"""
        return self.cases.get(case_id)
    
    def get_cases(self, case_ids: List[str] = None) -> List[Case]:
        """
        获取用例列表
        
        Args:
            case_ids: 指定的用例ID列表，None表示获取所有
            
        Returns:
            Case列表
        """
        if case_ids:
            return [self.cases[cid] for cid in case_ids if cid in self.cases]
        return [self.cases[cid] for cid in self._case_order if cid in self.cases]
    
    def filter_by_tags(self, tags: List[str], match_all: bool = False) -> List[Case]:
        """
        按标签筛选用例
        
        Args:
            tags: 标签列表
            match_all: True=匹配所有标签，False=匹配任意标签
            
        Returns:
            筛选后的用例列表
        """
        filtered = []
        for case in self.get_cases():
            if match_all:
                if case.has_all_tags(tags):
                    filtered.append(case)
            else:
                if case.has_any_tag(tags):
                    filtered.append(case)
        
        logger.info(f"按标签筛选 {tags} (match_all={match_all}): 找到 {len(filtered)} 个用例")
        return filtered
    
    def filter_by_priority(self, priority: int) -> List[Case]:
        """按优先级筛选"""
        return [c for c in self.get_cases() if c.priority == priority]
    
    def sort_by_priority(self, cases: List[Case] = None) -> List[Case]:
        """
        按优先级排序（高优先级在前）
        
        Args:
            cases: 用例列表，None表示对所有用例排序
            
        Returns:
            排序后的用例列表
        """
        target_cases = cases or self.get_cases()
        return sorted(target_cases, key=lambda c: (c.priority, self._case_order.index(c.case_id) if c.case_id in self._case_order else 999))
    
    def sort_by_dependency(self, cases: List[Case] = None) -> List[Case]:
        """
        按依赖关系排序（被依赖的用例在前）
        
        Args:
            cases: 用例列表
            
        Returns:
            排序后的用例列表
        """
        target_cases = cases or self.get_cases()
        case_map = {c.case_id: c for c in target_cases}
        
        # 拓扑排序
        visited = set()
        result = []
        
        def visit(case_id):
            if case_id in visited:
                return
            visited.add(case_id)
            
            case = case_map.get(case_id)
            if case:
                # 先处理依赖的用例
                for dep_id in case.depends_on:
                    if dep_id in case_map:
                        visit(dep_id)
                result.append(case)
        
        for case in target_cases:
            visit(case.case_id)
        
        logger.info(f"按依赖关系排序: {len(result)} 个用例")
        return result
    
    def load_from_directory(self, test_dir: str, tags: List[str] = None) -> List[Case]:
        """
        从目录加载测试用例（扫描Python文件）
        
        Args:
            test_dir: 测试文件目录
            tags: 默认标签
            
        Returns:
            加载的用例列表
        """
        test_path = Path(test_dir)
        if not test_path.exists():
            logger.warning(f"测试目录不存在: {test_dir}")
            return []
        
        loaded_cases = []
        
        # 扫描所有Python文件
        for py_file in test_path.rglob('*.py'):
            if py_file.name.startswith('test_') or py_file.name.startswith('_'):
                continue
            
            try:
                # 动态导入模块
                module_path = str(py_file).replace(os.sep, '.')[:-3]
                if module_path.startswith('.'):
                    module_path = module_path[1:]
                
                module = importlib.import_module(module_path)
                cases = self.extract_cases_from_module(module, tags)
                loaded_cases.extend(cases)
                
            except Exception as e:
                logger.error(f"加载测试文件失败 {py_file}: {e}")
        
        logger.info(f"从目录加载用例: {len(loaded_cases)} 个 (目录: {test_dir})")
        return loaded_cases
    
    def extract_cases_from_module(self, module, tags: List[str] = None) -> List[Case]:
        """
        从模块中提取测试用例
        
        Args:
            module: Python模块
            tags: 标签列表
            
        Returns:
            提取的用例列表
        """
        cases = []
        
        for name, obj in inspect.getmembers(module):
            # 只提取函数，且名称不以'_'开头
            if inspect.isfunction(obj) and not name.startswith('_'):
                # 检查函数签名是否接受 context 参数
                sig = inspect.signature(obj)
                params = list(sig.parameters.keys())
                
                # 简单约定：接受 context 参数的函数视为测试用例
                if 'context' in params or 'driver_manager' in params:
                    case = Case(
                        case_id=f"{module.__name__}.{name}",
                        case_code=name.upper().replace('_', '-'),
                        case_name=name,
                        test_func=obj,
                        tags=tags or [],
                        description=obj.__doc__ or ""
                    )
                    cases.append(case)
        
        return cases
    
    def load_from_config(self, config: Dict[str, Any]) -> List[Case]:
        """
        从配置字典加载用例
        
        Args:
            config: 用例配置列表
            
        Returns:
            加载的用例列表
        """
        cases = []
        
        for case_config in config.get('test_cases', []):
            # 解析测试函数
            test_func = self._resolve_test_func(case_config.get('test_func'))
            
            if not test_func:
                logger.warning(f"无法解析测试函数: {case_config.get('test_func')}")
                continue
            
            case = Case(
                case_id=case_config.get('case_id', case_config['case_code']),
                case_code=case_config['case_code'],
                case_name=case_config['case_name'],
                test_func=test_func,
                tags=case_config.get('tags', []),
                priority=case_config.get('priority', 1),
                params=case_config.get('params', {}),
                enabled=case_config.get('enabled', True),
                depends_on=case_config.get('depends_on', []),
                timeout=case_config.get('timeout', 30.0),
                description=case_config.get('description', '')
            )
            cases.append(case)
        
        logger.info(f"从配置加载用例: {len(cases)} 个")
        return cases
    
    def _resolve_test_func(self, func_ref: str) -> Optional[Callable]:
        """
        解析函数引用字符串为可调用对象
        
        Args:
            func_ref: 函数引用，如 'test_encoder.read_angle'
            
        Returns:
            可调用对象或None
        """
        try:
            if '.' in func_ref:
                module_path, func_name = func_ref.rsplit('.', 1)
                module = importlib.import_module(module_path)
                return getattr(module, func_name)
            else:
                # 尝试从当前模块查找
                import __main__
                return getattr(__main__, func_ref, None)
        except Exception as e:
            logger.error(f"解析函数引用失败 {func_ref}: {e}")
            return None
    
    def get_case_count(self) -> int:
        """获取用例总数"""
        return len(self.cases)
    
    def get_enabled_count(self) -> int:
        """获取启用用例数"""
        return sum(1 for c in self.cases.values() if c.enabled)
    
    def clear(self):
        """清空所有用例"""
        self.cases.clear()
        self._case_order.clear()
        logger.info("用例管理器已清空")


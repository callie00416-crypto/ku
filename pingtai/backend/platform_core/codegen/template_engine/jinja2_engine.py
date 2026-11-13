"""
Jinja2模板引擎 - Jinja2 Template Engine

【职责】
- 基于Jinja2的模板渲染
- 支持模板继承和包含
- 提供丰富的过滤器
"""
from typing import Dict, Any, Optional
from pathlib import Path
import logging

try:
    from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
    from jinja2 import select_autoescape
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

from .engine import TemplateEngine


logger = logging.getLogger(__name__)


class Jinja2Engine(TemplateEngine):
    """Jinja2模板引擎实现"""
    
    def __init__(self, config):
        """
        Args:
            config: 平台配置
        """
        if not JINJA2_AVAILABLE:
            raise ImportError("Jinja2未安装，请安装: pip install jinja2")
        
        super().__init__(config)
        
        # 创建Jinja2环境
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            auto_reload=False,
            cache_size=self.config.template_engine.cache_size if self.cache_enabled else 0
        )
        
        # 注册自定义过滤器
        self._register_filters()
        
        # 注册自定义测试器
        self._register_tests()
        
        logger.info("Jinja2模板引擎初始化完成")
    
    def _register_filters(self):
        """注册自定义过滤器"""
        
        # 首字母大写
        def capitalize_filter(value):
            if isinstance(value, str):
                return value.capitalize()
            return value
        
        # 驼峰命名
        def camel_case_filter(value):
            if isinstance(value, str):
                components = value.split('_')
                return components[0] + ''.join(x.title() for x in components[1:])
            return value
        
        # 帕斯卡命名
        def pascal_case_filter(value):
            if isinstance(value, str):
                return ''.join(x.title() for x in value.split('_'))
            return value
        
        # 蛇形命名
        def snake_case_filter(value):
            if isinstance(value, str):
                import re
                s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
                return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
            return value
        
        # 添加类型提示
        def type_hint_filter(value):
            type_mapping = {
                'str': 'str',
                'int': 'int',
                'float': 'float',
                'bool': 'bool',
                'list': 'List',
                'dict': 'Dict',
                'any': 'Any'
            }
            return type_mapping.get(value, value)
        
        # Python JSON转换（处理布尔值）
        def to_python_json(value):
            """转换为Python兼容的JSON字符串"""
            import json
            json_str = json.dumps(value, ensure_ascii=False)
            # 替换JSON布尔值为Python布尔值
            json_str = json_str.replace('true', 'True').replace('false', 'False')
            return json_str
        
        # 注册过滤器
        self.env.filters['capitalize'] = capitalize_filter
        self.env.filters['camel_case'] = camel_case_filter
        self.env.filters['pascal_case'] = pascal_case_filter
        self.env.filters['snake_case'] = snake_case_filter
        self.env.filters['type_hint'] = type_hint_filter
        self.env.filters['tojson'] = to_python_json
    
    def _register_tests(self):
        """注册自定义测试器"""
        
        # 测试是否为None
        def is_none(value):
            return value is None
        
        # 测试是否为空
        def is_empty(value):
            if value is None:
                return True
            if isinstance(value, (str, list, dict)):
                return len(value) == 0
            return False
        
        # 注册测试器
        self.env.tests['none'] = is_none
        self.env.tests['empty'] = is_empty
    
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """渲染模板
        
        Args:
            template_name: 模板名称
            context: 上下文数据
            
        Returns:
            渲染结果
        """
        try:
            # 检查缓存
            cache_key = f"{template_name}:{hash(str(context))}"
            if self.cache_enabled and cache_key in self.cache:
                return self.cache[cache_key]
            
            # 加载模板
            template = self.env.get_template(template_name)
            
            # 渲染模板
            result = template.render(**context)
            
            # 缓存结果
            if self.cache_enabled:
                self.cache[cache_key] = result
            
            return result
            
        except TemplateNotFound as e:
            logger.error(f"模板未找到: {template_name}")
            raise FileNotFoundError(f"模板未找到: {template_name}") from e
        except Exception as e:
            logger.error(f"模板渲染失败: {e}")
            raise
    
    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """渲染模板字符串
        
        Args:
            template_string: 模板字符串
            context: 上下文数据
            
        Returns:
            渲染结果
        """
        try:
            # 检查缓存
            cache_key = f"string:{hash(template_string)}:{hash(str(context))}"
            if self.cache_enabled and cache_key in self.cache:
                return self.cache[cache_key]
            
            # 创建模板
            template = self.env.from_string(template_string)
            
            # 渲染模板
            result = template.render(**context)
            
            # 缓存结果
            if self.cache_enabled:
                self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"模板字符串渲染失败: {e}")
            raise
    
    def add_global(self, name: str, value: Any):
        """添加全局变量
        
        Args:
            name: 变量名
            value: 变量值
        """
        self.env.globals[name] = value
        logger.info(f"添加全局变量: {name}")
    
    def add_filter(self, name: str, filter_func):
        """添加自定义过滤器
        
        Args:
            name: 过滤器名称
            filter_func: 过滤器函数
        """
        self.env.filters[name] = filter_func
        logger.info(f"添加过滤器: {name}")
    
    def add_test(self, name: str, test_func):
        """添加自定义测试器
        
        Args:
            name: 测试器名称
            test_func: 测试器函数
        """
        self.env.tests[name] = test_func
        logger.info(f"添加测试器: {name}")
    
    def get_template_names(self) -> list:
        """获取所有模板名称
        
        Returns:
            模板名称列表
        """
        template_names = []
        if self.template_dir.exists():
            for template_file in self.template_dir.rglob('*.j2'):
                rel_path = template_file.relative_to(self.template_dir)
                template_names.append(str(rel_path))
        return template_names
    
    def template_exists(self, template_name: str) -> bool:
        """检查模板是否存在
        
        Args:
            template_name: 模板名称
            
        Returns:
            是否存在
        """
        try:
            self.env.get_template(template_name)
            return True
        except TemplateNotFound:
            return False
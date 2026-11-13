"""
代码生成平台核心 - CodeGen Platform Core

【职责】
- 平台入口和协调器
- 模块生命周期管理
- 插件系统管理
- 错误处理和日志
"""
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
import logging
import traceback

from .config import CodeGenConfig


class CodeGenPlatform:
    """代码生成平台核心类
    
    【职责】
    - 协调各个模块工作
    - 管理插件系统
    - 提供统一接口
    - 处理错误和日志
    
    【使用示例】
    >>> platform = CodeGenPlatform(config)
    >>> platform.initialize()
    >>> result = platform.generate(device_spec)
    >>> platform.shutdown()
    """
    
    def __init__(self, config: Optional[CodeGenConfig] = None):
        """
        Args:
            config: 平台配置
        """
        self.config = config or CodeGenConfig()
        self.logger = self._setup_logger()
        
        # 模块实例
        self._modules = {}
        
        # 插件系统
        self._plugins = {}
        self._hooks = {}
        
        # 状态管理
        self._initialized = False
        self._started = False
        
        self.logger.info(f"代码生成平台初始化: {self.config.project_name}")
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger('CodeGenPlatform')
        logger.setLevel(logging.DEBUG if self.config.debug else logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def initialize(self):
        """初始化平台
        
        【三阶段生命周期】
        - Construct: __init__ 中完成
        - Initialize: 本方法中完成
        - Start: start 方法中完成
        """
        if self._initialized:
            self.logger.warning("平台已经初始化")
            return
        
        try:
            self.logger.info("开始初始化代码生成平台...")
            
            # 验证配置
            if not self.config.validate():
                raise ValueError("配置验证失败")
            
            # 初始化核心模块
            self._initialize_modules()
            
            # 加载插件
            self._load_plugins()
            
            self._initialized = True
            self.logger.info("代码生成平台初始化完成")
            
        except Exception as e:
            self.logger.error(f"平台初始化失败: {e}")
            self.logger.debug(traceback.format_exc())
            raise
    
    def _initialize_modules(self):
        """初始化核心模块"""
        try:
            # 延迟导入，避免循环依赖
            from ..template_engine.engine import TemplateEngine
            from ..generator.engine import GeneratorEngine
            from ..scaffold.builder import ScaffoldBuilder
            from ..ast.processor import ASTProcessor
            
            # 初始化模板引擎
            if self.config.template_engine.engine_type == "jinja2":
                from ..template_engine.jinja2_engine import Jinja2Engine
                self._modules['template_engine'] = Jinja2Engine(self.config)
            else:
                self._modules['template_engine'] = TemplateEngine(self.config)
            
            # 初始化生成器
            self._modules['generator'] = GeneratorEngine(self.config, self._modules['template_engine'])
            
            # 初始化脚手架
            self._modules['scaffold'] = ScaffoldBuilder(self.config)
            
            # 初始化AST处理器
            if self.config.ast.enabled:
                self._modules['ast'] = ASTProcessor(self.config)
            
            # 初始化AI代码生成器
            if self.config.ai.enabled:
                from ..ai.codegen import AICodeGenerator
                self._modules['ai'] = AICodeGenerator(self.config)
            
            self.logger.info(f"核心模块初始化完成: {list(self._modules.keys())}")
            
        except ImportError as e:
            self.logger.warning(f"部分模块初始化失败: {e}")
        except Exception as e:
            self.logger.error(f"模块初始化错误: {e}")
            raise
    
    def _load_plugins(self):
        """加载插件"""
        for plugin_name in self.config.plugins:
            try:
                self.load_plugin(plugin_name)
            except Exception as e:
                self.logger.warning(f"插件加载失败 {plugin_name}: {e}")
    
    def load_plugin(self, plugin_name: str):
        """加载插件
        
        Args:
            plugin_name: 插件名称
        """
        try:
            # 动态导入插件
            import importlib
            plugin_module = importlib.import_module(plugin_name)
            
            # 获取插件类
            if hasattr(plugin_module, 'Plugin'):
                plugin_class = plugin_module.Plugin
                plugin_instance = plugin_class(self.config, self)
                
                self._plugins[plugin_name] = plugin_instance
                
                # 注册插件钩子
                if hasattr(plugin_instance, 'register_hooks'):
                    hooks = plugin_instance.register_hooks()
                    for hook_name, hook_func in hooks.items():
                        self.register_hook(hook_name, hook_func)
                
                self.logger.info(f"插件加载成功: {plugin_name}")
            else:
                raise ValueError(f"插件 {plugin_name} 缺少 Plugin 类")
                
        except Exception as e:
            self.logger.error(f"插件加载失败 {plugin_name}: {e}")
            raise
    
    def register_hook(self, hook_name: str, hook_func: Callable):
        """注册钩子
        
        Args:
            hook_name: 钩子名称
            hook_func: 钩子函数
        """
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(hook_func)
    
    def execute_hook(self, hook_name: str, *args, **kwargs):
        """执行钩子
        
        Args:
            hook_name: 钩子名称
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            钩子执行结果列表
        """
        results = []
        if hook_name in self._hooks:
            for hook_func in self._hooks[hook_name]:
                try:
                    result = hook_func(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    self.logger.warning(f"钩子执行失败 {hook_name}: {e}")
        return results
    
    def start(self):
        """启动平台"""
        if not self._initialized:
            self.initialize()
        
        if self._started:
            self.logger.warning("平台已经启动")
            return
        
        try:
            self.logger.info("启动代码生成平台...")
            
            # 启动所有模块
            for module_name, module_instance in self._modules.items():
                if hasattr(module_instance, 'start'):
                    module_instance.start()
                    self.logger.info(f"模块启动完成: {module_name}")
            
            # 执行启动钩子
            self.execute_hook('on_platform_start')
            
            self._started = True
            self.logger.info("代码生成平台启动完成")
            
        except Exception as e:
            self.logger.error(f"平台启动失败: {e}")
            self.logger.debug(traceback.format_exc())
            raise
    
    def shutdown(self):
        """关闭平台"""
        if not self._started:
            return
        
        try:
            self.logger.info("关闭代码生成平台...")
            
            # 执行关闭钩子
            self.execute_hook('on_platform_shutdown')
            
            # 关闭所有模块
            for module_name, module_instance in reversed(self._modules.items()):
                if hasattr(module_instance, 'shutdown'):
                    module_instance.shutdown()
                    self.logger.info(f"模块关闭完成: {module_name}")
            
            self._started = False
            self.logger.info("代码生成平台关闭完成")
            
        except Exception as e:
            self.logger.error(f"平台关闭失败: {e}")
            raise
    
    def get_module(self, module_name: str):
        """获取模块实例
        
        Args:
            module_name: 模块名称
            
        Returns:
            模块实例
        """
        if module_name not in self._modules:
            raise ValueError(f"模块不存在: {module_name}")
        return self._modules[module_name]
    
    def has_module(self, module_name: str) -> bool:
        """检查模块是否存在
        
        Args:
            module_name: 模块名称
            
        Returns:
            是否存在
        """
        return module_name in self._modules
    
    def generate(self, spec: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """生成代码
        
        Args:
            spec: 生成规范
            **kwargs: 额外参数
            
        Returns:
            生成结果
        """
        if not self._started:
            self.start()
        
        try:
            self.logger.info(f"开始生成代码: {spec.get('name', 'unknown')}")
            
            # 执行生成前钩子
            self.execute_hook('before_generate', spec=spec)
            
            # 获取生成器模块
            generator = self.get_module('generator')
            
            # 执行生成
            result = generator.generate(spec, **kwargs)
            
            # 执行生成后钩子
            self.execute_hook('after_generate', spec=spec, result=result)
            
            self.logger.info(f"代码生成完成: {result.get('files_count', 0)} 个文件")
            return result
            
        except Exception as e:
            self.logger.error(f"代码生成失败: {e}")
            self.logger.debug(traceback.format_exc())
            raise
    
    def create_scaffold(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """创建项目脚手架
        
        Args:
            project_spec: 项目规范
            
        Returns:
            创建结果
        """
        if not self._started:
            self.start()
        
        try:
            self.logger.info(f"开始创建脚手架: {project_spec.get('name', 'unknown')}")
            
            # 获取脚手架构建器
            scaffold = self.get_module('scaffold')
            
            # 创建脚手架
            result = scaffold.build(project_spec)
            
            self.logger.info(f"脚手架创建完成: {result.get('files_count', 0)} 个文件")
            return result
            
        except Exception as e:
            self.logger.error(f"脚手架创建失败: {e}")
            self.logger.debug(traceback.format_exc())
            raise
    
    def validate_code(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """验证代码
        
        Args:
            code: 代码内容
            language: 编程语言
            
        Returns:
            验证结果
        """
        if not self.has_module('ast'):
            return {'valid': True, 'message': 'AST模块未启用'}
        
        try:
            ast_processor = self.get_module('ast')
            return ast_processor.validate(code, language)
        except Exception as e:
            self.logger.error(f"代码验证失败: {e}")
            return {'valid': False, 'message': str(e)}
    
    def optimize_code(self, code: str, language: str = 'python') -> str:
        """优化代码
        
        Args:
            code: 代码内容
            language: 编程语言
            
        Returns:
            优化后的代码
        """
        if not self.has_module('ast'):
            return code
        
        try:
            ast_processor = self.get_module('ast')
            return ast_processor.optimize(code, language)
        except Exception as e:
            self.logger.error(f"代码优化失败: {e}")
            return code
    
    def ai_generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """AI生成代码
        
        Args:
            prompt: 提示词
            context: 上下文信息
            
        Returns:
            生成的代码
        """
        if not self.has_module('ai'):
            raise RuntimeError("AI代码生成模块未启用")
        
        try:
            ai_generator = self.get_module('ai')
            return ai_generator.generate(prompt, context)
        except Exception as e:
            self.logger.error(f"AI代码生成失败: {e}")
            raise
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.shutdown()
        return False
    
    def __repr__(self) -> str:
        return f"CodeGenPlatform(name={self.config.project_name}, modules={len(self._modules)}, plugins={len(self._plugins)})"
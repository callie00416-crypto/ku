"""
代码生成平台配置 - CodeGen Configuration

【职责】
- 管理平台配置
- 提供配置验证
- 支持配置文件加载
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import yaml


@dataclass
class TemplateEngineConfig:
    """模板引擎配置"""
    engine_type: str = "jinja2"  # jinja2, mako, string
    template_dir: str = "templates"
    cache_enabled: bool = True
    cache_size: int = 100


@dataclass
class GeneratorConfig:
    """生成器配置"""
    output_dir: str = "output"
    overwrite: bool = False
    format_code: bool = True
    validate_output: bool = True


@dataclass
class AIConfig:
    """AI代码生成配置"""
    enabled: bool = False
    model: str = "gpt-4"
    api_key: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7


@dataclass
class ASTConfig:
    """AST配置"""
    enabled: bool = True
    language: str = "python"
    validate_syntax: bool = True
    optimize_ast: bool = True


@dataclass
class CodeGenConfig:
    """代码生成平台总配置"""
    
    # 基础配置
    project_name: str = "codegen_project"
    version: str = "1.0.0"
    debug: bool = False
    
    # 模块配置
    template_engine: TemplateEngineConfig = field(default_factory=TemplateEngineConfig)
    generator: GeneratorConfig = field(default_factory=GeneratorConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    ast: ASTConfig = field(default_factory=ASTConfig)
    
    # 扩展配置
    plugins: List[str] = field(default_factory=list)
    custom_handlers: Dict[str, str] = field(default_factory=dict)
    
    # 路径配置
    base_path: Optional[Path] = None
    config_path: Optional[Path] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.base_path is None:
            self.base_path = Path.cwd()
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'CodeGenConfig':
        """从字典创建配置"""
        # 处理嵌套配置
        template_engine_dict = config_dict.pop('template_engine', {})
        generator_dict = config_dict.pop('generator', {})
        ai_dict = config_dict.pop('ai', {})
        ast_dict = config_dict.pop('ast', {})
        
        return cls(
            template_engine=TemplateEngineConfig(**template_engine_dict),
            generator=GeneratorConfig(**generator_dict),
            ai=AIConfig(**ai_dict),
            ast=ASTConfig(**ast_dict),
            **config_dict
        )
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'CodeGenConfig':
        """从文件加载配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置对象
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        # 根据文件扩展名选择解析器
        if config_path.suffix == '.json':
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
        elif config_path.suffix in ['.yaml', '.yml']:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
        else:
            raise ValueError(f"不支持的配置文件格式: {config_path.suffix}")
        
        config = cls.from_dict(config_dict)
        config.config_path = config_path
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'project_name': self.project_name,
            'version': self.version,
            'debug': self.debug,
            'template_engine': {
                'engine_type': self.template_engine.engine_type,
                'template_dir': self.template_engine.template_dir,
                'cache_enabled': self.template_engine.cache_enabled,
                'cache_size': self.template_engine.cache_size
            },
            'generator': {
                'output_dir': self.generator.output_dir,
                'overwrite': self.generator.overwrite,
                'format_code': self.generator.format_code,
                'validate_output': self.generator.validate_output
            },
            'ai': {
                'enabled': self.ai.enabled,
                'model': self.ai.model,
                'api_key': self.ai.api_key,
                'max_tokens': self.ai.max_tokens,
                'temperature': self.ai.temperature
            },
            'ast': {
                'enabled': self.ast.enabled,
                'language': self.ast.language,
                'validate_syntax': self.ast.validate_syntax,
                'optimize_ast': self.ast.optimize_ast
            },
            'plugins': self.plugins,
            'custom_handlers': self.custom_handlers
        }
    
    def save_to_file(self, config_path: Optional[Path] = None):
        """保存配置到文件
        
        Args:
            config_path: 配置文件路径，默认使用当前配置路径
        """
        if config_path is None:
            config_path = self.config_path
        
        if config_path is None:
            raise ValueError("未指定配置文件路径")
        
        config_dict = self.to_dict()
        config_path = Path(config_path)
        
        # 根据文件扩展名选择保存格式
        if config_path.suffix == '.json':
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
        elif config_path.suffix in ['.yaml', '.yml']:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, allow_unicode=True, default_flow_style=False)
        else:
            raise ValueError(f"不支持的配置文件格式: {config_path.suffix}")
    
    def validate(self) -> bool:
        """验证配置有效性
        
        Returns:
            是否有效
        """
        try:
            # 验证基础配置
            if not self.project_name:
                raise ValueError("项目名称不能为空")
            
            # 验证模板引擎配置
            if self.template_engine.engine_type not in ["jinja2", "mako", "string"]:
                raise ValueError(f"不支持的模板引擎类型: {self.template_engine.engine_type}")
            
            # 验证生成器配置
            if self.generator.output_dir:
                output_path = self.base_path / self.generator.output_dir
                # 不强制要求目录存在，生成时会创建
            
            # 验证AI配置
            if self.ai.enabled and not self.ai.api_key:
                raise ValueError("AI功能启用但未配置API密钥")
            
            return True
        except Exception as e:
            if self.debug:
                raise
            return False
    
    def get_output_path(self) -> Path:
        """获取输出路径"""
        return self.base_path / self.generator.output_dir
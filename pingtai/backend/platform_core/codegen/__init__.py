"""
代码生成平台 - CodeGen Platform

【模块说明】
- core: 核心平台和配置
- dsl: 领域特定语言
- template_engine: 模板引擎
- generator: 代码生成引擎
- scaffold: 项目脚手架
- ast: 代码分析和转换
- ai: AI代码生成
"""
from .core.platform import CodeGenPlatform
from .core.config import CodeGenConfig

__all__ = [
    'CodeGenPlatform',
    'CodeGenConfig'
]
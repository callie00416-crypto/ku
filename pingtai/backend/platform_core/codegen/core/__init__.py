"""
代码生成平台核心模块 - Core Module

【模块说明】
- platform: 平台核心类
- config: 配置管理
"""
from .platform import CodeGenPlatform
from .config import CodeGenConfig

__all__ = [
    'CodeGenPlatform',
    'CodeGenConfig'
]
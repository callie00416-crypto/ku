"""
模板引擎 - Template Engine

【职责】
- 提供模板渲染能力
- 支持多种模板引擎
- 模板缓存管理
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class TemplateEngine(ABC):
    """模板引擎抽象基类"""
    
    def __init__(self, config):
        """
        Args:
            config: 平台配置
        """
        self.config = config
        self.template_dir = Path(config.base_path) / config.template_engine.template_dir
        self.cache_enabled = config.template_engine.cache_enabled
        self.cache = {}
        
        # 确保模板目录存在
        self.template_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """渲染模板
        
        Args:
            template_name: 模板名称
            context: 上下文数据
            
        Returns:
            渲染结果
        """
        pass
    
    @abstractmethod
    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """渲染模板字符串
        
        Args:
            template_string: 模板字符串
            context: 上下文数据
            
        Returns:
            渲染结果
        """
        pass
    
    def get_template_path(self, template_name: str) -> Path:
        """获取模板路径
        
        Args:
            template_name: 模板名称
            
        Returns:
            模板文件路径
        """
        return self.template_dir / template_name
    
    def template_exists(self, template_name: str) -> bool:
        """检查模板是否存在
        
        Args:
            template_name: 模板名称
            
        Returns:
            是否存在
        """
        return self.get_template_path(template_name).exists()
    
    def load_template(self, template_name: str) -> str:
        """加载模板内容
        
        Args:
            template_name: 模板名称
            
        Returns:
            模板内容
        """
        template_path = self.get_template_path(template_name)
        
        if not template_path.exists():
            raise FileNotFoundError(f"模板不存在: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("模板缓存已清空")
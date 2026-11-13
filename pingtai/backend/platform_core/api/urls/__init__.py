"""
通用URL路由 - Common URL Patterns

【职责】
提供工业平台的通用URL路由配置

【设计原则】
- RESTful规范
- 统一路由格式
- 支持版本控制
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from typing import List, Dict, Any


def create_platform_router() -> DefaultRouter:
    """创建平台路由器"""
    router = DefaultRouter()
    router.trailing_slash = '/?'  # 支持带/和不带/的URL
    return router


def get_standard_urlpatterns(prefix: str = 'api/v1') -> List:
    """获取标准URL模式
    
    Args:
        prefix: API前缀，默认为 'api/v1'
        
    Returns:
        URL模式列表
    """
    return [
        path(f'{prefix}/', include([
            # 设备相关路由
            path('devices/', include('platform.api.urls.devices')),
            # 任务相关路由
            path('tasks/', include('platform.api.urls.tasks')),
            # 工位相关路由
            path('stations/', include('platform.api.urls.stations')),
            # 告警相关路由
            path('alarms/', include('platform.api.urls.alarms')),
            # 报告相关路由
            path('reports/', include('platform.api.urls.reports')),
        ])),
    ]


def register_viewset(router: DefaultRouter, prefix: str, viewset, basename: str):
    """注册视图集到路由器
    
    Args:
        router: 路由器实例
        prefix: URL前缀
        viewset: 视图集类
        basename: 基础名称
    """
    router.register(prefix, viewset, basename=basename)
"""
编码器测试系统 - URL 路由
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import TestCaseViewSet, TestTaskViewSet, TestReportViewSet
from .views.scanner import ScannerViewSet
from .views.station import StationViewSet

router = DefaultRouter()
router.register(r'test-cases', TestCaseViewSet, basename='test-case')
router.register(r'test-tasks', TestTaskViewSet, basename='test-task')
router.register(r'test-reports', TestReportViewSet, basename='test-report')
router.register(r'scanner', ScannerViewSet, basename='scanner')

# 工位管理（使用ViewSet）
router.register(r'stations', StationViewSet, basename='station')

urlpatterns = router.urls
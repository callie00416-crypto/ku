"""
通用序列化器 - Common Serializers

【职责】
提供工业平台的通用序列化器
包含设备、任务、工位、告警、报告等通用序列化器

【设计原则】
- 通用
- 可扩展
- 符合DRF规范
"""
from rest_framework import serializers
from typing import Dict, Any, Optional, List
from datetime import datetime


class PlatformSerializer(serializers.Serializer):
    """平台序列化器基类"""
    
    def to_representation(self, instance):
        """重写to_representation，添加平台标准字段"""
        data = super().to_representation(instance)
        
        # 添加平台标准字段
        if hasattr(instance, 'created_at'):
            data['created_at'] = instance.created_at.isoformat() if instance.created_at else None
        if hasattr(instance, 'updated_at'):
            data['updated_at'] = instance.updated_at.isoformat() if instance.updated_at else None
        if hasattr(instance, 'version'):
            data['version'] = instance.version
            
        return data


class DeviceSerializer(PlatformSerializer):
    """设备序列化器"""
    device_id = serializers.CharField(max_length=64)
    device_name = serializers.CharField(max_length=128, required=False)
    device_type = serializers.CharField(max_length=32)
    status = serializers.CharField(max_length=16)
    metadata = serializers.JSONField(required=False)
    station_id = serializers.CharField(max_length=64, required=False)
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class TaskSerializer(PlatformSerializer):
    """任务序列化器"""
    task_id = serializers.CharField(max_length=64)
    task_name = serializers.CharField(max_length=128)
    task_type = serializers.CharField(max_length=32)
    station_id = serializers.CharField(max_length=64)
    priority = serializers.CharField(max_length=16, required=False)
    status = serializers.CharField(max_length=16)
    progress = serializers.FloatField(required=False, default=0.0)
    metadata = serializers.JSONField(required=False)
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class StationSerializer(PlatformSerializer):
    """工位序列化器"""
    station_id = serializers.CharField(max_length=64)
    station_name = serializers.CharField(max_length=128)
    station_type = serializers.CharField(max_length=32)
    status = serializers.CharField(max_length=16)
    device_ids = serializers.ListField(
        child=serializers.CharField(max_length=64),
        required=False
    )
    current_task_id = serializers.CharField(max_length=64, required=False)
    metadata = serializers.JSONField(required=False)
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class AlarmSerializer(PlatformSerializer):
    """告警序列化器"""
    alarm_id = serializers.CharField(max_length=64)
    alarm_code = serializers.CharField(max_length=64)
    alarm_level = serializers.CharField(max_length=16)
    message = serializers.CharField()
    status = serializers.CharField(max_length=16)
    
    task_id = serializers.CharField(max_length=64, required=False)
    station_id = serializers.CharField(max_length=32, required=False)
    device_id = serializers.CharField(max_length=64, required=False)
    
    occurred_at = serializers.DateTimeField(required=False)
    acknowledged_at = serializers.DateTimeField(required=False)
    resolved_at = serializers.DateTimeField(required=False)
    
    metadata = serializers.JSONField(required=False)
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ReportSerializer(PlatformSerializer):
    """报告序列化器"""
    report_id = serializers.CharField(max_length=64)
    task_id = serializers.CharField(max_length=64)
    report_name = serializers.CharField(max_length=128)
    status = serializers.CharField(max_length=16)
    result = serializers.CharField(max_length=16)
    
    test_records = serializers.JSONField(required=False)
    metrics = serializers.JSONField(required=False)
    
    generated_at = serializers.DateTimeField(required=False)
    
    metadata = serializers.JSONField(required=False)
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class PaginatedResponseSerializer(serializers.Serializer):
    """分页响应序列化器"""
    count = serializers.IntegerField()
    next = serializers.URLField(required=False)
    previous = serializers.URLField(required=False)
    results = serializers.ListField()


class ErrorResponseSerializer(serializers.Serializer):
    """错误响应序列化器"""
    code = serializers.IntegerField()
    message = serializers.CharField()
    details = serializers.DictField(required=False)


class SuccessResponseSerializer(serializers.Serializer):
    """成功响应序列化器"""
    code = serializers.IntegerField(default=2000)
    message = serializers.CharField(default='success')
    data = serializers.DictField(required=False)
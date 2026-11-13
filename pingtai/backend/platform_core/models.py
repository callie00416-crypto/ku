"""
平台Django模型 - Platform Django Models

【职责】
提供工业平台的通用Django ORM模型
基于平台领域模型创建数据库表

【设计原则】
- 与领域模型解耦
- 适合数据库优化
- 支持工业大数据量
- 符合Django ORM规范
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json
from typing import Dict, Any, Optional


class TimeStampedModel(models.Model):
    """时间戳模型基类"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    class Meta:
        abstract = True


class PlatformDevice(TimeStampedModel):
    """平台设备模型"""
    
    DEVICE_TYPE_CHOICES = [
        ('encoder', '编码器'),
        ('motor', '电机'),
        ('power_supply', '电源'),
        ('plc', 'PLC'),
        ('camera', '相机'),
        ('daq', '数据采集'),
        ('unknown', '未知'),
    ]
    
    STATUS_CHOICES = [
        ('offline', '离线'),
        ('online', '在线'),
        ('running', '运行中'),
        ('error', '错误'),
        ('maintenance', '维护中'),
    ]
    
    device_id = models.CharField(max_length=64, unique=True, db_index=True)
    device_name = models.CharField(max_length=128, blank=True, null=True)
    device_type = models.CharField(max_length=32, choices=DEVICE_TYPE_CHOICES, db_index=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='offline', db_index=True)
    
    station_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    protocol = models.CharField(max_length=32, blank=True, null=True)
    
    is_connected = models.BooleanField(default=False, db_index=True)
    is_busy = models.BooleanField(default=False)
    is_heartbeat_alive = models.BooleanField(default=False)
    
    config = models.JSONField(default=dict, blank=True)
    metrics = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    last_heartbeat = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'platform_devices'
        verbose_name = '平台设备'
        verbose_name_plural = '平台设备'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device_id']),
            models.Index(fields=['device_type']),
            models.Index(fields=['status']),
            models.Index(fields=['station_id']),
            models.Index(fields=['is_connected']),
        ]
    
    def __str__(self):
        return f"{self.device_id} - {self.device_name or self.device_type}"


class PlatformTask(TimeStampedModel):
    """平台任务模型"""
    
    TASK_TYPE_CHOICES = [
        ('test', '测试'),
        ('calibration', '校准'),
        ('maintenance', '维护'),
        ('diagnosis', '诊断'),
        ('unknown', '未知'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', '低'),
        ('normal', '正常'),
        ('high', '高'),
        ('critical', '紧急'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('running', '运行中'),
        ('paused', '已暂停'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]
    
    RESULT_CHOICES = [
        ('pass', '通过'),
        ('fail', '失败'),
        ('unknown', '未知'),
    ]
    
    task_id = models.CharField(max_length=64, unique=True, db_index=True)
    task_name = models.CharField(max_length=128)
    task_type = models.CharField(max_length=32, choices=TASK_TYPE_CHOICES, db_index=True)
    station_id = models.CharField(max_length=64, db_index=True)
    
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending', db_index=True)
    result = models.CharField(max_length=16, choices=RESULT_CHOICES, blank=True, null=True, db_index=True)
    
    workorder_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    device_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    sn = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    
    progress = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    
    error_code = models.CharField(max_length=32, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    retry_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    max_retries = models.IntegerField(default=3, validators=[MinValueValidator(0)])
    actor_id = models.CharField(max_length=64, blank=True, null=True)
    
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    duration_ms = models.IntegerField(blank=True, null=True)
    
    metrics = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'platform_tasks'
        verbose_name = '平台任务'
        verbose_name_plural = '平台任务'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task_id']),
            models.Index(fields=['task_type']),
            models.Index(fields=['station_id']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['result']),
            models.Index(fields=['workorder_id']),
            models.Index(fields=['device_id']),
            models.Index(fields=['sn']),
        ]
    
    def __str__(self):
        return f"{self.task_id} - {self.task_name}"


class PlatformStation(TimeStampedModel):
    """平台工位模型"""
    
    STATION_TYPE_CHOICES = [
        ('test', '测试工位'),
        ('assembly', '装配工位'),
        ('packaging', '包装工位'),
        ('inspection', '检测工位'),
        ('unknown', '未知'),
    ]
    
    STATUS_CHOICES = [
        ('idle', '空闲'),
        ('running', '运行中'),
        ('paused', '已暂停'),
        ('error', '错误'),
        ('maintenance', '维护中'),
        ('offline', '离线'),
    ]
    
    MODE_CHOICES = [
        ('manual', '手动'),
        ('auto', '自动'),
        ('semi_auto', '半自动'),
    ]
    
    station_id = models.CharField(max_length=64, unique=True, db_index=True)
    station_code = models.CharField(max_length=64, unique=True)
    station_name = models.CharField(max_length=128)
    station_type = models.CharField(max_length=32, choices=STATION_TYPE_CHOICES, db_index=True)
    
    line_code = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    area_code = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='idle', db_index=True)
    mode = models.CharField(max_length=16, choices=MODE_CHOICES, default='manual')
    
    current_task_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    is_enabled = models.BooleanField(default=True, db_index=True)
    
    resource_state = models.JSONField(default=dict, blank=True)
    alarm_state = models.JSONField(default=dict, blank=True)
    mounted_devices = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'platform_stations'
        verbose_name = '平台工位'
        verbose_name_plural = '平台工位'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['station_id']),
            models.Index(fields=['station_code']),
            models.Index(fields=['station_type']),
            models.Index(fields=['status']),
            models.Index(fields=['line_code']),
            models.Index(fields=['area_code']),
            models.Index(fields=['current_task_id']),
            models.Index(fields=['is_enabled']),
        ]
    
    def __str__(self):
        return f"{self.station_id} - {self.station_name}"


class PlatformAlarm(TimeStampedModel):
    """平台告警模型"""
    
    ALARM_LEVEL_CHOICES = [
        ('info', '信息'),
        ('warning', '警告'),
        ('error', '错误'),
        ('critical', '严重'),
        ('fatal', '致命'),
    ]
    
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('acknowledged', '已确认'),
        ('resolved', '已解决'),
        ('closed', '已关闭'),
    ]
    
    alarm_id = models.CharField(max_length=64, unique=True, db_index=True)
    alarm_code = models.CharField(max_length=64, db_index=True)
    alarm_level = models.CharField(max_length=16, choices=ALARM_LEVEL_CHOICES, db_index=True)
    message = models.TextField()
    
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='active', db_index=True)
    
    task_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    station_id = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    device_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    workorder_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    
    occurred_at = models.DateTimeField(db_index=True)
    acknowledged_at = models.DateTimeField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'platform_alarms'
        verbose_name = '平台告警'
        verbose_name_plural = '平台告警'
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['alarm_id']),
            models.Index(fields=['alarm_code']),
            models.Index(fields=['alarm_level']),
            models.Index(fields=['status']),
            models.Index(fields=['occurred_at']),
            models.Index(fields=['task_id']),
            models.Index(fields=['station_id']),
            models.Index(fields=['device_id']),
            models.Index(fields=['workorder_id']),
        ]
    
    def __str__(self):
        return f"{self.alarm_id} - {self.alarm_code} - {self.alarm_level}"


class PlatformReport(TimeStampedModel):
    """平台报告模型"""
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('generated', '已生成'),
        ('archived', '已归档'),
    ]
    
    RESULT_CHOICES = [
        ('pass', '通过'),
        ('fail', '失败'),
        ('unknown', '未知'),
    ]
    
    report_id = models.CharField(max_length=64, unique=True, db_index=True)
    task_id = models.CharField(max_length=64, db_index=True)
    report_name = models.CharField(max_length=128)
    
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft', db_index=True)
    result = models.CharField(max_length=16, choices=RESULT_CHOICES, blank=True, null=True, db_index=True)
    
    workorder_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    sn = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    
    task_snapshot = models.JSONField(default=dict, blank=True)
    station_snapshot = models.JSONField(default=dict, blank=True)
    device_snapshots = models.JSONField(default=list, blank=True)
    test_records = models.JSONField(default=list, blank=True)
    alarm_snapshots = models.JSONField(default=list, blank=True)
    
    software_version = models.JSONField(default=dict, blank=True)
    operator_info = models.JSONField(default=dict, blank=True)
    
    generated_at = models.DateTimeField(blank=True, null=True)
    archived_at = models.DateTimeField(blank=True, null=True)
    
    metrics = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'platform_reports'
        verbose_name = '平台报告'
        verbose_name_plural = '平台报告'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_id']),
            models.Index(fields=['task_id']),
            models.Index(fields=['status']),
            models.Index(fields=['result']),
            models.Index(fields=['workorder_id']),
            models.Index(fields=['sn']),
        ]
    
    def __str__(self):
        return f"{self.report_id} - {self.report_name}"


class PlatformWorkOrder(TimeStampedModel):
    """平台工单模型"""
    
    STATUS_CHOICES = [
        ('PENDING', '待处理'),
        ('RUNNING', '进行中'),
        ('COMPLETED', '已完成'),
        ('CANCELLED', '已取消'),
        ('PAUSED', '已暂停'),
    ]
    
    workorder_id = models.CharField(max_length=64, unique=True, db_index=True)
    product_model = models.CharField(max_length=128, db_index=True)
    batch_number = models.CharField(max_length=64, db_index=True)
    
    planned_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    completed_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    ng_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    route_config = models.JSONField(default=dict, blank=True)
    priority = models.IntegerField(default=0, validators=[MinValueValidator(0)], db_index=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'platform_work_orders'
        verbose_name = '平台工单'
        verbose_name_plural = '平台工单'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workorder_id']),
            models.Index(fields=['product_model']),
            models.Index(fields=['batch_number']),
            models.Index(fields=['priority']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.workorder_id} - {self.product_model} - {self.batch_number}"
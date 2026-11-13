"""
存储模型 - ORM实体定义

【职责】
- 定义数据库表结构
- ORM实体映射
- 数据持久化基础

【设计原则】
- 与领域模型解耦
- 适合数据库优化
- 支持工业大数据量
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TaskModel(Base):
    """任务模型（ORM实体）"""
    __tablename__ = 'tasks'

    id = Column(String(64), primary_key=True, index=True)
    task_id = Column(String(64), unique=True, nullable=False, index=True)  # 业务ID
    workorder_id = Column(String(64), index=True)  # 工单ID
    station_id = Column(Integer, index=True)  # 工位ID
    device_id = Column(String(64), index=True)  # 设备ID
    sn = Column(String(128), index=True)  # 产品序列号
    
    task_type = Column(String(32), nullable=False)  # 任务类型
    priority = Column(String(16), default='normal')  # 优先级
    status = Column(String(32), default='pending', index=True)  # 任务状态
    result = Column(String(16), index=True)  # 任务结果
    error_code = Column(String(32))  # 错误码
    error_message = Column(Text)  # 错误消息
    
    retry_count = Column(Integer, default=0)  # 重试次数
    max_retries = Column(Integer, default=3)  # 最大重试次数
    actor_id = Column(String(64))  # 执行者ID
    
    start_time = Column(DateTime)  # 开始时间
    end_time = Column(DateTime)  # 结束时间
    duration_ms = Column(Integer)  # 持续毫秒数
    
    metrics = Column(JSON)  # 任务指标
    extra_metadata = Column(JSON)  # 额外元数据（注意：metadata是SQLAlchemy保留字）
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=0)  # 乐观锁版本


class ReportModel(Base):
    """报告模型（ORM实体）"""
    __tablename__ = 'reports'

    id = Column(String(64), primary_key=True, index=True)
    report_id = Column(String(64), unique=True, nullable=False, index=True)  # 报告ID
    task_id = Column(String(64), index=True)  # 关联任务ID
    workorder_id = Column(String(64), index=True)  # 工单ID
    sn = Column(String(128), index=True)  # 产品序列号
    
    status = Column(String(32), default='draft', index=True)  # 报告状态
    result = Column(String(16), index=True)  # 报告结果
    
    # 报告内容（JSON格式存储快照数据）
    task_snapshot = Column(JSON)  # 任务快照
    station_snapshot = Column(JSON)  # 工位快照
    device_snapshots = Column(JSON)  # 设备快照列表
    test_records = Column(JSON)  # 测试记录列表
    alarm_snapshots = Column(JSON)  # 告警快照列表
    
    # 软件版本信息
    software_version = Column(JSON)
    # 操作员信息
    operator_info = Column(JSON)
    
    # 时间信息
    generated_at = Column(DateTime)  # 生成时间
    archived_at = Column(DateTime)  # 归档时间
    
    # 指标
    metrics = Column(JSON)  # 报告指标
    
    # 附加信息
    extra_metadata = Column(JSON)  # 额外元数据（注意：metadata是SQLAlchemy保留字）
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=0)  # 乐观锁版本


class AlarmModel(Base):
    """告警模型（ORM实体）"""
    __tablename__ = 'alarms'

    id = Column(String(64), primary_key=True, index=True)
    alarm_id = Column(String(64), unique=True, nullable=False, index=True)  # 告警ID
    alarm_code = Column(String(64), index=True)  # 告警代码
    alarm_level = Column(String(16), index=True)  # 告警级别
    message = Column(Text)  # 告警消息
    
    status = Column(String(16), default='active', index=True)  # 告警状态
    
    # 时间信息
    occurred_at = Column(DateTime, index=True)  # 发生时间
    acknowledged_at = Column(DateTime, index=True)  # 确认时间
    resolved_at = Column(DateTime, index=True)  # 解决时间
    closed_at = Column(DateTime, index=True)  # 关闭时间
    
    # 关联信息
    task_id = Column(String(64), index=True)  # 关联任务
    station_id = Column(String(32), index=True)  # 关联工位
    device_id = Column(String(64), index=True)  # 关联设备
    workorder_id = Column(String(64), index=True)  # 关联工单
    
    # 额外元数据
    extra_metadata = Column(JSON)  # 额外元数据（注意：metadata是SQLAlchemy保留字）
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=0)  # 乐观锁版本


class StationModel(Base):
    """工位模型（ORM实体）"""
    __tablename__ = 'stations'

    id = Column(String(64), primary_key=True, index=True)
    station_id = Column(String(64), unique=True, nullable=False, index=True)  # 工位ID
    code = Column(String(64), unique=True, nullable=False)  # 工位代码
    name = Column(String(128))  # 工位名称
    line_code = Column(String(32), index=True)  # 生产线代码
    area_code = Column(String(32), index=True)  # 区域代码
    
    status = Column(String(16), default='idle', index=True)  # 工位状态
    mode = Column(String(16), default='manual')  # 运行模式
    
    current_task_id = Column(String(64), index=True)  # 当前任务ID
    is_enabled = Column(Boolean, default=True)  # 是否启用
    
    # 资源状态
    resource_state = Column(JSON)  # 资源状态（CPU、内存、磁盘等）
    alarm_state = Column(JSON)  # 告警状态
    mounted_devices = Column(JSON)  # 挂载的设备列表
    
    # 额外元数据
    extra_metadata = Column(JSON)  # 额外元数据（注意：metadata是SQLAlchemy保留字）
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=0)  # 乐观锁版本


class DeviceModel(Base):
    """设备模型（ORM实体）"""
    __tablename__ = 'devices'

    id = Column(String(64), primary_key=True, index=True)
    device_id = Column(String(64), unique=True, nullable=False, index=True)  # 设备ID
    station_id = Column(String(64), index=True)  # 所属工位
    code = Column(String(64), unique=True, nullable=False)  # 设备代码
    name = Column(String(128))  # 设备名称
    device_type = Column(String(32), index=True)  # 设备类型
    protocol = Column(String(32))  # 通信协议
    
    connect_status = Column(String(16), default='disconnected', index=True)  # 连接状态
    status = Column(String(16), default='idle', index=True)  # 设备状态
    
    is_connected = Column(Boolean, default=False)  # 是否连接
    is_busy = Column(Boolean, default=False)  # 是否忙碌
    is_heartbeat_alive = Column(Boolean, default=False)  # 心跳是否存活
    
    # 配置和指标
    config = Column(JSON)  # 设备配置
    metrics = Column(JSON)  # 设备指标
    calibration_info = Column(JSON)  # 校准信息
    
    # 时间信息
    last_heartbeat = Column(DateTime)  # 最后心跳时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 额外元数据
    extra_metadata = Column(JSON)  # 额外元数据（注意：metadata是SQLAlchemy保留字）
    
    version = Column(Integer, default=0)  # 乐观锁版本


class TestRecordModel(Base):
    """测试记录模型（独立表，支持大数据量）"""
    __tablename__ = 'test_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(String(64), unique=True, nullable=False, index=True)  # 记录ID
    report_id = Column(String(64), index=True)  # 所属报告ID
    
    step = Column(Integer)  # 步骤序号
    name = Column(String(128))  # 测试项名称
    value_type = Column(String(16))  # 值类型
    value_raw = Column(Text)  # 原始值
    expected = Column(Text)  # 期望值
    tolerance = Column(Text)  # 容差
    is_pass = Column(Boolean)  # 是否通过
    
    timestamp = Column(DateTime)  # 时间戳
    extra_metadata = Column(JSON)  # 额外元数据（注意：metadata是SQLAlchemy保留字）
    
    created_at = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=0)  # 乐观锁版本


class ReportAttachmentModel(Base):
    """报告附件模型（独立表，支持大文件）"""
    __tablename__ = 'report_attachments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    attachment_id = Column(String(64), unique=True, nullable=False, index=True)  # 附件ID
    report_id = Column(String(64), index=True)  # 所属报告ID
    
    type = Column(String(64))  # 文件类型
    filename = Column(String(256))  # 文件名
    file_path = Column(String(512))  # 文件路径
    file_size = Column(Integer)  # 文件大小
    checksum = Column(String(64))  # 校验和
    
    description = Column(Text)  # 描述
    upload_time = Column(DateTime)  # 上传时间
    
    created_at = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=0)  # 乐观锁版本


class WorkOrderModel(Base):
    """工单模型（ORM实体）"""
    __tablename__ = 'work_orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workorder_id = Column(String(64), unique=True, nullable=False, index=True)  # 工单ID
    product_model = Column(String(128), nullable=False)  # 产品型号
    batch_number = Column(String(64), index=True)  # 批次号
    
    planned_quantity = Column(Integer, default=0)  # 计划数量
    completed_quantity = Column(Integer, default=0)  # 完成数量
    ng_quantity = Column(Integer, default=0)  # NG数量
    
    route_config = Column(JSON)  # 工艺路线配置
    priority = Column(Integer, default=0, index=True)  # 优先级
    status = Column(String(32), default='PENDING', index=True)  # 状态
    
    start_time = Column(DateTime)  # 开始时间
    end_time = Column(DateTime)  # 结束时间
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=0)  # 乐观锁版本
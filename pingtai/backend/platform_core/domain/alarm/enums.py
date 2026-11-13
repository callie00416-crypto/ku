"""
告警领域枚举 - Alarm Domain Enums

【职责】
- 定义告警相关枚举类型
- 保证类型安全
- 提供业务语义

【设计原则】
- 枚举值一旦确定不再变更
- 每个枚举都有明确的业务含义
- 支持扩展但不破坏现有逻辑
"""
from enum import Enum


class AlarmLevel(Enum):
    """告警等级
    
    【分级原则】
    - FATAL: 系统崩溃级
    - ERROR: 业务中断级
    - WARN: 潜在风险级
    - INFO: 信息提示级
    
    【重要】
    - 等级不可随意扩展
    - 现场90%告警集中在ERROR/WARN
    - INFO用于关键节点记录
    """
    FATAL = "fatal"      # 系统崩溃
    ERROR = "error"      # 业务错误
    WARN = "warn"        # 警告
    INFO = "info"        # 信息


class AlarmStatus(Enum):
    """告警状态
    
    【生命周期】
    - ACTIVE: 激活中（刚触发）
    - ACKED: 已确认（运维已看到）
    - RESOLVED: 已解决（问题已修复）
    - CLOSED: 已关闭（归档完成）
    
    【重要】
    - 必须支持完整的生命周期
    - 否则现场告警系统会瘫痪
    """
    ACTIVE = "active"      # 激活
    ACKED = "acked"        # 已确认
    RESOLVED = "resolved"  # 已解决
    CLOSED = "closed"      # 已关闭
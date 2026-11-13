"""
工业平台内核 - Platform Kernel

【职责】
工业Runtime平台核心层
提供通用、稳定、长期不变的平台能力

【包含】
- runtime: Runtime、EventBus、Actor、Snapshot、Health
- domain: DDD领域模型（通用抽象）
- storage: CQRS存储、Repository
- application: 通用应用服务
- api: 平台API

【设计原则】
- 通用
- 稳定
- 长期不变
- 不包含项目业务

【禁止】
- 编码器业务
- AOI业务
- 特定设备逻辑
- 特定工艺逻辑
"""

__version__ = "1.0.0"
__platform_name__ = "Industrial Automation Platform"
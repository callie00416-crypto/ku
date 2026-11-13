"""
Runtime层 - Runtime Layer

【职责】
工业Runtime核心
提供运行时事件发布订阅、Actor模型、快照恢复、健康监控

【包含】
- actor: Actor模型、Mailbox、消息队列
- event_bus: 事件总线
- snapshot: 快照系统
- health: 健康监控

【设计原则】
- 零阻塞
- 零IO
- 零数据库操作

【禁止】
- ORM
- MySQL
- Django Model
- 工艺规则
- 工单逻辑
"""
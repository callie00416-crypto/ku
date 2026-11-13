"""
Application层 - Application Layer

【职责】
通用应用服务
提供流程编排、Handler、Repository调用、事务协调

【允许】
- 流程编排
- Handler
- Repository调用
- 事务协调
- 调用Domain
- 调用Repository Interface

【禁止】
- 业务规则
- 状态机
- 工艺if-else
- 超长Service

【设计原则】
Application层禁止膨胀
"""
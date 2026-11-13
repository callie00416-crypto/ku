"""
Storage层 - Storage Layer

【职责】
CQRS存储、Repository实现
提供数据持久化、查询、迁移能力

【包含】
- models: 数据模型
- repositories: Repository实现
- mappers: 对象映射
- query_services: 查询服务
- migrations: 数据库迁移

【允许】
- SQLAlchemy
- MySQL
- CRUD
- Query

【禁止】
- Runtime逻辑
- 工艺逻辑
- 状态机
- 业务规则
"""
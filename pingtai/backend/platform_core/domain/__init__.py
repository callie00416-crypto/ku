"""
Domain层 - Domain Layer

【职责】
DDD领域模型（通用抽象）
提供设备、任务、工位、告警、报告等通用领域模型

【包含】
- common: AggregateRoot、StateMachine、Enums
- device: 通用设备抽象
- task: 通用任务抽象
- station: 通用工位抽象
- alarm: 通用告警抽象
- report: 通用报告抽象

【设计原则】
- 纯Python
- 无框架依赖
- 无数据库依赖
- 无ORM

【禁止】
import django
import sqlalchemy
import pymysql
"""
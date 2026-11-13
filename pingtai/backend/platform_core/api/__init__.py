"""
平台API层 - Platform API Layer

【职责】
提供工业平台的通用API基础设施
包含通用视图基类、序列化器、URL路由

【包含】
- views: 通用视图基类
- serializers: 通用序列化器
- urls: 通用URL路由

【设计原则】
- 通用
- 可扩展
- 符合RESTful规范

【禁止】
- 项目特定业务逻辑
- 编码器特定逻辑
- 工艺特定逻辑
"""
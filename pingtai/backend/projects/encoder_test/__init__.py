"""
编码器测试项目 - Encoder Test Project

【职责】
编码器测试业务实现
包含编码器/电机/电源的特定动作、驱动、测试用例

【包含】
- actions: 编码器/电机/电源动作
- drivers: 编码器/电机/电源驱动
- core: 测试引擎、测试用例
- adapters: 平台适配层
- configs: 编码器测试配置
- flows: 编码器测试流程
- api: Django API 视图
- models: Django 数据模型
- serializers: Django 序列化器
- views: Django 视图
- tasks: Celery 任务
- management: Django 管理命令
- migrations: 数据库迁移
- utils: 工具函数

【设计原则】
- 工艺实现
- 设备组合
- 测试流程
- 业务配置

【禁止】
- 修改平台内核
- 修改DDD核心规则
- 修改Runtime机制
"""

default_app_config = 'projects.encoder_test.apps.EncoderTestConfig'
"""
共享层模块 - Shared Module

【职责】
可跨项目复用能力
提供通用的驱动、工具、日志系统

【包含】
- drivers: 可复用的驱动
  - base: BaseComm、BaseProtocol、BaseDevice
  - comm: RS485、TCP、CAN
  - protocol: Modbus、SCPI
- utils: 工具函数
- logging: 日志系统

【设计原则】
- 可复用
- 通用
- 稳定

【禁止】
- 业务层逻辑
- 工单逻辑
- 测试逻辑
- Runtime逻辑
"""
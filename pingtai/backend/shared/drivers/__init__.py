"""
共享驱动层 - Shared Drivers

【职责】
可复用的驱动层
提供BaseComm、BaseProtocol、BaseDevice等通用驱动接口

【包含】
- base: BaseComm、BaseProtocol、BaseDevice、BaseSDK、BaseAction
- comm: RS485、TCP、CAN、USB
- protocol: Modbus RTU、Modbus TCP、SCPI、CANopen、EtherCAT

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
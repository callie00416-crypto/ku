"""
Protocol 层 - 协议层

职责：协议封装、CRC、帧解析、寄存器读写

禁止：
- 处理设备业务逻辑
- 直接操作串口/socket
"""
from .modbus_rtu import ModbusDriver

__all__ = ['ModbusDriver']
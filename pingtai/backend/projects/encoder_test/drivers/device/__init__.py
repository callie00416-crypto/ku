"""
Device 层 - 设备层

职责：表达设备业务能力（set_voltage/move_to/read_angle 等）

禁止：
- 直接操作串口/socket
- 处理协议帧
"""
from .power_supply.power_supply import PowerSupply

__all__ = ['PowerSupply']
"""
Comm 层 - 通讯层

职责：只负责字节传输（open/close/send/recv）

禁止：
- 处理设备业务逻辑
- 处理协议帧
"""
from .rs485_comm import RS485Comm
from .tcp_comm import TCPComm
from .can_comm import CANComm

__all__ = ['RS485Comm', 'TCPComm', 'CANComm']
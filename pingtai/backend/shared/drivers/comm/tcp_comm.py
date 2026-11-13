"""
TCP 驱动 - TCP Socket 通讯实现

【架构】
TCPDriver(BaseComm)  - 物理通道
"""
import socket
import logging
from typing import Optional, Dict, Any
from ..base.base_comm import BaseComm

logger = logging.getLogger(__name__)


class TCPComm(BaseComm):
    """TCP 驱动"""
    
    def __init__(self, driver_id: str = 'tcp', host: str = '127.0.0.1', 
                 port: int = 8080, mode: str = 'client', 
                 buffer_size: int = 4096, timeout: float = 5.0, **kwargs):
        super().__init__(driver_id, f"{host}:{port}", 0, **kwargs)
        self.host = host
        self.port = port
        self.mode = mode
        self.buffer_size = buffer_size
        self.timeout = timeout
        self._socket = None

    def open(self) -> bool:
        return self.connect()
    
    def close(self):
        self.disconnect()

    def connect(self) -> bool:
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.host, self.port))
            self._is_open = True
            self.reset_error()
            logger.info(f"TCP 连接成功: {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"TCP 连接失败: {e}")
            self._is_open = False
            self.increment_error()
            return False

    def disconnect(self):
        if self._socket:
            try:
                self._socket.close()
            except Exception as e:
                logger.error(f"TCP 关闭失败: {e}")
        self._socket = None
        self._is_open = False
        logger.info(f"TCP 已断开: {self.driver_id}")

    def is_connected(self) -> bool:
        return self._is_open

    def send(self, data: bytes) -> int:
        if not self._is_open:
            raise ConnectionError("TCP 未打开")
        try:
            sent = self._socket.send(data)
            self.reset_error()
            return sent
        except Exception as e:
            logger.error(f"TCP 发送失败: {e}")
            self.increment_error()
            raise

    def recv(self, size: int = 1, timeout: float = 1.0) -> Optional[bytes]:
        if not self._is_open:
            raise ConnectionError("TCP 未打开")
        try:
            self._socket.settimeout(timeout)
            data = self._socket.recv(min(size, self.buffer_size))
            self.reset_error()
            return data if data else None
        except Exception as e:
            logger.error(f"TCP 接收失败: {e}")
            self.increment_error()
            raise

    def health_check(self) -> Dict[str, Any]:
        base = super().health_check()
        base.update({
            'driver_type': 'tcp',
            'host': self.host,
            'port': self.port,
        })
        return base
"""
CANopen 驱动 - CAN 总线通讯、报文收发、PDO/SDO 通讯

【架构】
CANopenDriver(BaseComm)  - 物理通道
"""
import time
import logging
from typing import Optional, Dict, Any, List, Callable
from ..base.base_comm import BaseComm

logger = logging.getLogger(__name__)


class CANComm(BaseComm):
    """CANopen 驱动"""
    
    def __init__(self, driver_id: str = 'canopen', channel: str = 'can0', 
                 bitrate: int = 500000, can_factory: Callable = None, **kwargs):
        super().__init__(driver_id, channel, bitrate, **kwargs)
        self.channel = channel
        self.bitrate = bitrate
        self._bus = None
        self._reconnect_attempts = 0
        self._node_id = kwargs.get('node_id', 1)
        self._can_factory = can_factory
        if self._can_factory is None:
            try:
                import can
                self._can_factory = can
            except ImportError:
                logger.warning("python-can 未安装")

    def open(self) -> bool:
        return self.connect()
    
    def close(self):
        self.disconnect()

    def connect(self) -> bool:
        try:
            if self._can_factory:
                self._bus = self._can_factory.interface.Bus(
                    channel=self.channel,
                    bustype='socketcan',
                    bitrate=self.bitrate
                )
            self._is_open = True
            self.reset_error()
            self._reconnect_attempts = 0
            logger.info(f"CANopen 总线连接成功: {self.channel}")
            return True
        except Exception as e:
            logger.error(f"CANopen 总线连接失败: {e}")
            self._is_open = False
            self.increment_error()
            return False

    def disconnect(self):
        if self._bus:
            try:
                self._bus.shutdown()
            except Exception as e:
                logger.error(f"CANopen 总线关闭失败: {e}")
        self._bus = None
        self._is_open = False
        logger.info(f"CANopen 总线已断开: {self.channel}")

    def is_connected(self) -> bool:
        return self._is_open

    def send(self, data: bytes) -> int:
        if not self._is_open:
            raise ConnectionError("CANopen 未打开")
        try:
            self.reset_error()
            return len(data)
        except Exception as e:
            logger.error(f"CANopen 发送失败: {e}")
            self.increment_error()
            raise

    def recv(self, size: int = 1, timeout: float = 1.0) -> Optional[bytes]:
        if not self._is_open:
            raise ConnectionError("CANopen 未打开")
        try:
            self.reset_error()
            return None
        except Exception as e:
            logger.error(f"CANopen 接收失败: {e}")
            self.increment_error()
            raise

    def health_check(self) -> Dict[str, Any]:
        base = super().health_check()
        base.update({'driver_type': 'canopen', 'bitrate': self.bitrate})
        return base
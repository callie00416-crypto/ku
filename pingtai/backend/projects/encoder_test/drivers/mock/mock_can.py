"""
Mock CAN 驱动 - 模拟 CAN 总线通讯

【架构】
MockCAN(BaseComm) - 继承自 BaseComm，模拟 CAN 总线通信

支持：
- 报文收发
- 总线错误模拟
- 离线模式模拟
- 队列式消息管理
"""
import logging
from typing import Dict, Any, List, Optional
from shared.drivers.base.base_comm import BaseComm

logger = logging.getLogger(__name__)


class MockCAN(BaseComm):
    """Mock CAN 驱动"""
    
    def __init__(self, driver_id: str = 'mock_can', channel: str = 'can0', 
                 bitrate: int = 500000, mode: str = 'normal', **kwargs):
        """
        初始化 Mock CAN 驱动
        
        Args:
            driver_id: 驱动唯一标识
            channel: CAN 通道，如 'can0', 'can1'
            bitrate: 波特率，常用 250000, 500000, 1000000
            mode: 工作模式
                - normal: 正常模式
                - bus_error: 总线错误模式（发送/接收时抛出异常）
                - offline: 离线模式（无法连接）
            **kwargs: 其他配置参数
        """
        super().__init__(driver_id, channel, bitrate, **kwargs)
        self.channel = channel
        self.bitrate = bitrate
        self.mode = mode
        self._messages: List[Dict[str, Any]] = []
    
    def open(self) -> bool:
        """打开 CAN 总线"""
        return self.connect()
    
    def close(self):
        """关闭 CAN 总线"""
        self.disconnect()
    
    def connect(self) -> bool:
        """连接 CAN 总线"""
        if self.mode == 'offline':
            logger.warning(f"Mock CAN 无法连接（离线模式）: {self.channel}")
            self._is_open = False
            return False
        
        logger.info(f"Mock CAN 已连接: {self.channel} @ {self.bitrate}bps")
        self._is_open = True
        return True
    
    def disconnect(self):
        """断开连接"""
        logger.info(f"Mock CAN 已断开: {self.channel}")
        self._is_open = False
        self._messages.clear()
    
    def send(self, data: bytes) -> int:
        """
        发送 CAN 报文
        
        Args:
            data: 要发送的数据
            
        Returns:
            发送的字节数
            
        Raises:
            ConnectionError: CAN 总线未连接时
            RuntimeError: 总线错误模式时
        """
        if not self._is_open:
            raise ConnectionError("CAN 总线未连接")
        
        if self.mode == 'bus_error':
            raise RuntimeError("CAN 总线错误")
        
        self._messages.append({'data': data, 'timestamp': time.time()})
        logger.debug(f"Mock CAN 发送数据: {len(data)} 字节 -> {data.hex()}")
        return len(data)
    
    def recv(self, size: int = 1, timeout: float = 1.0) -> Optional[bytes]:
        """
        接收 CAN 报文
        
        Args:
            size: 期望接收的字节数（当前实现忽略此参数）
            timeout: 超时时间（秒）
            
        Returns:
            接收到的数据，超时返回 None
            
        Raises:
            ConnectionError: CAN 总线未连接时
            RuntimeError: 总线错误模式时
        """
        if not self._is_open:
            raise ConnectionError("CAN 总线未连接")
        
        if self.mode == 'bus_error':
            raise RuntimeError("CAN 总线错误")
        
        if not self._messages:
            return None
        
        msg = self._messages.pop(0)
        logger.debug(f"Mock CAN 接收数据: {len(msg['data'])} 字节 -> {msg['data'].hex()}")
        return msg.get('data')
    
    def send_recv(self, message: bytes, timeout: float = 1.0) -> Optional[bytes]:
        """
        发送并接收响应
        
        Args:
            message: 要发送的数据
            timeout: 超时时间（秒）
            
        Returns:
            模拟的 PDO 响应数据
            
        Raises:
            ConnectionError: CAN 总线未连接时
            RuntimeError: 总线错误模式时
        """
        if not self._is_open:
            raise ConnectionError("CAN 总线未连接")
        
        if self.mode == 'bus_error':
            raise RuntimeError("CAN 总线错误")
        
        self.send(message)
        return b'\x00\x00\x00\x00'  # 模拟 PDO 响应
    
    def set_mode(self, mode: str):
        """
        设置模拟模式
        
        Args:
            mode: 模式名称
                - normal: 正常模式
                - bus_error: 总线错误模式
                - offline: 离线模式
                
        Raises:
            ValueError: 无效模式时
        """
        if mode not in ['normal', 'bus_error', 'offline']:
            raise ValueError("模式必须是: normal, bus_error, offline")
        self.mode = mode
        logger.info(f"Mock CAN 模式已切换为: {mode}")
    
    def queue_message(self, data: bytes):
        """
        队列式添加消息
        
        Args:
            data: 要添加的消息数据
        """
        self._messages.append({'data': data, 'timestamp': time.time()})
        logger.debug(f"Mock CAN 队列消息: {len(data)} 字节")
    
    def clear_messages(self):
        """清空消息队列"""
        self._messages.clear()
        logger.debug("Mock CAN 消息队列已清空")
    
    def health_check(self):
        """健康检查"""
        base = super().health_check()
        base.update({
            'channel': self.channel,
            'bitrate': self.bitrate,
            'mode': self.mode,
            'message_count': len(self._messages),
            'mock': True
        })
        return base


import time  # 需要在类定义后导入，避免循环导入问题
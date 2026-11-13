"""
Mock 串口驱动 - 用于测试的模拟串口

【架构】
MockSerial(BaseComm) - 继承自 BaseComm，模拟串口通信
"""
import time
import logging
from typing import Optional, List
from shared.drivers.base.base_comm import BaseComm

logger = logging.getLogger(__name__)


class MockSerial(BaseComm):
    """Mock 串口驱动
    
    用于测试环境，模拟真实的串口通信
    
    支持：
    - 发送/接收数据
    - 自动响应模式
    - 响应延迟模拟
    - 队列式响应
    """
    
    def __init__(self, driver_id: str = 'mock_serial', 
                 port: str = 'COM3', 
                 baudrate: int = 9600,
                 **kwargs):
        """
        初始化 Mock 串口驱动
        
        Args:
            driver_id: 驱动唯一标识
            port: 串口号
            baudrate: 波特率
            **kwargs: 其他配置参数
                - mock_response_delay: 模拟响应延迟（秒），默认 0.01
                - auto_response: 自动响应数据
        """
        super().__init__(driver_id, port, baudrate, **kwargs)
        self._send_buffer: bytes = b''
        self._recv_buffer: List[bytes] = []
        self._mock_response_delay = kwargs.get('mock_response_delay', 0.01)
        self._auto_response: Optional[bytes] = kwargs.get('auto_response', None)
    
    def open(self) -> bool:
        """打开串口"""
        try:
            logger.info(f"Mock 串口已打开: {self.port} @ {self.baudrate}bps")
            self._is_open = True
            return True
        except Exception as e:
            logger.error(f"Mock 串口打开失败: {e}")
            self.increment_error()
            return False
    
    def close(self):
        """关闭串口"""
        try:
            logger.info(f"Mock 串口已关闭: {self.port}")
            self._is_open = False
            self._send_buffer = b''
            self._recv_buffer.clear()
        except Exception as e:
            logger.error(f"Mock 串口关闭失败: {e}")
            self.increment_error()
    
    def send(self, data: bytes) -> int:
        """
        发送数据
        
        Args:
            data: 要发送的数据
            
        Returns:
            发送的字节数
            
        Raises:
            ConnectionError: 串口未打开时
        """
        if not self._is_open:
            raise ConnectionError(f"串口未打开: {self.port}")
        
        try:
            self._send_buffer = data
            logger.debug(f"Mock 串口发送数据: {len(data)} 字节 -> {data.hex()}")
            return len(data)
        except Exception as e:
            logger.error(f"Mock 串口发送失败: {e}")
            self.increment_error()
            raise
    
    def recv(self, size: int = 1, timeout: float = 1.0) -> Optional[bytes]:
        """
        接收数据
        
        Args:
            size: 期望接收的字节数（当前实现忽略此参数）
            timeout: 超时时间（秒）
            
        Returns:
            接收到的数据，超时返回 None
            
        Raises:
            ConnectionError: 串口未打开时
        """
        if not self._is_open:
            raise ConnectionError(f"串口未打开: {self.port}")
        
        start_time = time.time()
        sleep_interval = 0.001
        
        while time.time() - start_time < timeout:
            if self._recv_buffer:
                data = self._recv_buffer.pop(0)
                logger.debug(f"Mock 串口接收数据: {len(data)} 字节 -> {data.hex()}")
                return data
            
            if self._auto_response:
                time.sleep(self._mock_response_delay)
                logger.debug(f"Mock 串口自动响应: {self._auto_response.hex()}")
                return self._auto_response
            else:
                time.sleep(sleep_interval)
        
        logger.debug(f"Mock 串口接收超时: {timeout}s")
        return None
    
    def send_recv(self, data: bytes, timeout: float = 1.0) -> Optional[bytes]:
        """
        发送并接收响应
        
        Args:
            data: 要发送的数据
            timeout: 超时时间（秒）
            
        Returns:
            接收到的数据，超时返回 None
        """
        self.send(data)
        return self.recv(timeout=timeout)
    
    def set_auto_response(self, response: bytes):
        """设置自动响应数据"""
        self._auto_response = response
        logger.debug(f"Mock 串口设置自动响应: {response.hex()}")
    
    def queue_response(self, data: bytes):
        """队列式添加响应数据（支持多数据块）"""
        self._recv_buffer.append(data)
        logger.debug(f"Mock 串口队列响应数据: {len(data)} 字节 -> {data.hex()}")
    
    def clear_buffers(self):
        """清空所有缓冲区"""
        self._send_buffer = b''
        self._recv_buffer.clear()
        logger.debug("Mock 串口缓冲区已清空")
    
    def get_send_buffer(self) -> bytes:
        """获取发送缓冲区内容"""
        return self._send_buffer
    
    def set_response_delay(self, delay: float):
        """设置模拟响应延迟（秒）"""
        self._mock_response_delay = max(0, delay)
        logger.debug(f"Mock 串口响应延迟设置为: {delay}s")
    
    def health_check(self):
        """健康检查"""
        base = super().health_check()
        base.update({
            'send_buffer_size': len(self._send_buffer),
            'recv_buffer_count': len(self._recv_buffer),
            'mock': True
        })
        return base
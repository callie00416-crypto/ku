"""
自定义ASCII协议驱动

【协议特点】
- ASCII编码
- 固定指令格式: PREFIX,CMD,VALUE,SUFFIX
- 简单的响应解析
- 无寄存器概念

【职责】
- 构建ASCII命令
- 解析ASCII响应
- 处理通信层交互
"""
import logging
from typing import Optional

from shared.drivers.base.base_protocol import BaseProtocol


logger = logging.getLogger(__name__)


class CustomASCIIProtocol(BaseProtocol):
    """自定义ASCII协议
    
    【协议格式】
    - 命令: PREFIX,CMD,VALUE,SUFFIX
    - 响应: ASCII字符串
    
    【示例】
    - 命令: ATATATA,SET,AON,0000;
    - 响应: SET DONE!
    
    【使用示例】
    >>> from shared.drivers.factory import CommFactory
    >>> 
    >>> # 创建通信层
    >>> comm = CommFactory.create('rs485', port='COM1', baudrate=9600)
    >>> 
    >>> # 创建协议层
    >>> protocol = CustomASCIIProtocol(
    ...     comm=comm,
    ...     command_prefix='ATATATA,SET,',
    ...     command_suffix=';'
    ... )
    >>> 
    >>> # 发送命令
    >>> response = protocol.send_command('AON,0000')
    """
    
    def __init__(self, driver_id: str, comm, command_prefix: str = 'ATATATA,SET,', 
                 command_suffix: str = ';', newline: str = '\r\n', **kwargs):
        """
        Args:
            driver_id: 驱动ID
            comm: 通信层对象
            command_prefix: 命令前缀
            command_suffix: 命令后缀
            newline: 换行符（默认：\r\n）
            **kwargs: 其他参数
        """
        super().__init__(driver_id, comm, **kwargs)
        
        self.command_prefix = command_prefix
        self.command_suffix = command_suffix
        self.newline = newline
        
        # 响应映射
        self.response_map = {
            'SET DONE!': 'success',
            'SET ERROR!': 'error',
            'OVER RANGE ERROR!': 'over_range'
        }
        
        logger.info(f"自定义ASCII协议初始化完成")
        logger.debug(f"命令前缀: {command_prefix}")
        logger.debug(f"命令后缀: {command_suffix}")
        logger.debug(f"换行符: {repr(newline)}")
    
    def connect(self) -> bool:
        """连接设备
        
        Returns:
            是否连接成功
        """
        try:
            if self.comm and hasattr(self.comm, 'connect'):
                success = self.comm.connect()
                if success:
                    self._is_connected = True
                    logger.info("自定义ASCII协议连接成功")
                else:
                    logger.error("自定义ASCII协议连接失败")
                return success
            else:
                logger.warning("通信层不支持连接，假设已连接")
                self._is_connected = True
                return True
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        try:
            if self.comm and hasattr(self.comm, 'disconnect'):
                self.comm.disconnect()
            self._is_connected = False
            logger.info("自定义ASCII协议已断开")
        except Exception as e:
            logger.error(f"断开连接失败: {e}")
    
    def is_connected(self) -> bool:
        """检查是否连接
        
        Returns:
            是否已连接
        """
        return self._is_connected
    
    def send_command(self, command: str, timeout: Optional[int] = None) -> str:
        """发送命令
        
        Args:
            command: 命令内容（不包含前缀和后缀）
            timeout: 超时时间
            
        Returns:
            响应内容
        """
        try:
            # 构建完整命令
            full_command = f"{self.command_prefix}{command}{self.command_suffix}{self.newline}"
            logger.debug(f"发送命令: {full_command}")
            
            # 发送命令
            if hasattr(self.comm, 'send'):
                self.comm.send(full_command.encode('ascii'))
            else:
                raise AttributeError("通信层不支持send方法")
            
            # 读取响应
            if hasattr(self.comm, 'recv'):
                timeout_sec = timeout / 1000.0 if timeout else 1.0
                response_bytes = self.comm.recv(size=1024, timeout=timeout_sec)
                if response_bytes:
                    response = response_bytes.decode('ascii').strip()
                else:
                    response = ""
            else:
                raise AttributeError("通信层不支持recv方法")
            
            logger.debug(f"接收响应: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"发送命令失败: {e}")
            raise
    
    def write_register(self, address: int, value: int, **kwargs) -> bool:
        """写入寄存器（不支持）
        
        Args:
            address: 寄存器地址
            value: 寄存器值
            **kwargs: 其他参数
            
        Returns:
            是否成功
        """
        logger.warning("自定义ASCII协议不支持寄存器写入")
        return False
    
    def read_register(self, address: int, **kwargs) -> Optional[int]:
        """读取寄存器（不支持）
        
        Args:
            address: 寄存器地址
            **kwargs: 其他参数
            
        Returns:
            寄存器值
        """
        logger.warning("自定义ASCII协议不支持寄存器读取")
        return None
    
    def parse_response(self, response: str) -> dict:
        """解析响应
        
        Args:
            response: 响应字符串
            
        Returns:
            解析结果
        """
        result = {
            'raw': response,
            'status': 'unknown'
        }
        
        # 检查响应类型
        for resp_str, status in self.response_map.items():
            if resp_str in response:
                result['status'] = status
                break
        
        logger.debug(f"解析响应: {result}")
        return result
    
    def validate_command(self, command: str) -> bool:
        """验证命令
        
        Args:
            command: 命令内容
            
        Returns:
            是否有效
        """
        # 基本验证
        if not command:
            return False
        
        # 检查是否包含非法字符
        invalid_chars = ['\n', '\r', '\t']
        for char in invalid_chars:
            if char in command:
                logger.warning(f"命令包含非法字符: {char}")
                return False
        
        return True
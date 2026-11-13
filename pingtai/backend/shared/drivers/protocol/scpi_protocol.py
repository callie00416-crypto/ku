"""
SCPI协议驱动 - 标准命令可编程仪器协议

【职责】
- SCPI命令封装
- 命令解析和响应处理
- 支持标准SCPI命令集

【架构】
- 继承 BaseProtocol
- 封装SCPI命令格式
- 支持查询和设置命令

【使用示例】
>>> from shared.drivers.protocol.scpi_protocol import SCPIProtocol
>>> from shared.drivers.comm.usb_comm import USBComm
>>> comm = USBComm(driver_id='usb_tmc', vid=0x0914, pid=0x0001)
>>> comm.open()
>>> protocol = SCPIProtocol(driver_id='scpi', comm=comm)
>>> protocol.query('*IDN?')
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
import time
from typing import Dict, Any, Optional, Union
from shared.drivers.base.base_protocol import BaseProtocol

logger = logging.getLogger(__name__)


class SCPIProtocol(BaseProtocol):
    """SCPI协议驱动
    
    【组合关系】
    SCPIProtocol -> Comm (USB/Serial/TCP)
    
    【架构集成】
    - 继承 BaseProtocol 基类
    - 支持平台协议层管理
    - 符合工业设备规范
    
    【使用示例】
    >>> comm = USBComm(driver_id='usb_tmc', vid=0x0914, pid=0x0001)
    >>> comm.open()
    >>> protocol = SCPIProtocol(driver_id='scpi', comm=comm)
    >>> protocol.query('*IDN?')
    """
    
    def __init__(self, driver_id: str = 'scpi', comm=None, **kwargs):
        """
        Args:
            driver_id: 驱动ID
            comm: 通信对象
            **kwargs: 其他参数
        """
        super().__init__(driver_id, comm, **kwargs)
        self.comm = comm
        
        # SCPI命令分隔符
        self._cmd_separator = '\n'
        self._query_separator = '?'
    
    def connect(self) -> bool:
        """连接协议层
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 集成平台状态管理
        
        Returns:
            是否成功
        """
        try:
            if self.comm and not self.comm.is_open:
                if not self.comm.open():
                    self._is_connected = False
                    return False
            
            self._is_connected = True
            logger.info(f"SCPI协议连接成功: {self.driver_id}")
            return True
            
        except Exception as e:
            logger.error(f"SCPI协议连接失败: {e}")
            self._is_connected = False
            self.increment_error()
            return False
    
    def disconnect(self):
        """断开协议层
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 集成平台状态管理
        """
        self._is_connected = False
        
        if self.comm:
            self.comm.close()
        
        logger.info(f"SCPI协议已断开: {self.driver_id}")
    
    @property
    def is_connected(self) -> bool:
        """检查是否连接"""
        return self._is_connected and (self.comm is None or self.comm.is_open)
    
    def send_command(self, command: str) -> bool:
        """发送SCPI命令
        
        Args:
            command: SCPI命令（不带换行符）
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("SCPI协议未连接")
        
        try:
            # 添加换行符
            cmd_bytes = (command + self._cmd_separator).encode('utf-8')
            self.comm.send(cmd_bytes)
            logger.debug(f"SCPI发送命令: {command}")
            return True
            
        except Exception as e:
            logger.error(f"SCPI发送命令失败: {e}")
            self.increment_error()
            return False
    
    def query(self, command: str, timeout: float = 1.0) -> Optional[str]:
        """查询SCPI命令
        
        Args:
            command: SCPI查询命令（带?）
            timeout: 超时时间（秒）
            
        Returns:
            响应字符串
        """
        if not self.is_connected:
            raise ConnectionError("SCPI协议未连接")
        
        try:
            # 发送查询命令
            if not command.endswith('?'):
                command = command + '?'
            
            self.send_command(command)
            
            # 接收响应
            response_bytes = self.comm.recv(size=1024, timeout=timeout)
            
            if response_bytes is None:
                logger.warning(f"SCPI查询超时: {command}")
                return None
            
            # 解码响应
            response = response_bytes.decode('utf-8').strip()
            logger.debug(f"SCPI查询响应: {command} -> {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"SCPI查询失败: {e}")
            self.increment_error()
            return None
    
    def write(self, command: str) -> bool:
        """写入SCPI命令（不带响应）
        
        Args:
            command: SCPI命令
            
        Returns:
            是否成功
        """
        return self.send_command(command)
    
    def read(self, timeout: float = 1.0) -> Optional[str]:
        """读取SCPI响应
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            响应字符串
        """
        if not self.is_connected:
            raise ConnectionError("SCPI协议未连接")
        
        try:
            response_bytes = self.comm.recv(size=1024, timeout=timeout)
            
            if response_bytes is None:
                return None
            
            response = response_bytes.decode('utf-8').strip()
            logger.debug(f"SCPI读取响应: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"SCPI读取失败: {e}")
            self.increment_error()
            return None
    
    def reset(self) -> bool:
        """重置设备
        
        Returns:
            是否成功
        """
        return self.send_command('*RST')
    
    def clear(self) -> bool:
        """清除设备错误队列
        
        Returns:
            是否成功
        """
        return self.send_command('*CLS')
    
    def get_id(self) -> Optional[str]:
        """获取设备标识
        
        Returns:
            设备标识字符串
        """
        return self.query('*IDN')
    
    def get_error(self) -> Optional[str]:
        """获取设备错误
        
        Returns:
            错误信息
        """
        return self.query('SYST:ERR?')
    
    def wait_for_completion(self, timeout: float = 10.0) -> bool:
        """等待操作完成
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            是否完成
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self.query('*OPC?')
            if result == '1':
                return True
            time.sleep(0.1)
        return False
    
    def read_register(self, address: int, slave_id: int = None) -> Optional[int]:
        """读寄存器（SCPI协议不支持寄存器操作）
        
        Args:
            address: 寄存器地址
            slave_id: 从站ID
            
        Returns:
            寄存器值（SCPI协议不支持，返回None）
        """
        logger.warning("SCPI协议不支持寄存器读取操作")
        return None
    
    def write_register(self, address: int, value: int, slave_id: int = None) -> bool:
        """写寄存器（SCPI协议不支持寄存器操作）
        
        Args:
            address: 寄存器地址
            value: 寄存器值
            slave_id: 从站ID
            
        Returns:
            是否成功（SCPI协议不支持，返回False）
        """
        logger.warning("SCPI协议不支持寄存器写入操作")
        return False
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查
        
        【架构集成】
        - 继承基类健康检查
        - 添加SCPI特定检查
        - 提供详细诊断信息
        
        Returns:
            健康状态字典
        """
        base = super().health_check()
        
        # SCPI特定健康检查
        try:
            if self.is_connected:
                # 尝试获取设备ID
                device_id = self.get_id()
                device_error = self.get_error()
                
                scpi_health = {
                    'protocol_type': 'SCPI',
                    'device_id': device_id,
                    'last_error': device_error,
                    'comm_driver_id': self.comm.driver_id if self.comm else None,
                    'comm_is_open': self.comm.is_open if self.comm else False
                }
            else:
                scpi_health = {
                    'protocol_type': 'SCPI',
                    'status': 'disconnected',
                    'comm_driver_id': self.comm.driver_id if self.comm else None
                }
        except Exception as e:
            logger.error(f"SCPI健康检查异常: {e}")
            scpi_health = {
                'protocol_type': 'SCPI',
                'status': 'error',
                'error': str(e),
                'comm_driver_id': self.comm.driver_id if self.comm else None
            }
        
        base.update(scpi_health)
        return base
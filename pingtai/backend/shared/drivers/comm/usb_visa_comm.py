"""
USB通信驱动 - 基于PyVISA的USBTMC设备

【职责】
- 管理USB连接
- 数据收发
- 支持USBTMC（USB Test and Measurement Class）设备

【架构】
- 继承 BaseComm
- 使用 pyvisa 库
- 支持USBTMC协议

【使用示例】
>>> from shared.drivers.comm.usb_visa_comm import USBVisaComm
>>> comm = USBVisaComm(driver_id='usb_visa', vid=0x0914, pid=0x0001)
>>> comm.open()
>>> comm.send(b'*IDN?\n')
>>> response = comm.recv(1024)
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
import time
from typing import Dict, Any, Optional
from shared.drivers.base.base_comm import BaseComm

logger = logging.getLogger(__name__)

try:
    import pyvisa
    VISA_AVAILABLE = True
except ImportError:
    VISA_AVAILABLE = False
    logger.warning("pyvisa库未安装，USB VISA通信不可用")


class USBVisaComm(BaseComm):
    """USB VISA通信驱动 - USBTMC设备
    
    【组合关系】
    USBVisaComm -> VISA Resource
    
    【架构集成】
    - 继承 BaseComm 基类
    - 支持平台通信层管理
    - 符合工业设备规范
    
    【使用示例】
    >>> comm = USBVisaComm(driver_id='usb_visa', vid=0x0914, pid=0x0001)
    >>> comm.open()
    >>> comm.send(b'*IDN?\n')
    >>> response = comm.recv(1024)
    """
    
    def __init__(self, driver_id: str = 'usb_visa', vid: int = 0, pid: int = 0, 
                 **kwargs):
        """
        Args:
            driver_id: 驱动ID
            vid: USB Vendor ID
            pid: USB Product ID
            **kwargs: 其他参数
        """
        super().__init__(driver_id, **kwargs)
        self.vid = vid
        self.pid = pid
        
        self._resource_manager = None
        self._instrument = None
        
        if not VISA_AVAILABLE:
            raise ImportError("pyvisa库未安装，请执行: pip install pyvisa")
    
    def open(self) -> bool:
        """打开USB设备
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 支持超时和错误处理
        - 集成平台状态管理
        
        Returns:
            是否成功
        """
        try:
            logger.info(f"正在打开USB VISA设备: VID={self.vid:04X}, PID={self.pid:04X}")
            
            # 创建资源管理器
            self._resource_manager = pyvisa.ResourceManager()
            
            # 查找USB设备
            vid_hex = f"{self.vid:04X}"
            pid_hex = f"{self.pid:04X}"
            
            # 构建VISA资源字符串
            resource_string = f"USB0::{vid_hex}::{pid_hex}::INSTR"
            
            logger.info(f"尝试打开资源: {resource_string}")
            
            # 尝试打开设备
            try:
                self._instrument = self._resource_manager.open_resource(resource_string)
            except Exception as e:
                logger.warning(f"使用标准资源字符串失败: {e}")
                
                # 尝试列出所有资源
                try:
                    resources = self._resource_manager.list_resources()
                    logger.info(f"可用的VISA资源: {resources}")
                    
                    # 查找匹配的设备
                    for resource in resources:
                        if f"::{vid_hex}::" in resource and f"::{pid_hex}::" in resource:
                            logger.info(f"找到匹配设备: {resource}")
                            self._instrument = self._resource_manager.open_resource(resource)
                            break
                    else:
                        logger.error(f"未找到匹配的USB设备: VID={vid_hex}, PID={pid_hex}")
                        self._is_open = False
                        return False
                except Exception as e2:
                    logger.error(f"列出资源失败: {e2}")
                    self._is_open = False
                    return False
            
            # 设置超时和终止符
            self._instrument.timeout = 5000  # 5秒超时
            self._instrument.write_termination = '\n'
            self._instrument.read_termination = '\n'
            
            self._is_open = True
            logger.info(f"USB VISA设备打开成功: VID={self.vid:04X}, PID={self.pid:04X}")
            return True
            
        except Exception as e:
            logger.error(f"打开USB VISA设备失败: {e}")
            self._is_open = False
            self.increment_error()
            return False
    
    def close(self):
        """关闭USB设备
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 释放USB资源
        - 集成平台状态管理
        """
        try:
            if self._instrument is not None:
                self._instrument.close()
                self._instrument = None
            
            if self._resource_manager is not None:
                self._resource_manager.close()
                self._resource_manager = None
            
            self._is_open = False
            logger.info(f"USB VISA设备已关闭: {self.driver_id}")
            
        except Exception as e:
            logger.error(f"关闭USB VISA设备失败: {e}")
            self.increment_error()
    
    def send(self, data: bytes) -> int:
        """发送数据
        
        Args:
            data: 要发送的数据
            
        Returns:
            发送的字节数
        """
        if not self._is_open or self._instrument is None:
            raise ConnectionError("USB VISA设备未打开")
        
        try:
            # 如果是字符串，转换为bytes
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            self._instrument.write(data.decode('utf-8'))
            bytes_written = len(data)
            logger.debug(f"USB VISA发送 {bytes_written} 字节: {data[:100]}")
            return bytes_written
            
        except Exception as e:
            logger.error(f"USB VISA发送失败: {e}")
            self.increment_error()
            raise
    
    def recv(self, size: int = 1024, timeout: float = 1.0) -> Optional[bytes]:
        """接收数据
        
        Args:
            size: 接收缓冲区大小（VISA中不使用）
            timeout: 超时时间（秒）
            
        Returns:
            接收到的数据
        """
        if not self._is_open or self._instrument is None:
            raise ConnectionError("USB VISA设备未打开")
        
        try:
            # 设置超时
            original_timeout = self._instrument.timeout
            self._instrument.timeout = int(timeout * 1000)
            
            # 读取数据
            data = self._instrument.read()
            
            # 恢复超时
            self._instrument.timeout = original_timeout
            
            # 转换为bytes
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            logger.debug(f"USB VISA接收 {len(data)} 字节: {data[:100]}")
            return data
            
        except pyvisa.errors.VisaIOError as e:
            if e.abbreviation == 'VI_ERROR_TMO':  # 超时
                logger.debug("USB VISA接收超时")
                return None
            logger.error(f"USB VISA接收失败: {e}")
            self.increment_error()
            raise
        except Exception as e:
            logger.error(f"USB VISA接收失败: {e}")
            self.increment_error()
            raise
    
    def send_recv(self, data: bytes, timeout: float = 1.0) -> Optional[bytes]:
        """发送并接收
        
        Args:
            data: 要发送的数据
            timeout: 超时时间（秒）
            
        Returns:
            接收到的数据
        """
        self.send(data)
        time.sleep(0.1)  # 等待设备响应
        return self.recv(size=1024, timeout=timeout)
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查
        
        【架构集成】
        - 继承基类健康检查
        - 添加USB VISA特定检查
        - 提供详细诊断信息
        
        Returns:
            健康状态字典
        """
        base = super().health_check()
        
        # USB VISA特定健康检查
        try:
            if self._is_open and self._instrument is not None:
                visa_health = {
                    'vid': f"{self.vid:04X}",
                    'pid': f"{self.pid:04X}",
                    'resource_name': self._instrument.resource_name,
                    'timeout': self._instrument.timeout,
                    'write_termination': repr(self._instrument.write_termination),
                    'read_termination': repr(self._instrument.read_termination)
                }
            else:
                visa_health = {
                    'vid': f"{self.vid:04X}",
                    'pid': f"{self.pid:04X}",
                    'status': 'disconnected'
                }
        except Exception as e:
            logger.error(f"USB VISA健康检查异常: {e}")
            visa_health = {
                'vid': f"{self.vid:04X}",
                'pid': f"{self.pid:04X}",
                'status': 'error',
                'error': str(e)
            }
        
        base.update(visa_health)
        return base
    
    def reset(self):
        """重置USB设备"""
        self.close()
        time.sleep(0.5)
        self.open()
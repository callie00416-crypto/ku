"""
USB通信驱动 - 用于USBTMC设备

【职责】
- 管理USB连接
- 数据收发
- 支持USBTMC（USB Test and Measurement Class）设备

【架构】
- 继承 BaseComm
- 使用 pyusb 库
- 支持USBTMC协议

【使用示例】
>>> from shared.drivers.comm.usb_comm import USBComm
>>> comm = USBComm(driver_id='usb_tmc', vid=0x0914, pid=0x0001)
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
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    logger.warning("pyusb库未安装，USB通信不可用")


class USBComm(BaseComm):
    """USB通信驱动 - USBTMC设备
    
    【组合关系】
    USBComm -> USB Device
    
    【架构集成】
    - 继承 BaseComm 基类
    - 支持平台通信层管理
    - 符合工业设备规范
    
    【使用示例】
    >>> comm = USBComm(driver_id='usb_tmc', vid=0x0914, pid=0x0001)
    >>> comm.open()
    >>> comm.send(b'*IDN?\n')
    >>> response = comm.recv(1024)
    """
    
    USBTMC_CLASS = 0xFE
    USBTMC_SUBCLASS = 0x03
    USBTMC_PROTOCOL = 0x00
    
    def __init__(self, driver_id: str = 'usb_tmc', vid: int = 0, pid: int = 0, 
                 interface: int = 0, **kwargs):
        """
        Args:
            driver_id: 驱动ID
            vid: USB Vendor ID
            pid: USB Product ID
            interface: USB接口号
            **kwargs: 其他参数
        """
        super().__init__(driver_id, **kwargs)
        self.vid = vid
        self.pid = pid
        self.interface = interface
        
        self._device = None
        self._cfg = None
        self._intf = None
        self._ep_out = None
        self._ep_in = None
        
        if not USB_AVAILABLE:
            raise ImportError("pyusb库未安装，请执行: pip install pyusb")
    
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
            logger.info(f"正在打开USB设备: VID={self.vid:04X}, PID={self.pid:04X}")
            
            # 查找设备
            self._device = usb.core.find(idVendor=self.vid, idProduct=self.pid)
            
            if self._device is None:
                logger.error(f"未找到USB设备: VID={self.vid:04X}, PID={self.pid:04X}")
                self._is_open = False
                return False
            
            # 如果是Linux系统，需要先分离内核驱动
            if self._device.is_kernel_driver_active(self.interface):
                try:
                    self._device.detach_kernel_driver(self.interface)
                    logger.info("已分离内核驱动")
                except usb.core.USBError as e:
                    logger.warning(f"分离内核驱动失败: {e}")
            
            # 设置配置
            self._cfg = self._device.get_active_configuration()
            self._intf = self._cfg[(self.interface, 0)]
            
            # 查找端点
            ep_found = False
            for ep in self._intf.endpoints():
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                    self._ep_out = ep
                elif usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                    self._ep_in = ep
            
            if self._ep_out is None or self._ep_in is None:
                logger.error("未找到USB端点")
                self._is_open = False
                return False
            
            # 设置超时
            self._device.set_configuration()
            
            self._is_open = True
            logger.info(f"USB设备打开成功: VID={self.vid:04X}, PID={self.pid:04X}")
            return True
            
        except Exception as e:
            logger.error(f"打开USB设备失败: {e}")
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
            if self._device is not None:
                usb.util.dispose_resources(self._device)
                self._device = None
                self._cfg = None
                self._intf = None
                self._ep_out = None
                self._ep_in = None
            
            self._is_open = False
            logger.info(f"USB设备已关闭: {self.driver_id}")
            
        except Exception as e:
            logger.error(f"关闭USB设备失败: {e}")
            self.increment_error()
    
    def send(self, data: bytes) -> int:
        """发送数据
        
        Args:
            data: 要发送的数据
            
        Returns:
            发送的字节数
        """
        if not self._is_open or self._ep_out is None:
            raise ConnectionError("USB设备未打开")
        
        try:
            bytes_written = self._device.write(self._ep_out.bEndpointAddress, data, timeout=1000)
            logger.debug(f"USB发送 {bytes_written} 字节: {data[:100]}")
            return bytes_written
            
        except Exception as e:
            logger.error(f"USB发送失败: {e}")
            self.increment_error()
            raise
    
    def recv(self, size: int = 1024, timeout: float = 1.0) -> Optional[bytes]:
        """接收数据
        
        Args:
            size: 接收缓冲区大小
            timeout: 超时时间（秒）
            
        Returns:
            接收到的数据
        """
        if not self._is_open or self._ep_in is None:
            raise ConnectionError("USB设备未打开")
        
        try:
            data = self._device.read(self._ep_in.bEndpointAddress, size, timeout=int(timeout*1000))
            logger.debug(f"USB接收 {len(data)} 字节: {data[:100]}")
            return data
            
        except usb.core.USBError as e:
            if e.errno == 110:  # 超时
                logger.debug("USB接收超时")
                return None
            logger.error(f"USB接收失败: {e}")
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
        - 添加USB特定检查
        - 提供详细诊断信息
        
        Returns:
            健康状态字典
        """
        base = super().health_check()
        
        # USB特定健康检查
        try:
            if self._is_open and self._device is not None:
                usb_health = {
                    'vid': f"{self.vid:04X}",
                    'pid': f"{self.pid:04X}",
                    'interface': self.interface,
                    'endpoint_out': hex(self._ep_out.bEndpointAddress) if self._ep_out else None,
                    'endpoint_in': hex(self._ep_in.bEndpointAddress) if self._ep_in else None,
                    'device_configured': self._device.get_active_configuration() is not None
                }
            else:
                usb_health = {
                    'vid': f"{self.vid:04X}",
                    'pid': f"{self.pid:04X}",
                    'interface': self.interface,
                    'status': 'disconnected'
                }
        except Exception as e:
            logger.error(f"USB健康检查异常: {e}")
            usb_health = {
                'vid': f"{self.vid:04X}",
                'pid': f"{self.pid:04X}",
                'status': 'error',
                'error': str(e)
            }
        
        base.update(usb_health)
        return base
    
    def reset(self):
        """重置USB设备"""
        self.close()
        time.sleep(0.5)
        self.open()
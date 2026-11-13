"""串口设备检测器

自动扫描串口并识别设备类型
"""
import serial
import serial.tools.list_ports
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from .device_fingerprint import (
    DeviceFingerprint,
    get_fingerprint,
    get_all_fingerprints,
    match_fingerprint_by_hwid,
    match_fingerprint_by_description
)

logger = logging.getLogger(__name__)


@dataclass
class SerialPortInfo:
    """串口信息"""
    port: str
    description: str
    hwid: str
    vid: Optional[str] = None
    pid: Optional[str] = None
    serial_number: Optional[str] = None


@dataclass
class DeviceInfo:
    """设备信息"""
    port: str
    device_type: str
    name: str
    protocol: str
    baud_rate: int
    is_connected: bool = False
    confidence: float = 0.0
    connection_type: str = 'serial'  # serial or usb


class SerialDeviceDetector:
    """串口设备检测器"""
    
    def __init__(self):
        self._cache: Dict[str, DeviceInfo] = {}
        self._cache_timestamp: float = 0
        self._cache_ttl: float = 5.0
    
    def scan_all_ports(self) -> List[SerialPortInfo]:
        """扫描所有可用串口"""
        ports = []
        try:
            for port_info in serial.tools.list_ports.comports():
                port = SerialPortInfo(
                    port=port_info.device,
                    description=port_info.description,
                    hwid=port_info.hwid,
                    vid=self._extract_vid(port_info.hwid),
                    pid=self._extract_pid(port_info.hwid),
                    serial_number=port_info.serial_number
                )
                ports.append(port)
        except Exception as e:
            logger.error(f"扫描串口失败: {e}")
        return ports
    
    def _extract_vid(self, hwid: str) -> Optional[str]:
        """从硬件ID提取VID"""
        import re
        match = re.search(r'VID:PID=([0-9A-Fa-f]{4}):', hwid)
        return match.group(1).upper() if match else None
    
    def _extract_pid(self, hwid: str) -> Optional[str]:
        """从硬件ID提取PID"""
        import re
        match = re.search(r'VID:PID=[0-9A-Fa-f]{4}:([0-9A-Fa-f]{4})', hwid)
        return match.group(1).upper() if match else None
    
    def identify_device_by_hardware(self, port_info: SerialPortInfo) -> Optional[DeviceFingerprint]:
        """通过硬件信息识别设备"""
        from .device_fingerprint import get_all_fingerprints
        
        fingerprints = get_all_fingerprints()
        
        for fp in fingerprints.values():
            if fp.device_type == 'unknown':
                continue
            
            match = True
            
            if fp.vid:
                if not port_info.vid or fp.vid != port_info.vid:
                    match = False
            
            if fp.pid:
                if not port_info.pid or fp.pid != port_info.pid:
                    match = False
            
            if fp.serial_number:
                if not port_info.serial_number or fp.serial_number != port_info.serial_number:
                    match = False
            
            if match and (fp.vid or fp.pid or fp.serial_number):
                logger.info(f"通过硬件信息识别设备: {port_info.port} -> {fp.name}")
                return fp
        
        if port_info.description:
            matches = match_fingerprint_by_description(port_info.description)
            if matches:
                fp = matches[0]
                logger.info(f"通过描述识别设备: {port_info.port} -> {fp.name}")
                return fp
        
        return None
    
    def identify_device_by_protocol(self, port_info: SerialPortInfo) -> Optional[DeviceFingerprint]:
        """通过协议测试识别设备"""
        fingerprints = get_all_fingerprints()
        
        for fp in fingerprints.values():
            if fp.device_type == 'unknown':
                continue
            
            if fp.test_command is None:
                continue
            
            try:
                if self._test_device(port_info.port, fp):
                    logger.info(f"通过协议测试识别设备: {port_info.port} -> {fp.name}")
                    return fp
            except Exception as e:
                logger.debug(f"测试 {fp.name} 失败: {e}")
                continue
        
        return None
    
    def _test_device(self, port: str, fingerprint: DeviceFingerprint) -> bool:
        """测试设备是否匹配指纹"""
        try:
            ser = serial.Serial(port, fingerprint.baud_rate, timeout=fingerprint.response_timeout)
            
            for _ in range(fingerprint.retry_count):
                try:
                    if isinstance(fingerprint.test_command, list):
                        ser.write(bytes(fingerprint.test_command))
                    elif isinstance(fingerprint.test_command, str):
                        ser.write(fingerprint.test_command.encode('ascii'))
                    else:
                        ser.write(bytes([fingerprint.test_command]))
                    
                    response = ser.read(1024)
                    
                    if self._validate_response(response, fingerprint.expected_response):
                        ser.close()
                        return True
                    
                except Exception:
                    time.sleep(0.1)
            
            ser.close()
            return False
            
        except Exception as e:
            logger.debug(f"无法打开串口 {port}: {e}")
            return False
    
    def _validate_response(self, response: bytes, expected) -> bool:
        """验证响应是否符合预期"""
        if not response:
            return False
        
        if isinstance(expected, list):
            expected_bytes = bytes(expected)
            return response[:len(expected_bytes)] == expected_bytes
        elif isinstance(expected, int):
            return len(response) == expected
        
        return False
    
    def identify_device(self, port_info: SerialPortInfo) -> DeviceInfo:
        """识别设备"""
        fingerprint = self.identify_device_by_hardware(port_info)
        
        if not fingerprint:
            fingerprint = self.identify_device_by_protocol(port_info)
        
        if not fingerprint:
            fingerprint = get_fingerprint('unknown')
        
        return DeviceInfo(
            port=port_info.port,
            device_type=fingerprint.device_type,
            name=fingerprint.name,
            protocol=fingerprint.protocol,
            baud_rate=fingerprint.baud_rate,
            is_connected=True,
            confidence=1.0 if fingerprint.device_type != 'unknown' else 0.0
        )
    
    def auto_discover(self, use_cache: bool = True) -> Dict[str, DeviceInfo]:
        """自动发现所有设备（串口+USB）"""
        current_time = time.time()
        
        if use_cache and self._cache and (current_time - self._cache_timestamp) < self._cache_ttl:
            logger.debug("使用缓存的设备信息")
            return self._cache
        
        logger.info("开始自动发现设备...")
        
        devices = {}
        
        logger.info("扫描串口设备...")
        ports = self.scan_all_ports()
        for port_info in ports:
            try:
                device_info = self.identify_device(port_info)
                devices[port_info.port] = device_info
            except Exception as e:
                logger.error(f"识别设备 {port_info.port} 失败: {e}")
        
        logger.info("扫描USB设备...")
        try:
            from .usb_detector import UsbDeviceDetector
            usb_detector = UsbDeviceDetector()
            usb_devices = usb_detector.scan_devices()
            
            for key, usb_info in usb_devices.items():
                device_info = DeviceInfo(
                    port=key,
                    device_type=usb_info.device_type,
                    name=usb_info.product_name,
                    protocol=usb_info.protocol,
                    baud_rate=0,
                    is_connected=True,
                    confidence=1.0,
                    connection_type='usb'
                )
                devices[key] = device_info
                logger.info(f"发现USB设备: {key} -> {usb_info.product_name}")
        except ImportError:
            logger.warning("USB检测模块未加载")
        except Exception as e:
            logger.error(f"扫描USB设备失败: {e}")
        
        logger.info("扫描WMI设备...")
        try:
            from .wmi_detector import WmiDeviceDetector
            wmi_detector = WmiDeviceDetector()
            wmi_devices = wmi_detector.scan_devices()
            
            for key, wmi_info in wmi_devices.items():
                if key not in devices:
                    device_info = DeviceInfo(
                        port=key,
                        device_type=wmi_info.device_type,
                        name=wmi_info.name,
                        protocol=wmi_info.protocol,
                        baud_rate=0,
                        is_connected=True,
                        confidence=1.0,
                        connection_type=wmi_info.connection_type
                    )
                    devices[key] = device_info
                    logger.info(f"发现WMI设备: {key} -> {wmi_info.name}")
        except ImportError:
            logger.warning("WMI检测模块未加载")
        except Exception as e:
            logger.error(f"扫描WMI设备失败: {e}")
        
        self._cache = devices
        self._cache_timestamp = current_time
        
        logger.info(f"自动发现完成，找到 {len(devices)} 个设备")
        return devices
    
    def get_device_by_type(self, device_type: str) -> Optional[DeviceInfo]:
        """根据设备类型获取设备"""
        devices = self.auto_discover()
        for device in devices.values():
            if device.device_type == device_type:
                return device
        return None
    
    def get_all_devices_by_type(self, device_type: str) -> List[DeviceInfo]:
        """根据设备类型获取所有设备"""
        devices = self.auto_discover()
        return [d for d in devices.values() if d.device_type == device_type]
    
    def clear_cache(self):
        """清除缓存"""
        self._cache = {}
        self._cache_timestamp = 0
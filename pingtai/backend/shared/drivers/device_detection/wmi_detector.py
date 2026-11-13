"""WMI设备检测器

使用Windows WMI识别设备，包括IVI仪器
"""
import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    import win32com.client
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    logger.warning("pywin32 未安装，无法使用WMI检测")


@dataclass
class DeviceInfo:
    """设备信息"""
    port: str
    device_type: str
    name: str
    protocol: str
    connection_type: str


class WmiDeviceDetector:
    """WMI设备检测器"""
    
    def __init__(self):
        if WMI_AVAILABLE:
            try:
                self._wmi = win32com.client.GetObject("winmgmts:")
            except Exception as e:
                logger.error(f"初始化WMI失败: {e}")
                self._wmi = None
        else:
            self._wmi = None
    
    def scan_devices(self) -> Dict[str, DeviceInfo]:
        """扫描所有设备"""
        devices = {}
        
        if not self._wmi:
            return devices
        
        try:
            devices.update(self._scan_pnp_devices())
            devices.update(self._scan_usb_devices())
            
        except Exception as e:
            logger.error(f"扫描设备失败: {e}")
        
        return devices
    
    def _scan_pnp_devices(self):
        """扫描即插即用设备"""
        devices = {}
        
        try:
            for device in self._wmi.InstancesOf("Win32_PnPEntity"):
                try:
                    name = str(device.Name) if device.Name else ""
                    device_id = str(device.DeviceID) if device.DeviceID else ""
                    
                    if 'Test and Measurement' in name:
                        vid, pid = self._parse_vid_pid(device_id)
                        if vid and pid:
                            key = f"USB_{vid}_{pid}"
                            devices[key] = DeviceInfo(
                                port=key,
                                device_type='dg811_waveform_generator',
                                name=f"RIGOL DG811波形发生器 ({name})",
                                protocol='usbtmc',
                                connection_type='usb'
                            )
                            logger.info(f"发现测试仪器: {name}")
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"扫描即插即用设备失败: {e}")
        
        return devices
    
    def _scan_usb_devices(self):
        """扫描USB设备"""
        devices = {}
        
        try:
            for device in self._wmi.InstancesOf("Win32_USBHub"):
                try:
                    name = str(device.Name) if device.Name else ""
                    device_id = str(device.DeviceID) if device.DeviceID else ""
                    
                    if 'RIGOL' in name or 'DG8' in name:
                        vid, pid = self._parse_vid_pid(device_id)
                        if vid and pid:
                            key = f"USB_{vid}_{pid}"
                            devices[key] = DeviceInfo(
                                port=key,
                                device_type='dg811_waveform_generator',
                                name=f"RIGOL波形发生器 ({name})",
                                protocol='usbtmc',
                                connection_type='usb'
                            )
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"扫描USB设备失败: {e}")
        
        return devices
    
    def _parse_vid_pid(self, device_id):
        """从设备ID解析VID和PID"""
        try:
            if 'VID_' in device_id and 'PID_' in device_id:
                vid = device_id.split('VID_')[1].split('&')[0]
                pid = device_id.split('PID_')[1].split('\\')[0]
                return vid, pid
            return None, None
        except Exception:
            return None, None
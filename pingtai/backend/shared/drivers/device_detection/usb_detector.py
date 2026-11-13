"""USB设备检测器（Windows专用）

使用Windows SetupAPI识别直接通过USB连接的设备
"""
import logging
import ctypes
from ctypes import wintypes
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class GUID(ctypes.Structure):
    """GUID结构定义"""
    _fields_ = [
        ('Data1', wintypes.DWORD),
        ('Data2', wintypes.WORD),
        ('Data3', wintypes.WORD),
        ('Data4', wintypes.BYTE * 8)
    ]


@dataclass
class UsbDeviceInfo:
    """USB设备信息"""
    vendor_id: int
    product_id: int
    vendor_name: str
    product_name: str
    device_type: str
    protocol: str = 'usb'


class SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
    """设备接口数据结构"""
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('InterfaceClassGuid', GUID),
        ('Flags', wintypes.DWORD),
        ('Reserved', wintypes.LPVOID)
    ]


class SP_DEVINFO_DATA(ctypes.Structure):
    """设备信息数据结构"""
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('ClassGuid', GUID),
        ('DevInst', wintypes.DWORD),
        ('Reserved', wintypes.LPVOID)
    ]


class UsbDeviceDetector:
    """USB设备检测器（Windows）"""
    
    def __init__(self):
        try:
            self._setupapi = ctypes.WinDLL('setupapi.dll', use_last_error=True)
            self._init_constants()
        except Exception as e:
            logger.error(f"初始化Windows API失败: {e}")
            self._setupapi = None
    
    def _init_constants(self):
        """初始化Windows API常量"""
        self.DIGCF_PRESENT = 0x00000002
        self.DIGCF_DEVICEINTERFACE = 0x00000010
        self.GUID_DEVINTERFACE_USB_DEVICE = self._get_usb_guid()
        
        self.SPDRP_DEVICEDESC = 0x00000000
        self.SPDRP_HARDWAREID = 0x00000001
        self.SPDRP_MFG = 0x00000002
        self.SPDRP_FRIENDLYNAME = 0x0000000C
    
    def _get_usb_guid(self):
        """获取USB设备接口GUID {A5DCBF10-6530-11D2-901F-00C04FB951ED}"""
        guid = GUID()
        guid.Data1 = 0xA5DCBF10
        guid.Data2 = 0x6530
        guid.Data3 = 0x11D2
        guid.Data4 = (0x90, 0x1F, 0x00, 0xC0, 0x4F, 0xB9, 0x51, 0xED)
        return guid
    
    def scan_devices(self) -> Dict[str, UsbDeviceInfo]:
        """扫描所有USB设备"""
        devices = {}
        
        if not self._setupapi:
            return devices
        
        try:
            hdi = self._setupapi.SetupDiGetClassDevsW(
                ctypes.byref(self.GUID_DEVINTERFACE_USB_DEVICE),
                None,
                None,
                self.DIGCF_PRESENT | self.DIGCF_DEVICEINTERFACE
            )
            
            if hdi == wintypes.HANDLE(-1).value:
                return devices
            
            interface_data = SP_DEVICE_INTERFACE_DATA()
            interface_data.cbSize = ctypes.sizeof(interface_data)
            
            index = 0
            while True:
                if not self._setupapi.SetupDiEnumDeviceInterfaces(
                    hdi,
                    None,
                    ctypes.byref(self.GUID_DEVINTERFACE_USB_DEVICE),
                    index,
                    ctypes.byref(interface_data)
                ):
                    break
                
                required_size = wintypes.DWORD()
                self._setupapi.SetupDiGetDeviceInterfaceDetailW(
                    hdi,
                    ctypes.byref(interface_data),
                    None,
                    0,
                    ctypes.byref(required_size),
                    None
                )
                
                detail_data = ctypes.create_string_buffer(required_size.value)
                detail_data[0:4] = required_size.value.to_bytes(4, 'little')
                
                device_info_data = SP_DEVINFO_DATA()
                device_info_data.cbSize = ctypes.sizeof(device_info_data)
                
                if self._setupapi.SetupDiGetDeviceInterfaceDetailW(
                    hdi,
                    ctypes.byref(interface_data),
                    detail_data,
                    required_size,
                    None,
                    ctypes.byref(device_info_data)
                ):
                    device_info = self._get_device_info(hdi, device_info_data)
                    if device_info:
                        key = f"USB_{device_info.vendor_id:04X}_{device_info.product_id:04X}"
                        devices[key] = device_info
                
                index += 1
            
            self._setupapi.SetupDiDestroyDeviceInfoList(hdi)
            
        except Exception as e:
            logger.error(f"扫描USB设备失败: {e}")
        
        return devices
    
    def _get_device_info(self, hdi, device_info_data):
        """获取设备信息"""
        try:
            hardware_id = self._get_device_property(hdi, device_info_data, self.SPDRP_HARDWAREID)
            if not hardware_id:
                return None
            
            vid, pid = self._parse_hardware_id(hardware_id)
            if vid is None or pid is None:
                return None
            
            product_name = self._get_device_property(hdi, device_info_data, self.SPDRP_FRIENDLYNAME)
            if not product_name:
                product_name = self._get_device_property(hdi, device_info_data, self.SPDRP_DEVICEDESC)
            
            return self._identify_device(vid, pid, product_name)
        
        except Exception as e:
            logger.debug(f"获取设备信息失败: {e}")
            return None
    
    def _get_device_property(self, hdi, device_info_data, property_id):
        """获取设备属性"""
        try:
            buffer = ctypes.create_string_buffer(1024)
            if self._setupapi.SetupDiGetDeviceRegistryPropertyW(
                hdi,
                ctypes.byref(device_info_data),
                property_id,
                None,
                buffer,
                ctypes.sizeof(buffer),
                None
            ):
                return buffer.value.decode('utf-16').strip()
            return None
        except Exception:
            return None
    
    def _parse_hardware_id(self, hardware_id):
        """从硬件ID解析VID和PID"""
        try:
            parts = hardware_id.split('\\')
            for part in parts:
                if 'VID_' in part and 'PID_' in part:
                    vid_str = part.split('VID_')[1].split('&')[0]
                    pid_str = part.split('PID_')[1]
                    return int(vid_str, 16), int(pid_str, 16)
            return None, None
        except Exception:
            return None, None
    
    def _identify_device(self, vid: int, pid: int, product_name: str) -> Optional[UsbDeviceInfo]:
        """识别USB设备类型"""
        device_map = {
            (0x0914, 0x0001): {
                'device_type': 'dg811_waveform_generator',
                'name': 'RIGOL DG811波形发生器',
                'protocol': 'usbtmc'
            },
            (0x1AB1, 0x0588): {
                'device_type': 'dg4102_waveform_generator',
                'name': 'RIGOL DG4102波形发生器',
                'protocol': 'usbtmc'
            },
            (0x0699, 0x0363): {
                'device_type': 'tektronix_oscilloscope',
                'name': 'Tektronix示波器',
                'protocol': 'usbtmc'
            },
            (0x0B3E, 0x1002): {
                'device_type': 'keysight_multimeter',
                'name': 'Keysight万用表',
                'protocol': 'usbtmc'
            }
        }
        
        key = (vid, pid)
        if key in device_map:
            info = device_map[key]
            return UsbDeviceInfo(
                vendor_id=vid,
                product_id=pid,
                vendor_name="",
                product_name=info['name'],
                device_type=info['device_type'],
                protocol=info['protocol']
            )
        
        if product_name:
            if 'RIGOL' in product_name or 'DG811' in product_name:
                return UsbDeviceInfo(
                    vendor_id=vid,
                    product_id=pid,
                    vendor_name="",
                    product_name=f"RIGOL 设备 ({product_name})",
                    device_type='dg811_waveform_generator',
                    protocol='usbtmc'
                )
            
            if 'Test and Measurement' in product_name:
                return UsbDeviceInfo(
                    vendor_id=vid,
                    product_id=pid,
                    vendor_name="",
                    product_name=f"测试仪器 ({product_name})",
                    device_type='test_instrument',
                    protocol='usbtmc'
                )
        
        return None
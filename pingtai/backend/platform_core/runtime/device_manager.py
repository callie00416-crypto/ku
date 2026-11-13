"""设备管理器

管理平台中的所有设备，包括自动发现、注册、分配等
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import threading
import time

logger = logging.getLogger(__name__)


class DeviceStatus(Enum):
    """设备状态"""
    UNKNOWN = "unknown"
    DISCOVERED = "discovered"
    REGISTERED = "registered"
    CONNECTED = "connected"
    READY = "ready"
    ERROR = "error"
    DISCONNECTED = "disconnected"


@dataclass
class Device:
    """设备"""
    device_id: str
    device_type: str
    name: str
    port: Optional[str] = None
    protocol: str = "unknown"
    baud_rate: int = 9600
    status: DeviceStatus = DeviceStatus.UNKNOWN
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DeviceManager:
    """设备管理器
    
    职责：
    - 自动发现设备
    - 注册设备
    - 管理设备生命周期
    - 分配设备给工位
    """
    
    def __init__(self):
        self._devices: Dict[str, Device] = {}
        self._lock = threading.RLock()
        self._auto_discovery_enabled = False
        self._discovery_interval = 10.0
        self._discovery_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def auto_discover_devices(self) -> List[Device]:
        """自动发现设备"""
        from shared.drivers.device_detection.serial_detector import SerialDeviceDetector
        
        logger.info("开始自动发现设备...")
        
        detector = SerialDeviceDetector()
        device_infos = detector.auto_discover(use_cache=False)
        
        new_devices = []
        
        for port, device_info in device_infos.items():
            device_id = f"{device_info.device_type}_{port.replace('COM', '')}"
            
            with self._lock:
                if device_id not in self._devices:
                    device = Device(
                        device_id=device_id,
                        device_type=device_info.device_type,
                        name=device_info.name,
                        port=device_info.port,
                        protocol=device_info.protocol,
                        baud_rate=device_info.baud_rate,
                        status=DeviceStatus.DISCOVERED
                    )
                    self._devices[device_id] = device
                    new_devices.append(device)
                    logger.info(f"发现新设备: {device.name} ({device.port})")
                else:
                    device = self._devices[device_id]
                    device.status = DeviceStatus.DISCOVERED
        
        logger.info(f"自动发现完成，共 {len(self._devices)} 个设备")
        return new_devices
    
    def register_device(self, device: Device) -> bool:
        """注册设备"""
        with self._lock:
            if device.device_id in self._devices:
                logger.warning(f"设备 {device.device_id} 已存在")
                return False
            
            device.status = DeviceStatus.REGISTERED
            self._devices[device.device_id] = device
            logger.info(f"注册设备: {device.name} ({device.device_id})")
            return True
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """获取设备"""
        with self._lock:
            return self._devices.get(device_id)
    
    def get_devices_by_type(self, device_type: str) -> List[Device]:
        """根据类型获取设备"""
        with self._lock:
            return [d for d in self._devices.values() if d.device_type == device_type]
    
    def get_all_devices(self) -> List[Device]:
        """获取所有设备"""
        with self._lock:
            return list(self._devices.values())
    
    def update_device_status(self, device_id: str, status: DeviceStatus):
        """更新设备状态"""
        with self._lock:
            device = self._devices.get(device_id)
            if device:
                device.status = status
                logger.debug(f"设备 {device_id} 状态更新为: {status.value}")
    
    def remove_device(self, device_id: str) -> bool:
        """移除设备"""
        with self._lock:
            if device_id in self._devices:
                device = self._devices.pop(device_id)
                logger.info(f"移除设备: {device.name} ({device.device_id})")
                return True
            return False
    
    def start_auto_discovery(self, interval: float = 10.0):
        """启动自动发现"""
        if self._auto_discovery_enabled:
            logger.warning("自动发现已在运行")
            return
        
        self._auto_discovery_enabled = True
        self._discovery_interval = interval
        self._stop_event.clear()
        
        self._discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        self._discovery_thread.start()
        
        logger.info(f"启动自动发现，间隔: {interval}s")
    
    def stop_auto_discovery(self):
        """停止自动发现"""
        if not self._auto_discovery_enabled:
            return
        
        self._auto_discovery_enabled = False
        self._stop_event.set()
        
        if self._discovery_thread:
            self._discovery_thread.join(timeout=5.0)
        
        logger.info("停止自动发现")
    
    def _discovery_loop(self):
        """自动发现循环"""
        while not self._stop_event.is_set():
            try:
                self.auto_discover_devices()
            except Exception as e:
                logger.error(f"自动发现失败: {e}")
            
            self._stop_event.wait(self._discovery_interval)
    
    def get_device_summary(self) -> Dict:
        """获取设备摘要"""
        with self._lock:
            summary = {
                'total': len(self._devices),
                'by_type': {},
                'by_status': {}
            }
            
            for device in self._devices.values():
                summary['by_type'][device.device_type] = summary['by_type'].get(device.device_type, 0) + 1
                summary['by_status'][device.status.value] = summary['by_status'].get(device.status.value, 0) + 1
            
            return summary
    
    def shutdown(self):
        """关闭设备管理器"""
        self.stop_auto_discovery()
        logger.info("设备管理器已关闭")


_global_device_manager: Optional[DeviceManager] = None
_manager_lock = threading.Lock()


def get_device_manager() -> DeviceManager:
    """获取全局设备管理器"""
    global _global_device_manager
    
    with _manager_lock:
        if _global_device_manager is None:
            _global_device_manager = DeviceManager()
        
        return _global_device_manager
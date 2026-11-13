"""
设备管理器 - 设备生命周期与资源管理

所属层级：Manager 层
职责：
- 设备注册/注销
- 设备状态跟踪
- 健康检查
- 异常恢复

禁止：
- 直接操作设备业务逻辑
- 在 Manager 中处理协议或通讯细节
"""
import logging
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DeviceRecord:
    """设备记录"""
    driver_id: str
    device_type: str
    status: str = "initialized"
    error_count: int = 0
    last_check: Optional[datetime] = None
    lock: threading.Lock = field(default_factory=threading.Lock)


class DeviceManager:
    """设备管理器
    
    负责设备生命周期管理，但不参与设备业务逻辑
    
    使用示例：
    >>> manager = DeviceManager()
    >>> manager.register_device('ps1', ps_device)
    >>> manager.connect('ps1')
    >>> manager.health_check_all()
    """
    
    def __init__(self):
        self._devices: Dict[str, Any] = {}
        self._records: Dict[str, DeviceRecord] = {}
        self._lock = threading.Lock()
    
    def register_device(self, driver_id: str, device: Any, device_type: str = 'unknown'):
        """注册设备
        
        Args:
            driver_id: 设备唯一标识
            device: 设备实例（BaseDevice 子类）
            device_type: 设备类型（power_supply/motor/encoder/laser）
        """
        with self._lock:
            self._devices[driver_id] = device
            self._records[driver_id] = DeviceRecord(
                driver_id=driver_id,
                device_type=device_type,
                status="registered"
            )
            logger.info(f"设备注册: {driver_id} ({device_type})")
    
    def unregister_device(self, driver_id: str):
        """注销设备"""
        with self._lock:
            if driver_id in self._devices:
                self.disconnect(driver_id)
                del self._devices[driver_id]
                del self._records[driver_id]
                logger.info(f"设备注销: {driver_id}")
    
    def connect(self, driver_id: str) -> bool:
        """连接设备"""
        device = self._devices.get(driver_id)
        if not device:
            logger.error(f"设备未注册: {driver_id}")
            return False
        
        try:
            result = device.connect()
            self._update_status(driver_id, "connected" if result else "fault")
            return result
        except Exception as e:
            logger.error(f"设备连接失败: {driver_id} - {e}")
            self._update_status(driver_id, "fault")
            return False
    
    def disconnect(self, driver_id: str):
        """断开设备"""
        device = self._devices.get(driver_id)
        if device:
            try:
                device.disconnect()
            except Exception as e:
                logger.error(f"设备断开失败: {driver_id} - {e}")
        self._update_status(driver_id, "disconnected")
    
    def get_device(self, driver_id: str) -> Optional[Any]:
        """获取设备实例"""
        return self._devices.get(driver_id)
    
    def _update_status(self, driver_id: str, status: str):
        """更新设备状态"""
        if driver_id in self._records:
            self._records[driver_id].status = status
            self._records[driver_id].last_check = datetime.now()
    
    def health_check_all(self) -> Dict[str, Any]:
        """健康检查所有设备"""
        results = {}
        for driver_id, device in self._devices.items():
            try:
                health = device.health_check()
                results[driver_id] = {
                    'status': 'ok',
                    'health': health,
                    'timestamp': datetime.now().isoformat()
                }
                self._update_status(driver_id, 'healthy')
            except Exception as e:
                logger.error(f"健康检查失败: {driver_id} - {e}")
                results[driver_id] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self._update_status(driver_id, 'unhealthy')
                if driver_id in self._records:
                    self._records[driver_id].error_count += 1
        return results
    
    def get_all_status(self) -> List[Dict[str, Any]]:
        """获取所有设备状态"""
        return [
            {
                'driver_id': r.driver_id,
                'device_type': r.device_type,
                'status': r.status,
                'error_count': r.error_count,
                'last_check': r.last_check.isoformat() if r.last_check else None
            }
            for r in self._records.values()
        ]
"""
Manager 模块 - 驱动资源管理

职责：设备状态管理、健康检查、异常恢复、驱动生命周期管理

使用示例：
>>> from drivers.manager import DeviceManager, DriverManager
>>> device_manager = DeviceManager()
>>> device_manager.register_device('ps1', device)
>>> device_manager.health_check_all()

>>> driver_manager = DriverManager()
>>> driver_manager.connect_all()
"""
from .device_manager import DeviceManager
from .driver_manager import DriverManager, get_driver_manager

__all__ = ['DeviceManager', 'DriverManager', 'get_driver_manager']
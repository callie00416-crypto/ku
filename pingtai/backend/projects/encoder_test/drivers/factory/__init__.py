"""
Factory 模块 - 驱动工厂

职责：创建 Comm/Protocol/Device 实例，禁止直接 new 具体实现类

使用示例：
>>> from drivers.factory import CommFactory, ProtocolFactory, DeviceFactory
>>> comm = CommFactory.create('rs485', port='COM4', baudrate=9600)
>>> protocol = ProtocolFactory.create('modbus', comm=comm, slave_id=1)
>>> device = DeviceFactory.create('power_supply', protocol=protocol)

统一驱动工厂：
>>> from drivers.factory import DriverFactory
>>> driver = DriverFactory.create_driver('motor', {'protocol': 'modbus'})
"""
from .comm_factory import CommFactory
from .protocol_factory import ProtocolFactory
from .device_factory import DeviceFactory
from .driver_factory import DriverFactory

__all__ = ['CommFactory', 'ProtocolFactory', 'DeviceFactory', 'DriverFactory']
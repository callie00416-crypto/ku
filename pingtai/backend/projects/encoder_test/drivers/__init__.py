"""
工业自动化驱动平台 - 标准化接口

【架构说明 - 组合优于继承】
┌─────────────────────────────────────────────────────────────────────────────┐
│  Device层     drivers/device/                                             │
│  BaseDevice   - 设备业务能力（set_voltage/move_to/read_angle）            │
│    - PowerSupply / MotorDriver / EncoderDriver / LaserDriver             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Protocol层   drivers/protocol/                                           │
│  BaseProtocol - 协议封装（read_register/write_register）                  │
│    - ModbusDriver                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  Comm层       drivers/comm/                                               │
│  BaseComm     - 字节传输（open/close/send/recv）                          │
│    - RS485Comm / TCPComm / CANComm                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  Factory层    drivers/factory/                                            │
│  Manager层    drivers/manager/                                            │
└─────────────────────────────────────────────────────────────────────────────┘

【使用示例】
>>> from shared.drivers.factory import CommFactory, ProtocolFactory, DeviceFactory
>>> comm = CommFactory.create('rs485', port='COM4', baudrate=9600)
>>> comm.open()
>>> 
>>> protocol = ProtocolFactory.create('modbus_rtu', comm=comm, slave_id=1)
>>> protocol.connect()
>>> 
>>> ps = DeviceFactory.create('power_supply', protocol=protocol)
>>> ps.connect()
>>> ps.set_voltage(5.0, channel=1)

【重要变更】
- 2025-01: 重构驱动架构，分离 BaseComm/BaseProtocol/BaseDevice
- 2025-01: 引入 DriverFactory 统一驱动创建
- 2025-01: 引入 DriverManager 统一驱动管理
- 2026-05: 架构重构，迁移到 shared/drivers/
"""
from shared.drivers.base.base_comm import BaseComm
from shared.drivers.base.base_protocol import BaseProtocol
from shared.drivers.base.base_device import BaseDevice
from projects.encoder_test.drivers.factory.driver_factory import DriverFactory
from projects.encoder_test.drivers.manager.driver_manager import DriverManager, get_driver_manager

__all__ = [
    'BaseComm',
    'BaseProtocol',
    'BaseDevice',
    'DriverFactory',
    'DriverManager',
    'get_driver_manager'
]
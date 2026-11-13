"""
pytest 配置文件

定义共享的 fixtures，供所有测试使用
"""
import pytest
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from projects.encoder_test.drivers.tests.mocks.mock_base_classes import MockComm, MockProtocol, MockDevice


@pytest.fixture
def mock_comm():
    """创建 Mock 通讯驱动"""
    return MockComm('test_comm', port='COM1', baudrate=9600)


@pytest.fixture
def mock_protocol():
    """创建 Mock 协议驱动"""
    return MockProtocol('test_protocol')


@pytest.fixture
def mock_device():
    """创建 Mock 设备"""
    return MockDevice('test_device')


@pytest.fixture
def rs485_comm():
    """创建 RS485 通讯驱动"""
    from shared.drivers.comm.rs485_comm import RS485Comm
    return RS485Comm('test_rs485', port='COM1', baudrate=9600)


@pytest.fixture
def tcp_comm():
    """创建 TCP 通讯驱动"""
    from shared.drivers.comm.tcp_comm import TCPComm
    return TCPComm('test_tcp', host='localhost', port=502)


@pytest.fixture
def can_comm():
    """创建 CAN 通讯驱动"""
    from shared.drivers.comm.can_comm import CANComm
    return CANComm('test_can', channel='can0', bitrate=500000)


@pytest.fixture
def modbus_driver(mock_comm):
    """创建 Modbus 协议驱动"""
    from shared.drivers.protocol.modbus_rtu import ModbusDriver
    return ModbusDriver('test_modbus', comm=mock_comm, slave_id=1)


@pytest.fixture
def encoder_driver(modbus_driver):
    """创建编码器设备驱动"""
    from projects.encoder_test.drivers.device.encoder.encoder import EncoderDriver
    return EncoderDriver('test_encoder', protocol=modbus_driver)


@pytest.fixture
def servo_motor(modbus_driver):
    """创建伺服电机设备驱动"""
    from projects.encoder_test.drivers.device.motor.servo_motor import ServoMotor
    return ServoMotor('test_motor', protocol=modbus_driver)


@pytest.fixture
def power_supply(modbus_driver):
    """创建电源设备驱动"""
    from projects.encoder_test.drivers.device.power_supply.power_supply import PowerSupply
    return PowerSupply('test_ps', protocol=modbus_driver)


@pytest.fixture
def laser_driver(modbus_driver):
    """创建激光设备驱动"""
    from projects.encoder_test.drivers.device.laser.laser import LaserDriver
    return LaserDriver('test_laser', protocol=modbus_driver)


@pytest.fixture
def comm_factory():
    """获取通讯工厂"""
    from projects.encoder_test.drivers.factory.comm_factory import CommFactory
    return CommFactory


@pytest.fixture
def protocol_factory():
    """获取协议工厂"""
    from projects.encoder_test.drivers.factory.protocol_factory import ProtocolFactory
    return ProtocolFactory


@pytest.fixture
def device_factory():
    """获取设备工厂"""
    from projects.encoder_test.drivers.factory.device_factory import DeviceFactory
    return DeviceFactory


@pytest.fixture
def driver_factory():
    """获取驱动工厂"""
    from projects.encoder_test.drivers.factory.driver_factory import DriverFactory
    return DriverFactory


@pytest.fixture
def device_manager():
    """创建设备管理器"""
    from projects.encoder_test.drivers.manager.device_manager import DeviceManager
    return DeviceManager()


@pytest.fixture
def driver_manager():
    """创建驱动管理器"""
    from projects.encoder_test.drivers.manager.driver_manager import DriverManager
    return DriverManager()
"""
drivers 模块统一单元测试

【测试覆盖】
1. Base层：使用Mock类测试抽象接口
2. Comm层：RS485Comm、TCPComm、CANComm
3. Protocol层：ModbusDriver
4. Device层：EncoderDriver、ServoMotor、PowerSupply、LaserDriver
5. Factory层：各类工厂
6. Manager层：设备管理、驱动管理
"""
import unittest
import sys
import os
from unittest.mock import Mock

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from projects.encoder_test.drivers.tests.mocks.mock_base_classes import MockComm, MockProtocol, MockDevice


class TestBaseComm(unittest.TestCase):
    """BaseComm 单元测试（使用Mock）"""
    
    def test_initialization(self):
        """测试初始化"""
        comm = MockComm('test_comm', port='COM1', baudrate=9600)
        self.assertEqual(comm.driver_id, 'test_comm')
        self.assertEqual(comm.port, 'COM1')
        self.assertEqual(comm.baudrate, 9600)
        self.assertFalse(comm.is_open)
    
    def test_error_handling(self):
        """测试错误处理"""
        comm = MockComm('test_comm', port='COM1', baudrate=9600)
        initial_errors = comm.error_count
        comm.increment_error()
        self.assertEqual(comm.error_count, initial_errors + 1)
        
        comm.reset_error()
        self.assertEqual(comm.error_count, 0)
    
    def test_health_check(self):
        """测试健康检查"""
        comm = MockComm('test_comm', port='COM1', baudrate=9600)
        health = comm.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('is_open', health)
        self.assertIn('error_count', health)


class TestBaseProtocol(unittest.TestCase):
    """BaseProtocol 单元测试（使用Mock）"""
    
    def test_initialization(self):
        """测试初始化"""
        protocol = MockProtocol('test_protocol')
        self.assertEqual(protocol.driver_id, 'test_protocol')
        self.assertIsNone(protocol.comm)
    
    def test_set_comm(self):
        """测试设置通讯驱动"""
        protocol = MockProtocol('test_protocol')
        comm = MockComm('test_comm')
        protocol.set_comm(comm)
        self.assertEqual(protocol.comm, comm)
    
    def test_health_check(self):
        """测试健康检查"""
        protocol = MockProtocol('test_protocol')
        health = protocol.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('is_connected', health)


class TestBaseDevice(unittest.TestCase):
    """BaseDevice 单元测试（使用Mock）"""
    
    def test_initialization(self):
        """测试初始化"""
        device = MockDevice('test_device')
        self.assertEqual(device.driver_id, 'test_device')
        self.assertIsNone(device.protocol)
    
    def test_set_protocol(self):
        """测试设置协议驱动"""
        device = MockDevice('test_device')
        protocol = MockProtocol('test_protocol')
        device.set_protocol(protocol)
        self.assertEqual(device.protocol, protocol)
    
    def test_health_check(self):
        """测试健康检查"""
        device = MockDevice('test_device')
        health = device.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('is_connected', health)


class TestCommDrivers(unittest.TestCase):
    """通讯驱动单元测试"""
    
    def test_rs485_comm_initialization(self):
        """测试RS485通讯驱动初始化"""
        from drivers.comm.rs485_comm import RS485Comm
        comm = RS485Comm(driver_id='test_rs485', port='COM3', baudrate=9600)
        self.assertEqual(comm.driver_id, 'test_rs485')
        self.assertEqual(comm.port, 'COM3')
        self.assertEqual(comm.baudrate, 9600)
    
    def test_tcp_comm_initialization(self):
        """测试TCP通讯驱动初始化"""
        from drivers.comm.tcp_comm import TCPComm
        comm = TCPComm(driver_id='test_tcp', host='localhost', port=502)
        self.assertEqual(comm.driver_id, 'test_tcp')
        self.assertEqual(comm.host, 'localhost')
        self.assertEqual(comm.port, 502)
    
    def test_can_comm_initialization(self):
        """测试CAN通讯驱动初始化"""
        from drivers.comm.can_comm import CANComm
        comm = CANComm(driver_id='test_can', channel='can0', bitrate=500000)
        self.assertEqual(comm.driver_id, 'test_can')
        self.assertEqual(comm.channel, 'can0')
        self.assertEqual(comm.bitrate, 500000)


class TestProtocolDrivers(unittest.TestCase):
    """协议驱动单元测试"""
    
    def test_modbus_driver_initialization(self):
        """测试Modbus驱动初始化"""
        from drivers.protocol.modbus_rtu import ModbusDriver
        mock_comm = Mock()
        modbus = ModbusDriver(driver_id='test_modbus', comm=mock_comm, slave_id=1)
        self.assertEqual(modbus.driver_id, 'test_modbus')
        self.assertEqual(modbus.slave_id, 1)


class TestDeviceDrivers(unittest.TestCase):
    """设备驱动单元测试"""
    
    def test_encoder_driver_initialization(self):
        """测试编码器驱动初始化"""
        from drivers.device.encoder.encoder import EncoderDriver
        mock_protocol = Mock()
        encoder = EncoderDriver(driver_id='test_encoder', protocol=mock_protocol)
        self.assertEqual(encoder.driver_id, 'test_encoder')
    
    def test_servo_motor_initialization(self):
        """测试伺服电机驱动初始化"""
        from drivers.device.motor.servo_motor import ServoMotor
        mock_protocol = Mock()
        motor = ServoMotor(driver_id='test_motor', protocol=mock_protocol)
        self.assertEqual(motor.driver_id, 'test_motor')
    
    def test_power_supply_initialization(self):
        """测试电源驱动初始化"""
        from drivers.device.power_supply.power_supply import PowerSupply
        mock_protocol = Mock()
        ps = PowerSupply(driver_id='test_ps', protocol=mock_protocol)
        self.assertEqual(ps.driver_id, 'test_ps')
    
    def test_laser_driver_initialization(self):
        """测试激光驱动初始化"""
        from drivers.device.laser.laser import LaserDriver
        mock_protocol = Mock()
        laser = LaserDriver(driver_id='test_laser', protocol=mock_protocol)
        self.assertEqual(laser.driver_id, 'test_laser')


class TestFactoryClasses(unittest.TestCase):
    """工厂类单元测试"""
    
    def test_comm_factory_registration(self):
        """测试通讯工厂注册"""
        from drivers.factory.comm_factory import CommFactory
        self.assertTrue(hasattr(CommFactory, '_registry'))
    
    def test_protocol_factory_registration(self):
        """测试协议工厂注册"""
        from drivers.factory.protocol_factory import ProtocolFactory
        self.assertTrue(hasattr(ProtocolFactory, '_registry'))
    
    def test_device_factory_registration(self):
        """测试设备工厂注册"""
        from drivers.factory.device_factory import DeviceFactory
        self.assertTrue(hasattr(DeviceFactory, '_registry'))
    
    def test_driver_factory_create(self):
        """测试驱动工厂创建"""
        from drivers.factory.driver_factory import DriverFactory
        config = {'mock': {'enabled': True}}
        drivers = DriverFactory.create_drivers_from_config(config, mock_mode=True)
        self.assertIsInstance(drivers, dict)


class TestManagerClasses(unittest.TestCase):
    """管理器类单元测试"""
    
    def test_device_manager_initialization(self):
        """测试设备管理器初始化"""
        from drivers.manager.device_manager import DeviceManager
        manager = DeviceManager()
        self.assertIsInstance(manager._devices, dict)
    
    def test_driver_manager_initialization(self):
        """测试驱动管理器初始化"""
        from drivers.manager.driver_manager import DriverManager
        manager = DriverManager()
        self.assertIsInstance(manager.drivers, dict)


# 测试套件
def suite():
    """创建测试套件"""
    test_suite = unittest.TestSuite()
    
    test_suite.addTest(unittest.makeSuite(TestBaseComm))
    test_suite.addTest(unittest.makeSuite(TestBaseProtocol))
    test_suite.addTest(unittest.makeSuite(TestBaseDevice))
    test_suite.addTest(unittest.makeSuite(TestCommDrivers))
    test_suite.addTest(unittest.makeSuite(TestProtocolDrivers))
    test_suite.addTest(unittest.makeSuite(TestDeviceDrivers))
    test_suite.addTest(unittest.makeSuite(TestFactoryClasses))
    test_suite.addTest(unittest.makeSuite(TestManagerClasses))
    
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
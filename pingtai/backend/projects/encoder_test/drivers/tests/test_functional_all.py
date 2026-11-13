"""
drivers 模块统一功能测试

【测试覆盖】
1. Comm层功能：RS485Comm、TCPComm、CANComm
2. Protocol层功能：ModbusDriver
3. Device层功能：EncoderDriver、ServoMotor、PowerSupply、LaserDriver
4. Factory层功能：各类工厂创建驱动
5. Manager层功能：设备管理、驱动管理
"""
import unittest
from unittest.mock import Mock, MagicMock
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class TestCommLayerFunctional(unittest.TestCase):
    """通讯层功能测试"""
    
    def test_rs485_comm_functional(self):
        """测试 RS485Comm 功能"""
        from drivers.comm.rs485_comm import RS485Comm
        comm = RS485Comm(driver_id='test_rs485', port='COM1', baudrate=9600)
        
        self.assertEqual(comm.driver_id, 'test_rs485')
        self.assertEqual(comm.port, 'COM1')
        self.assertEqual(comm.baudrate, 9600)
        
        health = comm.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('port', health)
        
        self.assertTrue(hasattr(comm, 'open'))
        self.assertTrue(hasattr(comm, 'close'))
        self.assertTrue(hasattr(comm, 'send'))
        self.assertTrue(hasattr(comm, 'recv'))
    
    def test_tcp_comm_functional(self):
        """测试 TCPComm 功能"""
        from drivers.comm.tcp_comm import TCPComm
        comm = TCPComm(driver_id='test_tcp', host='127.0.0.1', port=502)
        
        self.assertEqual(comm.driver_id, 'test_tcp')
        self.assertEqual(comm.host, '127.0.0.1')
        self.assertEqual(comm.port, 502)
        
        health = comm.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('host', health)
        
        self.assertTrue(hasattr(comm, 'connect'))
        self.assertTrue(hasattr(comm, 'disconnect'))
        self.assertTrue(hasattr(comm, 'send'))
        self.assertTrue(hasattr(comm, 'recv'))
    
    def test_can_comm_functional(self):
        """测试 CANComm 功能"""
        from drivers.comm.can_comm import CANComm
        comm = CANComm(driver_id='test_can', channel='can0', bitrate=500000)
        
        self.assertEqual(comm.driver_id, 'test_can')
        self.assertEqual(comm.channel, 'can0')
        self.assertEqual(comm.bitrate, 500000)
        
        health = comm.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('port', health)  # CAN使用port字段存储channel


class TestProtocolLayerFunctional(unittest.TestCase):
    """协议层功能测试"""
    
    def test_modbus_driver_functional(self):
        """测试 ModbusDriver 功能"""
        from drivers.protocol.modbus_rtu import ModbusDriver
        
        mock_comm = Mock()
        mock_comm.is_connected = Mock(return_value=True)
        mock_comm.send = Mock(return_value=True)
        
        modbus = ModbusDriver(driver_id='test_modbus', comm=mock_comm, slave_id=1)
        
        self.assertEqual(modbus.driver_id, 'test_modbus')
        self.assertEqual(modbus.slave_id, 1)
        
        health = modbus.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('slave_id', health)
        
        self.assertTrue(hasattr(modbus, 'read_register'))
        self.assertTrue(hasattr(modbus, 'write_register'))


class TestDeviceLayerFunctional(unittest.TestCase):
    """设备层功能测试"""
    
    def test_encoder_driver_functional(self):
        """测试 EncoderDriver 功能"""
        from drivers.device.encoder.encoder import EncoderDriver
        
        mock_protocol = Mock()
        encoder = EncoderDriver(driver_id='test_encoder', protocol=mock_protocol)
        
        self.assertEqual(encoder.driver_id, 'test_encoder')
        
        health = encoder.health_check()
        self.assertIn('driver_id', health)
    
    def test_servo_motor_functional(self):
        """测试 ServoMotor 功能"""
        from drivers.device.motor.servo_motor import ServoMotor
        
        mock_protocol = Mock()
        mock_protocol.write_register = Mock(return_value=True)
        
        motor = ServoMotor(driver_id='test_motor', protocol=mock_protocol)
        
        self.assertEqual(motor.driver_id, 'test_motor')
        
        health = motor.health_check()
        self.assertIn('driver_id', health)
    
    def test_power_supply_functional(self):
        """测试 PowerSupply 功能"""
        from drivers.device.power_supply.power_supply import PowerSupply
        
        mock_protocol = Mock()
        ps = PowerSupply(driver_id='test_ps', protocol=mock_protocol)
        
        self.assertEqual(ps.driver_id, 'test_ps')
        
        health = ps.health_check()
        self.assertIn('driver_id', health)
    
    def test_laser_driver_functional(self):
        """测试 LaserDriver 功能"""
        from drivers.device.laser.laser import LaserDriver
        
        mock_protocol = Mock()
        laser = LaserDriver(driver_id='test_laser', protocol=mock_protocol)
        
        self.assertEqual(laser.driver_id, 'test_laser')
        
        health = laser.health_check()
        self.assertIn('driver_id', health)


class TestFactoryFunctional(unittest.TestCase):
    """工厂层功能测试"""
    
    def test_comm_factory_create(self):
        """测试通讯工厂创建"""
        from drivers.factory.comm_factory import CommFactory
        
        config = {'port': 'COM1', 'baudrate': 9600}
        comm = CommFactory.create('rs485', **config)
        
        self.assertIsNotNone(comm)
        self.assertEqual(comm.driver_id, 'rs485')
    
    def test_protocol_factory_create(self):
        """测试协议工厂创建"""
        from drivers.factory.protocol_factory import ProtocolFactory
        
        mock_comm = Mock()
        protocol = ProtocolFactory.create('modbus_rtu', comm=mock_comm, slave_id=1)
        
        self.assertIsNotNone(protocol)
        self.assertEqual(protocol.driver_id, 'modbus')
    
    def test_device_factory_create(self):
        """测试设备工厂创建"""
        from drivers.factory.device_factory import DeviceFactory
        
        mock_protocol = Mock()
        device = DeviceFactory.create('encoder', protocol=mock_protocol)
        
        self.assertIsNotNone(device)
        self.assertEqual(device.driver_id, 'encoder')


class TestManagerFunctional(unittest.TestCase):
    """管理层功能测试"""
    
    def test_device_manager_functional(self):
        """测试 DeviceManager 功能"""
        from drivers.manager.device_manager import DeviceManager
        
        manager = DeviceManager()
        
        mock_device = Mock()
        mock_device.health_check = Mock(return_value={'status': 'ready'})
        
        manager.register_device('test_device', mock_device)
        
        self.assertIn('test_device', manager._devices)
    
    def test_driver_manager_functional(self):
        """测试 DriverManager 功能"""
        from drivers.manager.driver_manager import DriverManager
        
        manager = DriverManager()
        
        self.assertIsInstance(manager.drivers, dict)
        
        status = manager.get_all_status()
        self.assertIn('mock_enabled', status)


# 测试套件
def suite():
    """创建测试套件"""
    test_suite = unittest.TestSuite()
    
    test_suite.addTest(unittest.makeSuite(TestCommLayerFunctional))
    test_suite.addTest(unittest.makeSuite(TestProtocolLayerFunctional))
    test_suite.addTest(unittest.makeSuite(TestDeviceLayerFunctional))
    test_suite.addTest(unittest.makeSuite(TestFactoryFunctional))
    test_suite.addTest(unittest.makeSuite(TestManagerFunctional))
    
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
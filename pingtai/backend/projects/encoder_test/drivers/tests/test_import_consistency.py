"""
导入一致性测试 - 验证所有驱动类的导入是否正确

【目的】
1. 确保类名与文件名一致
2. 确保所有驱动都能正确导入
3. 确保工厂注册正确
4. 防止类名不一致导致的导入错误

【测试范围】
- Base层：BaseComm, BaseDevice, BaseProtocol, SDKDriver
- Comm层：RS485Comm, TCPComm, CANComm
- Protocol层：ModbusDriver
- Device层：EncoderDriver, ServoMotor, PowerSupply, LaserDriver
- SDK层：CameraSDKDriver, DAQSDKDriver, EncoderSDKDriver
- Factory层：CommFactory, ProtocolFactory, DeviceFactory
- Manager层：DeviceManager
"""
import unittest
import sys
import os

# 确保从项目根目录导入
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)


class TestImportConsistency(unittest.TestCase):
    """测试导入一致性"""
    
    def test_base_layer_import(self):
        """测试Base层导入"""
        from encoder_test.drivers.base import BaseComm, BaseProtocol, BaseDevice, SDKDriver
        
        self.assertIsNotNone(BaseComm)
        self.assertIsNotNone(BaseProtocol)
        self.assertIsNotNone(BaseDevice)
        self.assertIsNotNone(SDKDriver)
    
    def test_comm_layer_import(self):
        """测试Comm层导入"""
        from encoder_test.drivers.comm.rs485_comm import RS485Comm
        from encoder_test.drivers.comm.tcp_comm import TCPComm
        from encoder_test.drivers.comm.can_comm import CANComm
        
        self.assertIsNotNone(RS485Comm)
        self.assertIsNotNone(TCPComm)
        self.assertIsNotNone(CANComm)
    
    def test_protocol_layer_import(self):
        """测试Protocol层导入"""
        from encoder_test.drivers.protocol.modbus_rtu import ModbusDriver
        
        self.assertIsNotNone(ModbusDriver)
    
    def test_device_layer_import(self):
        """测试Device层导入"""
        from encoder_test.drivers.device.encoder.encoder import EncoderDriver
        from encoder_test.drivers.device.motor.servo_motor import ServoMotor
        from encoder_test.drivers.device.power_supply.power_supply import PowerSupply
        from encoder_test.drivers.device.laser.laser import LaserDriver
        
        self.assertIsNotNone(EncoderDriver)
        self.assertIsNotNone(ServoMotor)
        self.assertIsNotNone(PowerSupply)
        self.assertIsNotNone(LaserDriver)
    
    def test_device_module_import(self):
        """测试Device模块导出"""
        from encoder_test.drivers.device import PowerSupply, ServoMotor, EncoderDriver, LaserDriver
        
        self.assertIsNotNone(PowerSupply)
        self.assertIsNotNone(ServoMotor)
        self.assertIsNotNone(EncoderDriver)
        self.assertIsNotNone(LaserDriver)
    
    def test_sdk_layer_import(self):
        """测试SDK层导入"""
        from encoder_test.drivers.sdk.camera_sdk import CameraSDKDriver
        from encoder_test.drivers.sdk.daq_sdk import DAQSDKDriver
        from encoder_test.drivers.sdk.encoder_sdk import EncoderSDKDriver
        
        self.assertIsNotNone(CameraSDKDriver)
        self.assertIsNotNone(DAQSDKDriver)
        self.assertIsNotNone(EncoderSDKDriver)
    
    def test_factory_layer_import(self):
        """测试Factory层导入"""
        from encoder_test.drivers.factory.comm_factory import CommFactory
        from encoder_test.drivers.factory.protocol_factory import ProtocolFactory
        from encoder_test.drivers.factory.device_factory import DeviceFactory
        
        self.assertIsNotNone(CommFactory)
        self.assertIsNotNone(ProtocolFactory)
        self.assertIsNotNone(DeviceFactory)
    
    def test_manager_layer_import(self):
        """测试Manager层导入"""
        from encoder_test.drivers.manager.device_manager import DeviceManager
        
        self.assertIsNotNone(DeviceManager)


class TestClassNameConsistency(unittest.TestCase):
    """测试类名与文件名一致性"""
    
    def test_servo_motor_naming(self):
        """验证伺服电机类名与文件名一致"""
        from drivers.device.motor.servo_motor import ServoMotor
        
        # 类名应为 ServoMotor
        self.assertEqual(ServoMotor.__name__, 'ServoMotor')
        
        # 模块名应为 servo_motor
        self.assertEqual(ServoMotor.__module__, 'drivers.device.motor.servo_motor')
    
    def test_encoder_driver_naming(self):
        """验证编码器类名与文件名一致"""
        from drivers.device.encoder.encoder import EncoderDriver
        
        # 类名应为 EncoderDriver
        self.assertEqual(EncoderDriver.__name__, 'EncoderDriver')
        
        # 模块名应为 encoder
        self.assertEqual(EncoderDriver.__module__, 'drivers.device.encoder.encoder')
    
    def test_modbus_driver_naming(self):
        """验证Modbus类名与文件名一致"""
        from drivers.protocol.modbus_rtu import ModbusDriver
        
        # 类名应为 ModbusDriver
        self.assertEqual(ModbusDriver.__name__, 'ModbusDriver')
        
        # 模块名应为 modbus_rtu
        self.assertEqual(ModbusDriver.__module__, 'drivers.protocol.modbus_rtu')


class TestFactoryRegistration(unittest.TestCase):
    """测试工厂注册一致性"""
    
    def test_device_factory_registration(self):
        """测试设备工厂注册"""
        from drivers.factory.device_factory import DeviceFactory
        
        # 检查注册的设备类型
        self.assertTrue(hasattr(DeviceFactory, '_registry'))
        
        # 检查已注册的设备
        registry = DeviceFactory._registry
        self.assertIn('power_supply', registry)
        self.assertIn('motor', registry)
        self.assertIn('encoder', registry)
        self.assertIn('laser', registry)
    
    def test_comm_factory_registration(self):
        """测试通讯工厂注册"""
        from drivers.factory.comm_factory import CommFactory
        
        # 检查注册的通讯类型
        self.assertTrue(hasattr(CommFactory, '_registry'))
        
        # 检查已注册的通讯驱动
        registry = CommFactory._registry
        self.assertIn('rs485', registry)
        self.assertIn('tcp', registry)
        self.assertIn('can', registry)
    
    def test_protocol_factory_registration(self):
        """测试协议工厂注册"""
        from drivers.factory.protocol_factory import ProtocolFactory
        
        # 检查注册的协议类型
        self.assertTrue(hasattr(ProtocolFactory, '_registry'))
        
        # 检查已注册的协议驱动
        registry = ProtocolFactory._registry
        self.assertIn('modbus_rtu', registry)
        self.assertIn('modbus_tcp', registry)


class TestDriverInstantiation(unittest.TestCase):
    """测试驱动实例化"""
    
    def test_servo_motor_instantiation(self):
        """测试ServoMotor实例化"""
        from drivers.device.motor.servo_motor import ServoMotor
        from unittest.mock import Mock
        
        mock_protocol = Mock()
        motor = ServoMotor(protocol=mock_protocol, driver_id='test_motor')
        
        self.assertEqual(motor.driver_id, 'test_motor')
        self.assertEqual(motor.protocol, mock_protocol)
    
    def test_encoder_driver_instantiation(self):
        """测试EncoderDriver实例化"""
        from drivers.device.encoder.encoder import EncoderDriver
        from unittest.mock import Mock
        
        mock_protocol = Mock()
        encoder = EncoderDriver(protocol=mock_protocol, driver_id='test_encoder')
        
        self.assertEqual(encoder.driver_id, 'test_encoder')
        self.assertEqual(encoder.protocol, mock_protocol)
    
    def test_modbus_driver_instantiation(self):
        """测试ModbusDriver实例化"""
        from drivers.protocol.modbus_rtu import ModbusDriver
        from unittest.mock import Mock
        
        mock_comm = Mock()
        modbus = ModbusDriver(driver_id='test_modbus', comm=mock_comm, slave_id=1)
        
        self.assertEqual(modbus.driver_id, 'test_modbus')
        self.assertEqual(modbus.slave_id, 1)


if __name__ == '__main__':
    unittest.main()
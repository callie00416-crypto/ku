"""
drivers 模块统一集成测试

【测试覆盖】
1. 通讯层 + 协议层集成
2. 协议层 + 设备层集成
3. 完整驱动链路集成
4. 工厂 + 管理器集成
"""
import unittest
from unittest.mock import Mock, MagicMock
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class TestCommProtocolIntegration(unittest.TestCase):
    """通讯层与协议层集成测试"""
    
    def test_modbus_over_rs485(self):
        """测试 Modbus 协议通过 RS485 通讯"""
        from drivers.comm.rs485_comm import RS485Comm
        from drivers.protocol.modbus_rtu import ModbusDriver
        
        # 创建 RS485 通讯驱动
        comm = RS485Comm(driver_id='rs485', port='COM1', baudrate=9600)
        
        # 创建 Modbus 协议驱动并绑定通讯
        modbus = ModbusDriver(driver_id='modbus', comm=comm, slave_id=1)
        
        # 验证协议层正确使用通讯层
        self.assertEqual(modbus.comm, comm)
        self.assertEqual(modbus.slave_id, 1)
        
        # 测试健康检查
        health = modbus.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('slave_id', health)
    
    def test_modbus_over_tcp(self):
        """测试 Modbus 协议通过 TCP 通讯"""
        from drivers.comm.tcp_comm import TCPComm
        from drivers.protocol.modbus_rtu import ModbusDriver
        
        # 创建 TCP 通讯驱动
        comm = TCPComm(driver_id='tcp', host='localhost', port=502)
        
        # 创建 Modbus 协议驱动并绑定通讯
        modbus = ModbusDriver(driver_id='modbus_tcp', comm=comm, slave_id=1)
        
        self.assertEqual(modbus.comm, comm)


class TestProtocolDeviceIntegration(unittest.TestCase):
    """协议层与设备层集成测试"""
    
    def test_encoder_with_modbus(self):
        """测试编码器通过 Modbus 协议"""
        from drivers.comm.rs485_comm import RS485Comm
        from drivers.protocol.modbus_rtu import ModbusDriver
        from drivers.device.encoder.encoder import EncoderDriver
        
        # 创建完整链路
        comm = RS485Comm(driver_id='rs485', port='COM1', baudrate=9600)
        modbus = ModbusDriver(driver_id='modbus', comm=comm, slave_id=1)
        encoder = EncoderDriver(driver_id='encoder', protocol=modbus)
        
        # 验证链路完整性
        self.assertEqual(encoder.protocol, modbus)
        self.assertEqual(modbus.comm, comm)
    
    def test_motor_with_modbus(self):
        """测试电机通过 Modbus 协议"""
        from drivers.comm.rs485_comm import RS485Comm
        from drivers.protocol.modbus_rtu import ModbusDriver
        from drivers.device.motor.servo_motor import ServoMotor
        
        # 创建完整链路
        comm = RS485Comm(driver_id='rs485', port='COM1', baudrate=9600)
        modbus = ModbusDriver(driver_id='modbus', comm=comm, slave_id=1)
        motor = ServoMotor(driver_id='motor', protocol=modbus)
        
        # 验证链路完整性
        self.assertEqual(motor.protocol, modbus)
        self.assertEqual(modbus.comm, comm)


class TestFactoryManagerIntegration(unittest.TestCase):
    """工厂与管理器集成测试"""
    
    def test_factory_create_chain(self):
        """测试工厂创建驱动链"""
        from drivers.factory.comm_factory import CommFactory
        from drivers.factory.protocol_factory import ProtocolFactory
        from drivers.factory.device_factory import DeviceFactory
        
        # 使用工厂创建完整驱动链
        comm = CommFactory.create('rs485', port='COM1', baudrate=9600)
        protocol = ProtocolFactory.create('modbus_rtu', comm=comm, slave_id=1)
        device = DeviceFactory.create('encoder', protocol=protocol)
        
        # 验证创建结果
        self.assertIsNotNone(comm)
        self.assertIsNotNone(protocol)
        self.assertIsNotNone(device)
        
        # 验证链路连接
        self.assertEqual(protocol.comm, comm)
        self.assertEqual(device.protocol, protocol)
    
    def test_driver_manager_with_factory(self):
        """测试驱动管理器与工厂集成"""
        from drivers.manager.driver_manager import DriverManager
        
        # 创建驱动管理器（内部使用工厂）
        manager = DriverManager()
        
        # 验证驱动已创建
        self.assertGreater(len(manager.drivers), 0)
        
        # 测试连接所有驱动
        result = manager.connect_all()
        self.assertTrue(result)
        
        # 测试获取状态
        status = manager.get_all_status()
        self.assertIn('mock_enabled', status)


# 测试套件
def suite():
    """创建测试套件"""
    test_suite = unittest.TestSuite()
    
    test_suite.addTest(unittest.makeSuite(TestCommProtocolIntegration))
    test_suite.addTest(unittest.makeSuite(TestProtocolDeviceIntegration))
    test_suite.addTest(unittest.makeSuite(TestFactoryManagerIntegration))
    
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
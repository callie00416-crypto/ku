"""
协议层单元测试 - 提高Protocol模块覆盖率
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class TestModbusRTU(unittest.TestCase):
    """Modbus RTU协议测试"""
    
    def test_initialization(self):
        """测试初始化"""
        from encoder_test.drivers.protocol.modbus_rtu import ModbusDriver
        mock_comm = Mock()
        modbus = ModbusDriver(driver_id='test_modbus', comm=mock_comm, slave_id=1)
        self.assertEqual(modbus.driver_id, 'test_modbus')
        self.assertEqual(modbus.slave_id, 1)
    
    def test_connect_disconnect(self):
        """测试连接和断开"""
        from encoder_test.drivers.protocol.modbus_rtu import ModbusDriver
        mock_comm = Mock()
        mock_comm.open = Mock(return_value=True)
        
        modbus = ModbusDriver(driver_id='test_modbus', comm=mock_comm, slave_id=1)
        result = modbus.connect()
        self.assertTrue(result)
        
        modbus.disconnect()
    
    def test_read_register(self):
        """测试读取寄存器"""
        from encoder_test.drivers.protocol.modbus_rtu import ModbusDriver
        mock_comm = Mock()
        mock_comm.open = Mock(return_value=True)
        
        mock_result = Mock()
        mock_result.isError = Mock(return_value=False)
        mock_result.registers = [100]
        
        modbus = ModbusDriver(driver_id='test_modbus', comm=mock_comm, slave_id=1)
        modbus.connect()
        modbus._client = Mock()
        modbus._client.read_holding_registers = Mock(return_value=mock_result)
        
        result = modbus.read_register(address=0)
        self.assertEqual(result, 100)
    
    def test_read_registers(self):
        """测试读取多个寄存器"""
        from encoder_test.drivers.protocol.modbus_rtu import ModbusDriver
        mock_comm = Mock()
        mock_comm.open = Mock(return_value=True)
        
        mock_result = Mock()
        mock_result.isError = Mock(return_value=False)
        mock_result.registers = [100, 200, 300]
        
        modbus = ModbusDriver(driver_id='test_modbus', comm=mock_comm, slave_id=1)
        modbus.connect()
        modbus._client = Mock()
        modbus._client.read_holding_registers = Mock(return_value=mock_result)
        
        result = modbus.read_registers(address=0, count=3)
        self.assertEqual(result, [100, 200, 300])
    
    def test_write_register(self):
        """测试写入寄存器"""
        from encoder_test.drivers.protocol.modbus_rtu import ModbusDriver
        mock_comm = Mock()
        mock_comm.open = Mock(return_value=True)
        
        mock_result = Mock()
        mock_result.isError = Mock(return_value=False)
        
        modbus = ModbusDriver(driver_id='test_modbus', comm=mock_comm, slave_id=1)
        modbus.connect()
        modbus._client = Mock()
        modbus._client.write_register = Mock(return_value=mock_result)
        
        result = modbus.write_register(address=0, value=100)
        self.assertTrue(result)
    
    def test_read_long(self):
        """测试读取长整型"""
        from encoder_test.drivers.protocol.modbus_rtu import ModbusDriver
        mock_comm = Mock()
        mock_comm.open = Mock(return_value=True)
        
        mock_result = Mock()
        mock_result.isError = Mock(return_value=False)
        mock_result.registers = [100, 200]
        
        modbus = ModbusDriver(driver_id='test_modbus', comm=mock_comm, slave_id=1)
        modbus.connect()
        modbus._client = Mock()
        modbus._client.read_holding_registers = Mock(return_value=mock_result)
        
        result = modbus.read_long(address=0)
        self.assertIsNotNone(result)
    
    def test_write_long(self):
        """测试写入长整型"""
        from encoder_test.drivers.protocol.modbus_rtu import ModbusDriver
        mock_comm = Mock()
        mock_comm.open = Mock(return_value=True)
        
        mock_result = Mock()
        mock_result.isError = Mock(return_value=False)
        
        modbus = ModbusDriver(driver_id='test_modbus', comm=mock_comm, slave_id=1)
        modbus.connect()
        modbus._client = Mock()
        modbus._client.write_registers = Mock(return_value=mock_result)
        
        result = modbus.write_long(address=0, value=65536)
        self.assertTrue(result)
    
    def test_health_check(self):
        """测试健康检查"""
        from drivers.protocol.modbus_rtu import ModbusDriver
        mock_comm = Mock()
        modbus = ModbusDriver(driver_id='test_modbus', comm=mock_comm, slave_id=1)
        health = modbus.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('slave_id', health)
    
    def test_connect_without_comm(self):
        """测试无通讯层连接"""
        from drivers.protocol.modbus_rtu import ModbusDriver
        modbus = ModbusDriver(driver_id='test_modbus', comm=None, slave_id=1)
        result = modbus.connect()
        self.assertFalse(result)
    
    def test_read_register_not_connected(self):
        """测试未连接时读取寄存器"""
        from drivers.protocol.modbus_rtu import ModbusDriver
        mock_comm = Mock()
        modbus = ModbusDriver(driver_id='test_modbus', comm=mock_comm, slave_id=1)
        
        with self.assertRaises(ConnectionError):
            modbus.read_register(address=0)


def suite():
    """创建测试套件"""
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestModbusRTU))
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
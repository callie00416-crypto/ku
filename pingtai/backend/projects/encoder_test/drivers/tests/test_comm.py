"""
通讯层单元测试 - 提高Comm模块覆盖率
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class TestRS485Comm(unittest.TestCase):
    """RS485通讯测试"""
    
    def test_initialization(self):
        """测试初始化"""
        from encoder_test.drivers.comm.rs485_comm import RS485Comm
        comm = RS485Comm(driver_id='test_rs485', port='COM3', baudrate=9600)
        self.assertEqual(comm.driver_id, 'test_rs485')
        self.assertEqual(comm.port, 'COM3')
        self.assertEqual(comm.baudrate, 9600)
    
    def test_open_close(self):
        """测试打开和关闭"""
        from encoder_test.drivers.comm.rs485_comm import RS485Comm
        comm = RS485Comm(driver_id='test_rs485', port='COM3', baudrate=9600)
        
        result = comm.open()
        self.assertFalse(result)  # 未安装serial库时返回False
        
        comm.close()
    
    def test_send_recv(self):
        """测试发送和接收"""
        from encoder_test.drivers.comm.rs485_comm import RS485Comm
        comm = RS485Comm(driver_id='test_rs485', port='COM3', baudrate=9600)
        
        result = comm.send(b'hello')
        self.assertEqual(result, 0)
        
        data = comm.recv(1024)
        self.assertEqual(data, b'')
    
    def test_send_recv_with_timeout(self):
        """测试带超时的收发"""
        from encoder_test.drivers.comm.rs485_comm import RS485Comm
        comm = RS485Comm(driver_id='test_rs485', port='COM3', baudrate=9600)
        
        data = comm.recv(1024, timeout=0.1)
        self.assertEqual(data, b'')
    
    def test_send_recv_method(self):
        """测试send_recv方法"""
        from drivers.comm.rs485_comm import RS485Comm
        comm = RS485Comm(driver_id='test_rs485', port='COM3', baudrate=9600)
        
        data = comm.send_recv(b'hello', timeout=0.1)
        self.assertEqual(data, b'')
    
    def test_health_check(self):
        """测试健康检查"""
        from drivers.comm.rs485_comm import RS485Comm
        comm = RS485Comm(driver_id='test_rs485', port='COM3', baudrate=9600)
        health = comm.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('port', health)


class TestTCPComm(unittest.TestCase):
    """TCP通讯测试"""
    
    def test_initialization(self):
        """测试初始化"""
        from encoder_test.drivers.comm.tcp_comm import TCPComm
        comm = TCPComm(driver_id='test_tcp', host='127.0.0.1', port=502)
        self.assertEqual(comm.driver_id, 'test_tcp')
        self.assertEqual(comm.host, '127.0.0.1')
        self.assertEqual(comm.port, 502)
    
    def test_connect_disconnect(self):
        """测试连接和断开"""
        from encoder_test.drivers.comm.tcp_comm import TCPComm
        comm = TCPComm(driver_id='test_tcp', host='127.0.0.1', port=502)
        
        result = comm.connect()
        self.assertFalse(result)  # 连接失败
        
        comm.disconnect()
    
    def test_send_recv(self):
        """测试发送和接收"""
        from drivers.comm.tcp_comm import TCPComm
        comm = TCPComm(driver_id='test_tcp', host='127.0.0.1', port=502)
        
        result = comm.send(b'hello')
        self.assertEqual(result, 0)
        
        data = comm.recv(1024)
        self.assertEqual(data, b'')
    
    def test_send_recv_with_timeout(self):
        """测试带超时的收发"""
        from drivers.comm.tcp_comm import TCPComm
        comm = TCPComm(driver_id='test_tcp', host='127.0.0.1', port=502)
        
        data = comm.recv(1024, timeout=0.1)
        self.assertEqual(data, b'')
    
    def test_health_check(self):
        """测试健康检查"""
        from drivers.comm.tcp_comm import TCPComm
        comm = TCPComm(driver_id='test_tcp', host='127.0.0.1', port=502)
        health = comm.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('host', health)


class TestCANComm(unittest.TestCase):
    """CAN通讯测试"""
    
    def test_initialization(self):
        """测试初始化"""
        from encoder_test.drivers.comm.can_comm import CANComm
        comm = CANComm(driver_id='test_can', channel='can0', bitrate=500000)
        self.assertEqual(comm.driver_id, 'test_can')
        self.assertEqual(comm.channel, 'can0')
        self.assertEqual(comm.bitrate, 500000)
    
    def test_open_close(self):
        """测试打开和关闭"""
        from drivers.comm.can_comm import CANComm
        comm = CANComm(driver_id='test_can', channel='can0', bitrate=500000)
        
        result = comm.open()
        self.assertFalse(result)
        
        comm.close()
    
    def test_send_recv(self):
        """测试发送和接收"""
        from drivers.comm.can_comm import CANComm
        comm = CANComm(driver_id='test_can', channel='can0', bitrate=500000)
        
        result = comm.send(b'hello')
        self.assertEqual(result, 0)
        
        data = comm.recv(1024)
        self.assertEqual(data, b'')
    
    def test_health_check(self):
        """测试健康检查"""
        from drivers.comm.can_comm import CANComm
        comm = CANComm(driver_id='test_can', channel='can0', bitrate=500000)
        health = comm.health_check()
        self.assertIn('driver_id', health)


def suite():
    """创建测试套件"""
    test_suite = unittest.TestSuite()
    
    test_suite.addTest(unittest.makeSuite(TestRS485Comm))
    test_suite.addTest(unittest.makeSuite(TestTCPComm))
    test_suite.addTest(unittest.makeSuite(TestCANComm))
    
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
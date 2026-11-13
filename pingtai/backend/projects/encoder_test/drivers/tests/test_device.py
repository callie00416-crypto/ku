"""
设备层单元测试 - 提高Device模块覆盖率
"""
import unittest
from unittest.mock import Mock, MagicMock
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class TestEncoderDriver(unittest.TestCase):
    """编码器驱动测试"""
    
    def test_initialization(self):

        """测试初始化"""
        from encoder_test.drivers.device.encoder.encoder import EncoderDriver
        mock_protocol = Mock()
        encoder = EncoderDriver(driver_id='test_encoder', protocol=mock_protocol)
        self.assertEqual(encoder.driver_id, 'test_encoder')
    
    def test_connect_disconnect(self):
        """测试连接和断开"""
        from encoder_test.drivers.device.encoder.encoder import EncoderDriver
        mock_protocol = Mock()
        encoder = EncoderDriver(driver_id='test_encoder', protocol=mock_protocol)
        
        result = encoder.connect()
        self.assertTrue(result)
        self.assertTrue(encoder.is_connected())
        
        encoder.disconnect()
        self.assertFalse(encoder.is_connected())
    
    def test_read_data(self):
        """测试读取数据"""
        from encoder_test.drivers.device.encoder.encoder import EncoderDriver
        mock_protocol = Mock()
        mock_protocol.read_register = Mock(return_value=100)
        
        encoder = EncoderDriver(driver_id='test_encoder', protocol=mock_protocol)
        encoder.connect()
        data = encoder.read_data()
        self.assertIn('angle', data)
        self.assertIn('speed', data)
    
    def test_write_data(self):
        """测试写入数据"""
        from encoder_test.drivers.device.encoder.encoder import EncoderDriver
        mock_protocol = Mock()
        encoder = EncoderDriver(driver_id='test_encoder', protocol=mock_protocol)
        
        result = encoder.write_data({'test': 'data'})
        self.assertTrue(result)
    
    def test_reset(self):
        """测试复位"""
        from encoder_test.drivers.device.encoder.encoder import EncoderDriver
        mock_protocol = Mock()
        encoder = EncoderDriver(driver_id='test_encoder', protocol=mock_protocol)
        
        encoder.reset()
    
    def test_health_check(self):
        """测试健康检查"""
        from encoder_test.drivers.device.encoder.encoder import EncoderDriver
        mock_protocol = Mock()
        encoder = EncoderDriver(driver_id='test_encoder', protocol=mock_protocol)
        health = encoder.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('resolution', health)


class TestServoMotor(unittest.TestCase):
    """伺服电机驱动测试"""
    
    def test_initialization(self):
        """测试初始化"""
        from encoder_test.drivers.device.motor.servo_motor import ServoMotor
        mock_protocol = Mock()
        motor = ServoMotor(driver_id='test_motor', protocol=mock_protocol)
        self.assertEqual(motor.driver_id, 'test_motor')
    
    def test_connect_disconnect(self):
        """测试连接和断开"""
        from encoder_test.drivers.device.motor.servo_motor import ServoMotor
        mock_protocol = Mock()
        motor = ServoMotor(driver_id='test_motor', protocol=mock_protocol)
        
        result = motor.connect()
        self.assertTrue(result)
        self.assertTrue(motor.is_connected())
        
        motor.disconnect()
        self.assertFalse(motor.is_connected())
    
    def test_enable_disable(self):
        """测试使能和禁用"""
        from encoder_test.drivers.device.motor.servo_motor import ServoMotor
        mock_protocol = Mock()
        
        motor = ServoMotor(driver_id='test_motor', protocol=mock_protocol)
        result = motor.enable()
        self.assertTrue(result)
        
        motor.disable()
    
    def test_start_stop(self):
        """测试启动和停止"""
        from drivers.device.motor.servo_motor import ServoMotor
        mock_protocol = Mock()
        
        motor = ServoMotor(driver_id='test_motor', protocol=mock_protocol)
        result = motor.start(speed=1000)
        self.assertTrue(result)
        
        motor.stop()
    
    def test_read_data(self):
        """测试读取数据"""
        from drivers.device.motor.servo_motor import ServoMotor
        mock_protocol = Mock()
        
        motor = ServoMotor(driver_id='test_motor', protocol=mock_protocol)
        data = motor.read_data()
        self.assertIn('position', data)
        self.assertIn('speed', data)
        self.assertIn('running', data)
        self.assertIn('enabled', data)
    
    def test_write_data(self):
        """测试写入数据"""
        from drivers.device.motor.servo_motor import ServoMotor
        mock_protocol = Mock()
        motor = ServoMotor(driver_id='test_motor', protocol=mock_protocol)
        
        result = motor.write_data({'speed': 1000, 'position': 100})
        self.assertTrue(result)
    
    def test_reset(self):
        """测试复位"""
        from drivers.device.motor.servo_motor import ServoMotor
        mock_protocol = Mock()
        motor = ServoMotor(driver_id='test_motor', protocol=mock_protocol)
        
        motor.reset()


class TestLaserDriver(unittest.TestCase):
    """激光设备驱动测试"""
    
    def test_initialization(self):
        """测试初始化"""
        from drivers.device.laser.laser import LaserDriver
        mock_protocol = Mock()
        laser = LaserDriver(driver_id='test_laser', protocol=mock_protocol)
        self.assertEqual(laser.driver_id, 'test_laser')
    
    def test_connect_disconnect(self):
        """测试连接和断开"""
        from drivers.device.laser.laser import LaserDriver
        mock_protocol = Mock()
        laser = LaserDriver(driver_id='test_laser', protocol=mock_protocol)
        
        result = laser.connect()
        self.assertTrue(result)
        self.assertTrue(laser.is_connected())
        
        laser.disconnect()
        self.assertFalse(laser.is_connected())
    
    def test_calibrate(self):
        """测试校准"""
        from drivers.device.laser.laser import LaserDriver
        mock_protocol = Mock()
        
        laser = LaserDriver(driver_id='test_laser', protocol=mock_protocol)
        result = laser.calibrate()
        self.assertTrue(result)
    
    def test_read_angle(self):
        """测试读取角度"""
        from drivers.device.laser.laser import LaserDriver
        mock_protocol = Mock()
        
        laser = LaserDriver(driver_id='test_laser', protocol=mock_protocol)
        angle = laser.read_angle()
        self.assertEqual(angle, 0.0)
    
    def test_read_data(self):
        """测试读取数据"""
        from drivers.device.laser.laser import LaserDriver
        mock_protocol = Mock()
        mock_protocol.read_register = Mock(return_value=1000)
        
        laser = LaserDriver(driver_id='test_laser', protocol=mock_protocol)
        laser.connect()
        data = laser.read_data()
        self.assertIn('angle', data)
        self.assertIn('reference', data)
    
    def test_write_data(self):
        """测试写入数据"""
        from drivers.device.laser.laser import LaserDriver
        mock_protocol = Mock()
        laser = LaserDriver(driver_id='test_laser', protocol=mock_protocol)
        
        result = laser.write_data({'test': 'data'})
        self.assertTrue(result)
    
    def test_reset(self):
        """测试复位"""
        from drivers.device.laser.laser import LaserDriver
        mock_protocol = Mock()
        laser = LaserDriver(driver_id='test_laser', protocol=mock_protocol)
        
        laser.reset()
    
    def test_health_check(self):
        """测试健康检查"""
        from drivers.device.laser.laser import LaserDriver
        mock_protocol = Mock()
        laser = LaserDriver(driver_id='test_laser', protocol=mock_protocol)
        health = laser.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('precision', health)


class TestPowerSupply(unittest.TestCase):
    """电源设备驱动测试"""
    
    def test_initialization(self):
        """测试初始化"""
        from drivers.device.power_supply.power_supply import PowerSupply
        mock_protocol = Mock()
        ps = PowerSupply(driver_id='test_ps', protocol=mock_protocol)
        self.assertEqual(ps.driver_id, 'test_ps')
    
    def test_connect_disconnect(self):
        """测试连接和断开"""
        from drivers.device.power_supply.power_supply import PowerSupply
        mock_protocol = Mock()
        ps = PowerSupply(driver_id='test_ps', protocol=mock_protocol)
        
        result = ps.connect()
        self.assertTrue(result)
        
        ps.disconnect()
    
    def test_read_voltage(self):
        """测试读取电压"""
        from drivers.device.power_supply.power_supply import PowerSupply
        mock_protocol = Mock()
        mock_protocol.read_register = Mock(return_value=1200)
        
        ps = PowerSupply(driver_id='test_ps', protocol=mock_protocol)
        ps.connect()
        voltage = ps.read_voltage()
        self.assertEqual(voltage, 12.0)
    
    def test_read_current(self):
        """测试读取电流"""
        from drivers.device.power_supply.power_supply import PowerSupply
        mock_protocol = Mock()
        mock_protocol.read_register = Mock(return_value=500)
        
        ps = PowerSupply(driver_id='test_ps', protocol=mock_protocol)
        ps.connect()
        current = ps.read_current()
        self.assertEqual(current, 5.0)
    
    def test_read_status(self):
        """测试读取状态"""
        from drivers.device.power_supply.power_supply import PowerSupply
        mock_protocol = Mock()
        mock_protocol.read_register = Mock(return_value=1)
        
        ps = PowerSupply(driver_id='test_ps', protocol=mock_protocol)
        ps.connect()
        status = ps.read_status()
        self.assertIn('channel', status)
    
    def test_read_data(self):
        """测试读取数据"""
        from drivers.device.power_supply.power_supply import PowerSupply
        mock_protocol = Mock()
        mock_protocol.read_register = Mock(side_effect=[1200, 500])
        
        ps = PowerSupply(driver_id='test_ps', protocol=mock_protocol)
        ps.connect()
        data = ps.read_data()
        self.assertIn('voltage', data)
        self.assertIn('current', data)
    
    def test_write_data(self):
        """测试写入数据"""
        from drivers.device.power_supply.power_supply import PowerSupply
        mock_protocol = Mock()
        mock_protocol.write_register = Mock(return_value=True)
        
        ps = PowerSupply(driver_id='test_ps', protocol=mock_protocol)
        ps.connect()
        result = ps.write_data({'voltage': 12.0, 'current': 2.0})
        self.assertTrue(result)
    
    def test_health_check(self):
        """测试健康检查"""
        from drivers.device.power_supply.power_supply import PowerSupply
        mock_protocol = Mock()
        ps = PowerSupply(driver_id='test_ps', protocol=mock_protocol)
        health = ps.health_check()
        self.assertIn('driver_id', health)


def suite():
    """创建测试套件"""
    test_suite = unittest.TestSuite()
    
    test_suite.addTest(unittest.makeSuite(TestEncoderDriver))
    test_suite.addTest(unittest.makeSuite(TestServoMotor))
    test_suite.addTest(unittest.makeSuite(TestLaserDriver))
    test_suite.addTest(unittest.makeSuite(TestPowerSupply))
    
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
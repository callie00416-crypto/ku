"""
SDK层单元测试 - 提高SDK模块覆盖率
"""
import unittest
from unittest.mock import Mock, MagicMock
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class TestEncoderSDK(unittest.TestCase):
    """编码器SDK测试"""
    
    def test_initialization(self):
        """测试编码器SDK初始化"""
        from encoder_test.drivers.sdk.encoder_sdk import EncoderSDKDriver
        sdk = EncoderSDKDriver(driver_id='test_encoder_sdk')
        self.assertEqual(sdk.driver_id, 'test_encoder_sdk')
    
    def test_connect_disconnect(self):
        """测试连接和断开"""
        from encoder_test.drivers.sdk.encoder_sdk import EncoderSDKDriver
        sdk = EncoderSDKDriver(driver_id='test_encoder_sdk')
        
        result = sdk.connect()
        self.assertFalse(result)  # 未安装SDK时返回False
        
        sdk.disconnect()
    
    def test_read_angle(self):
        """测试读取角度"""
        from encoder_test.drivers.sdk.encoder_sdk import EncoderSDKDriver
        sdk = EncoderSDKDriver(driver_id='test_encoder_sdk')
        angle = sdk.read_angle()
        self.assertEqual(angle, 0.0)
    
    def test_read_speed(self):
        """测试读取速度"""
        from encoder_test.drivers.sdk.encoder_sdk import EncoderSDKDriver
        sdk = EncoderSDKDriver(driver_id='test_encoder_sdk')
        speed = sdk.read_speed()
        self.assertEqual(speed, 0.0)
    
    def test_read_position(self):
        """测试读取位置"""
        from encoder_test.drivers.sdk.encoder_sdk import EncoderSDKDriver
        sdk = EncoderSDKDriver(driver_id='test_encoder_sdk')
        position = sdk.read_position()
        self.assertEqual(position, 0)
    
    def test_health_check(self):
        """测试健康检查"""
        from encoder_test.drivers.sdk.encoder_sdk import EncoderSDKDriver
        sdk = EncoderSDKDriver(driver_id='test_encoder_sdk')
        health = sdk.health_check()
        self.assertIn('driver_id', health)


class TestCameraSDK(unittest.TestCase):
    """相机SDK测试"""
    
    def test_initialization(self):
        """测试相机SDK初始化"""
        from encoder_test.drivers.sdk.camera_sdk import CameraSDKDriver
        sdk = CameraSDKDriver(driver_id='test_camera_sdk')
        self.assertEqual(sdk.driver_id, 'test_camera_sdk')
    
    def test_connect_disconnect(self):
        """测试连接和断开"""
        from encoder_test.drivers.sdk.camera_sdk import CameraSDKDriver
        sdk = CameraSDKDriver(driver_id='test_camera_sdk')
        
        result = sdk.connect()
        self.assertFalse(result)
        
        sdk.disconnect()
    
    def test_capture(self):
        """测试拍照"""
        from encoder_test.drivers.sdk.camera_sdk import CameraSDKDriver
        sdk = CameraSDKDriver(driver_id='test_camera_sdk')
        image = sdk.capture()
        self.assertIsNone(image)
    
    def test_set_exposure(self):
        """测试设置曝光"""
        from encoder_test.drivers.sdk.camera_sdk import CameraSDKDriver
        sdk = CameraSDKDriver(driver_id='test_camera_sdk')
        result = sdk.set_exposure(100)
        self.assertFalse(result)
    
    def test_set_gain(self):
        """测试设置增益"""
        from encoder_test.drivers.sdk.camera_sdk import CameraSDKDriver
        sdk = CameraSDKDriver(driver_id='test_camera_sdk')
        result = sdk.set_gain(50)
        self.assertFalse(result)
    
    def test_health_check(self):
        """测试健康检查"""
        from drivers.sdk.camera_sdk import CameraSDKDriver
        sdk = CameraSDKDriver(driver_id='test_camera_sdk')
        health = sdk.health_check()
        self.assertIn('driver_id', health)


class TestDAQSDK(unittest.TestCase):
    """DAQ SDK测试"""
    
    def test_initialization(self):
        """测试DAQ SDK初始化"""
        from drivers.sdk.daq_sdk import DAQSDKDriver
        sdk = DAQSDKDriver(driver_id='test_daq_sdk')
        self.assertEqual(sdk.driver_id, 'test_daq_sdk')
    
    def test_connect_disconnect(self):
        """测试连接和断开"""
        from drivers.sdk.daq_sdk import DAQSDKDriver
        sdk = DAQSDKDriver(driver_id='test_daq_sdk')
        
        result = sdk.connect()
        self.assertFalse(result)
        
        sdk.disconnect()
    
    def test_read_analog(self):
        """测试读取模拟量"""
        from drivers.sdk.daq_sdk import DAQSDKDriver
        sdk = DAQSDKDriver(driver_id='test_daq_sdk')
        value = sdk.read_analog(0)
        self.assertEqual(value, 0.0)
    
    def test_write_analog(self):
        """测试写入模拟量"""
        from drivers.sdk.daq_sdk import DAQSDKDriver
        sdk = DAQSDKDriver(driver_id='test_daq_sdk')
        result = sdk.write_analog(0, 5.0)
        self.assertFalse(result)
    
    def test_read_digital(self):
        """测试读取数字量"""
        from drivers.sdk.daq_sdk import DAQSDKDriver
        sdk = DAQSDKDriver(driver_id='test_daq_sdk')
        value = sdk.read_digital(0)
        self.assertEqual(value, 0)
    
    def test_write_digital(self):
        """测试写入数字量"""
        from drivers.sdk.daq_sdk import DAQSDKDriver
        sdk = DAQSDKDriver(driver_id='test_daq_sdk')
        result = sdk.write_digital(0, 1)
        self.assertFalse(result)
    
    def test_read_multiple_channels(self):
        """测试读取多通道"""
        from drivers.sdk.daq_sdk import DAQSDKDriver
        sdk = DAQSDKDriver(driver_id='test_daq_sdk')
        values = sdk.read_multiple_channels([0, 1, 2])
        self.assertEqual(values, [0.0, 0.0, 0.0])
    
    def test_health_check(self):
        """测试健康检查"""
        from drivers.sdk.daq_sdk import DAQSDKDriver
        sdk = DAQSDKDriver(driver_id='test_daq_sdk')
        health = sdk.health_check()
        self.assertIn('driver_id', health)


def suite():
    """创建测试套件"""
    test_suite = unittest.TestSuite()
    
    test_suite.addTest(unittest.makeSuite(TestEncoderSDK))
    test_suite.addTest(unittest.makeSuite(TestCameraSDK))
    test_suite.addTest(unittest.makeSuite(TestDAQSDK))
    
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
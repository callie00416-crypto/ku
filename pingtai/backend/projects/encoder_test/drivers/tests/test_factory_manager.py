"""
工厂和管理器层单元测试 - 提高Factory和Manager模块覆盖率
"""
import unittest
from unittest.mock import Mock, MagicMock
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class TestDriverFactory(unittest.TestCase):
    """驱动工厂测试"""
    
    def test_initialization(self):
        """测试初始化"""
        from encoder_test.drivers.factory.driver_factory import DriverFactory
        factory = DriverFactory()
        self.assertIsNotNone(factory)
    
    def test_get(self):
        """测试获取驱动"""
        from encoder_test.drivers.factory.driver_factory import DriverFactory
        factory = DriverFactory()
        
        driver = factory.get('rs485')
        self.assertIsNotNone(driver)
    
    def test_get_all(self):
        """测试获取所有驱动"""
        from drivers.factory.driver_factory import DriverFactory
        factory = DriverFactory()
        
        all_drivers = factory.get_all()
        self.assertIsInstance(all_drivers, dict)


class TestDriverManager(unittest.TestCase):
    """驱动管理器测试"""
    
    def test_initialization(self):
        """测试初始化"""
        from encoder_test.drivers.manager.driver_manager import DriverManager
        manager = DriverManager()
        self.assertIsNotNone(manager)
    
    def test_get_driver(self):
        """测试获取驱动"""
        from encoder_test.drivers.manager.driver_manager import DriverManager
        manager = DriverManager()
        
        driver = manager.get_driver('rs485')
        self.assertIsNotNone(driver)
    
    def test_connect_all(self):
        """测试连接所有驱动"""
        from encoder_test.drivers.manager.driver_manager import DriverManager
        manager = DriverManager()
        
        manager.connect_all()
    
    def test_disconnect_all(self):
        """测试断开所有驱动"""
        from encoder_test.drivers.manager.driver_manager import DriverManager
        manager = DriverManager()
        
        manager.disconnect_all()
    
    def test_get_all_status(self):
        """测试获取所有驱动状态"""
        from encoder_test.drivers.manager.driver_manager import DriverManager
        manager = DriverManager()
        
        status = manager.get_all_status()
        self.assertIsInstance(status, dict)
    
    def test_get_fault_drivers(self):
        """测试获取故障驱动"""
        from drivers.manager.driver_manager import DriverManager
        manager = DriverManager()
        
        fault_drivers = manager.get_fault_drivers()
        self.assertIsInstance(fault_drivers, list)


class TestDeviceManager(unittest.TestCase):
    """设备管理器测试"""
    
    def test_initialization(self):
        """测试初始化"""
        from encoder_test.drivers.manager.device_manager import DeviceManager
        manager = DeviceManager()
        self.assertIsNotNone(manager)
    
    def test_register_device(self):
        """测试注册设备"""
        from encoder_test.drivers.manager.device_manager import DeviceManager
        from encoder_test.drivers.mock.mock_encoder import MockEncoder
        
        manager = DeviceManager()
        mock_encoder = MockEncoder(driver_id='encoder_001')
        
        manager.register_device('encoder_001', mock_encoder, 'encoder')
        self.assertIn('encoder_001', manager._devices)
    
    def test_unregister_device(self):
        """测试注销设备"""
        from encoder_test.drivers.manager.device_manager import DeviceManager
        from encoder_test.drivers.mock.mock_encoder import MockEncoder
        
        manager = DeviceManager()
        mock_encoder = MockEncoder(driver_id='encoder_001')
        
        manager.register_device('encoder_001', mock_encoder, 'encoder')
        manager.unregister_device('encoder_001')
        self.assertNotIn('encoder_001', manager._devices)
    
    def test_get_device(self):
        """测试获取设备"""
        from encoder_test.drivers.manager.device_manager import DeviceManager
        from encoder_test.drivers.mock.mock_encoder import MockEncoder
        
        manager = DeviceManager()
        mock_encoder = MockEncoder(driver_id='encoder_001')
        
        manager.register_device('encoder_001', mock_encoder, 'encoder')
        device = manager.get_device('encoder_001')
        self.assertEqual(device.driver_id, 'encoder_001')
    
    def test_connect(self):
        """测试连接设备"""
        from drivers.manager.device_manager import DeviceManager
        from drivers.mock.mock_encoder import MockEncoder
        
        manager = DeviceManager()
        mock_encoder = MockEncoder(driver_id='encoder_001')
        
        manager.register_device('encoder_001', mock_encoder, 'encoder')
        result = manager.connect('encoder_001')
    
    def test_health_check_all(self):
        """测试健康检查所有设备"""
        from drivers.manager.device_manager import DeviceManager
        from drivers.mock.mock_encoder import MockEncoder
        
        manager = DeviceManager()
        mock_encoder = MockEncoder(driver_id='encoder_001')
        
        manager.register_device('encoder_001', mock_encoder, 'encoder')
        results = manager.health_check_all()
        self.assertIsInstance(results, dict)
    
    def test_get_all_status(self):
        """测试获取所有设备状态"""
        from drivers.manager.device_manager import DeviceManager
        from drivers.mock.mock_encoder import MockEncoder
        
        manager = DeviceManager()
        mock_encoder = MockEncoder(driver_id='encoder_001')
        
        manager.register_device('encoder_001', mock_encoder, 'encoder')
        status = manager.get_all_status()
        self.assertIsInstance(status, list)


def suite():
    """创建测试套件"""
    test_suite = unittest.TestSuite()
    
    test_suite.addTest(unittest.makeSuite(TestDriverFactory))
    test_suite.addTest(unittest.makeSuite(TestDriverManager))
    test_suite.addTest(unittest.makeSuite(TestDeviceManager))
    
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
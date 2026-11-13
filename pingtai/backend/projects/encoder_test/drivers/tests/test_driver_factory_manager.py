"""
驱动工厂和管理器测试脚本

验证 DriverFactory 和 DriverManager 的基本功能
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from encoder_test.drivers.factory.driver_factory import DriverFactory
from encoder_test.drivers.manager.driver_manager import DriverManager, get_driver_manager


def test_driver_factory():
    """测试 DriverFactory"""
    print("=== 测试 DriverFactory ===")
    
    # 测试创建 Mock 驱动
    config = {
        'mock': {
            'enabled': True,
            'serial_port': 'COM3',
            'serial_baudrate': 9600,
            'serial_mode': 'normal'
        }
    }
    
    drivers = DriverFactory.create_drivers_from_config(config, mock_mode=True)
    print(f"创建的 Mock 驱动数量: {len(drivers)}")
    
    # 检查是否包含了预期的驱动类型
    expected_drivers = ['rs485', 'can', 'modbus', 'encoder', 'motor']
    for driver_name in expected_drivers:
        if driver_name in drivers:
            print(f"✓ {driver_name} 驱动创建成功: {type(drivers[driver_name]).__name__}")
        else:
            print(f"✗ {driver_name} 驱动创建失败")
    
    print()


def test_driver_manager():
    """测试 DriverManager"""
    print("=== 测试 DriverManager ===")
    
    # 创建驱动管理器
    manager = DriverManager()
    print(f"驱动管理器初始化完成，Mock模式: {manager.mock_enabled}")
    
    # 连接所有驱动
    success = manager.connect_all()
    print(f"连接所有驱动: {'成功' if success else '失败'}")
    
    # 获取驱动状态
    status = manager.get_all_status()
    print(f"获取驱动状态: {len(status)-1} 个驱动")  # 减1是因为mock_enabled不算驱动
    
    # 获取故障驱动
    fault_drivers = manager.get_fault_drivers()
    print(f"故障驱动: {len(fault_drivers)} 个")
    
    # 测试获取特定驱动
    rs485_driver = manager.get_driver('rs485')
    if rs485_driver:
        print(f"✓ 获取 rs485 驱动成功: {type(rs485_driver).__name__}")
    else:
        print("✗ 获取 rs485 驱动失败")
    
    # 关闭管理器
    manager.close()
    print("驱动管理器已关闭")
    
    print()


def test_get_driver_manager():
    """测试全局驱动管理器获取函数"""
    print("=== 测试全局驱动管理器 ===")
    
    # 第一次获取
    manager1 = get_driver_manager()
    print(f"第一次获取驱动管理器: {id(manager1)}")
    
    # 第二次获取（应该是同一个实例）
    manager2 = get_driver_manager()
    print(f"第二次获取驱动管理器: {id(manager2)}")
    
    print(f"两次获取的是同一个实例: {'是' if manager1 is manager2 else '否'}")
    
    print()


if __name__ == '__main__':
    test_driver_factory()
    test_driver_manager()
    test_get_driver_manager()
    print("=== 所有测试完成 ===")
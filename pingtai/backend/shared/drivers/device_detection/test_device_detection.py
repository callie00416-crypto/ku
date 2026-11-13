"""测试设备自动发现功能"""
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, project_root)

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from backend.shared.drivers.device_detection.serial_detector import SerialDeviceDetector
from backend.platform.runtime.device_manager import get_device_manager


def test_serial_detector():
    """测试串口检测器"""
    print("=" * 70)
    print("测试串口设备检测器")
    print("=" * 70)
    
    detector = SerialDeviceDetector()
    
    print("\n1. 扫描所有串口...")
    ports = detector.scan_all_ports()
    print(f"找到 {len(ports)} 个串口:")
    for port in ports:
        print(f"  - {port.port}: {port.description}")
        print(f"    VID: {port.vid}, PID: {port.pid}")
    
    print("\n2. 自动发现设备...")
    devices = detector.auto_discover(use_cache=False)
    print(f"识别到 {len(devices)} 个设备:")
    for port, device in devices.items():
        print(f"  - {port}:")
        print(f"    类型: {device.device_type}")
        print(f"    名称: {device.name}")
        print(f"    协议: {device.protocol}")
        print(f"    波特率: {device.baud_rate}")
        print(f"    置信度: {device.confidence}")


def test_device_manager():
    """测试设备管理器"""
    print("\n" + "=" * 70)
    print("测试设备管理器")
    print("=" * 70)
    
    manager = get_device_manager()
    
    print("\n1. 自动发现设备...")
    new_devices = manager.auto_discover_devices()
    print(f"发现 {len(new_devices)} 个新设备")
    
    print("\n2. 获取所有设备...")
    all_devices = manager.get_all_devices()
    print(f"共有 {len(all_devices)} 个设备:")
    for device in all_devices:
        print(f"  - {device.device_id}: {device.name} ({device.status.value})")
    
    print("\n3. 获取设备摘要...")
    summary = manager.get_device_summary()
    print(f"总计: {summary['total']}")
    print(f"按类型: {summary['by_type']}")
    print(f"按状态: {summary['by_status']}")
    
    print("\n4. 根据类型获取设备...")
    asdb2_devices = manager.get_devices_by_type('asdb2_motor')
    print(f"ASDB2电机: {len(asdb2_devices)} 个")
    
    dpt_devices = manager.get_devices_by_type('dpt_encoder')
    print(f"DPT编码器: {len(dpt_devices)} 个")


if __name__ == "__main__":
    test_serial_detector()
    test_device_manager()
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)
"""简单测试设备检测"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from shared.drivers.device_detection.serial_detector import SerialDeviceDetector

print("=" * 70)
print("串口设备检测测试")
print("=" * 70)

detector = SerialDeviceDetector()

print("\n1. 扫描串口...")
ports = detector.scan_all_ports()
print(f"找到 {len(ports)} 个串口:")
for port in ports:
    print(f"  {port.port}: {port.description}")
    print(f"    VID: {port.vid}, PID: {port.pid}")

print("\n2. 自动发现设备...")
devices = detector.auto_discover(use_cache=False)
print(f"识别到 {len(devices)} 个设备:")
for port, device in devices.items():
    print(f"  {port}: {device.name} ({device.protocol})")

print("\n测试完成")
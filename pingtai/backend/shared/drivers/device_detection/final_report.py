"""设备识别最终报告"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import logging
logging.basicConfig(level=logging.WARNING)

from shared.drivers.device_detection.serial_detector import SerialDeviceDetector

print("=" * 80)
print("编码器测试平台 - 设备自动识别报告")
print("=" * 80)

detector = SerialDeviceDetector()

print("\n【扫描结果】")
print("-" * 60)

devices = detector.auto_discover(use_cache=False)

device_map = {
    'asdb2_motor': 'ASDB2电机驱动器',
    'dpt_encoder': 'DPT磁双编码器',
    'ata101b_power_amplifier': 'ATA-101B功率放大器',
    'dg811_waveform_generator': 'RIGOL DG811波形发生器',
    'unknown': '未知设备'
}

found_devices = []
missing_devices = []

expected_devices = ['asdb2_motor', 'dpt_encoder', 'ata101b_power_amplifier', 'dg811_waveform_generator']

for port, device in devices.items():
    print(f"\n端口: {port}")
    print(f"设备类型: {device_map.get(device.device_type, device.device_type)}")
    print(f"协议: {device.protocol}")
    print(f"波特率: {device.baud_rate}")
    print(f"置信度: {device.confidence}")
    
    found_devices.append(device.device_type)

print("\n【设备匹配状态】")
print("-" * 60)

for expected in expected_devices:
    if expected in found_devices:
        print(f"✓ {device_map[expected]} - 已识别")
    else:
        print(f"✗ {device_map[expected]} - 未找到")
        missing_devices.append(expected)

if missing_devices:
    print(f"\n【未找到的设备】")
    print("-" * 60)
    print("以下设备未在串口上找到：")
    for device in missing_devices:
        print(f"  • {device_map[device]}")
    print("\n可能原因：")
    print("  1. 设备未连接或未通电")
    print("  2. 设备使用USB直接连接而非串口")
    print("  3. 设备VID/PID与预设值不匹配")

print("\n" + "=" * 80)
print(f"识别完成：共找到 {len(found_devices)} / {len(expected_devices)} 个设备")
print("=" * 80)
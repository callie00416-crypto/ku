"""
检测可用设备
"""
import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

import serial.tools.list_ports
import pyvisa

print("="*60)
print("可用串口列表")
print("="*60)
ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"  {port.device}: {port.description}")

print("\n" + "="*60)
print("可用 VISA 设备")
print("="*60)
try:
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    if resources:
        for resource in resources:
            print(f"  {resource}")
    else:
        print("  未检测到 VISA 设备")
    rm.close()
except Exception as e:
    print(f"  错误: {e}")
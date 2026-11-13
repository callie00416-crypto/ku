"""ASDB2电机驱动 - 自动识别串口示例

展示如何使用平台的自动设备发现能力来自动识别ASDB2电机驱动器的串口
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import time
import logging
from shared.drivers.comm.rs485_comm import RS485Comm
from shared.drivers.protocol.modbus_rtu import ModbusDriver
from shared.drivers.device_detection.serial_detector import SerialDeviceDetector
from projects.encoder_test.drivers.device.ASDB2.asdb2_driver import ASDB2Driver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def auto_detect_asdb2():
    """自动检测ASDB2电机驱动器"""
    print("=" * 70)
    print("ASDB2电机驱动器 - 自动识别串口")
    print("=" * 70 + "\n")
    
    # 创建设备检测器
    print("1. 创建设备检测器")
    detector = SerialDeviceDetector()
    print("    ✅ SerialDeviceDetector创建成功\n")
    
    # 自动发现所有设备
    print("2. 自动发现设备")
    devices = detector.auto_discover(use_cache=False)
    print(f"    发现 {len(devices)} 个设备\n")
    
    # 查找ASDB2电机驱动器
    print("3. 查找ASDB2电机驱动器")
    asdb2_devices = []
    for port, device_info in devices.items():
        if device_info.device_type == 'asdb2_motor':
            asdb2_devices.append((port, device_info))
            print(f"    ✅ 找到ASDB2电机驱动器: {port}")
            print(f"       设备名称: {device_info.name}")
            print(f"       协议: {device_info.protocol}")
            print(f"       波特率: {device_info.baud_rate}")
            print(f"       连接类型: {device_info.connection_type}")
    
    if not asdb2_devices:
        print("    ❌ 未找到ASDB2电机驱动器")
        return None, None
    
    # 返回第一个找到的ASDB2设备
    port, device_info = asdb2_devices[0]
    print(f"\n    选择设备: {port}")
    return port, device_info


def connect_with_auto_discovery():
    """使用自动识别连接ASDB2"""
    print("\n" + "=" * 70)
    print("使用自动识别连接ASDB2电机驱动器")
    print("=" * 70 + "\n")
    
    # 自动检测ASDB2
    port, device_info = auto_detect_asdb2()
    if not port:
        print("\n❌ 无法找到ASDB2电机驱动器")
        return False
    
    # 创建通讯层（使用自动识别到的端口和波特率）
    print("\n4. 创建通讯层")
    comm = RS485Comm(
        driver_id='rs485_asdb2',
        port=port,
        baudrate=device_info.baud_rate if device_info.baud_rate else 38400,
        parity='N',
        stopbits=2,
        bytesize=8,
        timeout=2.0
    )
    print(f"    ✅ RS485Comm创建成功 (端口: {port}, 波特率: {comm.baudrate})\n")
    
    # 创建协议层
    print("5. 创建协议层（MODBUS-RTU）")
    protocol = ModbusDriver(
        driver_id='modbus_asdb2',
        comm=comm,
        slave_id=0x7F,
        mode='rtu'
    )
    print("    ✅ ModbusDriver创建成功\n")
    
    # 创建设备驱动
    print("6. 创建设备驱动（ASDB2）")
    driver = ASDB2Driver(
        driver_id='asdb2',
        protocol=protocol,
        slave_id=0x7F
    )
    print("    ✅ ASDB2Driver创建成功\n")
    
    # 连接设备
    print("7. 连接设备")
    try:
        if not driver.connect():
            print("    ❌ 连接失败")
            return False
        print("    ✅ 连接成功\n")
    except Exception as e:
        print(f"    ❌ 连接失败: {e}")
        return False
    
    # 执行简单测试
    print("8. 执行简单测试")
    try:
        # 读取设备信息
        print("    读取设备信息...")
        health = driver.health_check()
        print(f"    设备类型: {health.get('device_type')}")
        print(f"    连接状态: {health.get('is_connected')}")
        
        # 设置速度并启动
        print("\n    设置速度...")
        driver.set_speed(p1_09=50, p1_10=50, p1_11=50)
        
        print("    使能伺服...")
        driver.enable_servo(True)
        
        print("    启动电机 (50 RPM, CW)...")
        driver.run_motor(speed_rpm=50, direction='CW', source='P1-11')
        
        time.sleep(5)
        
        feedback = driver.read_feedback_speed()
        print(f"    反馈速度: {feedback} RPM")
        
        print("    停止电机...")
        driver.stop_motor()
        driver.enable_servo(False)
        
    except Exception as e:
        print(f"    ❌ 测试失败: {e}")
        driver.disconnect()
        return False
    
    # 断开连接
    print("\n9. 断开连接")
    driver.disconnect()
    print("    ✅ 完成\n")
    
    print("=" * 70)
    print("✅ 自动识别连接测试完成!")
    print("=" * 70)
    
    return True


def batch_detect_all_devices():
    """批量检测所有设备并展示"""
    print("\n" + "=" * 70)
    print("批量检测所有设备")
    print("=" * 70 + "\n")
    
    detector = SerialDeviceDetector()
    devices = detector.auto_discover(use_cache=False)
    
    print("设备列表:")
    print("-" * 70)
    
    for port, device_info in devices.items():
        print(f"\n端口: {port}")
        print(f"  设备类型: {device_info.device_type}")
        print(f"  设备名称: {device_info.name}")
        print(f"  协议: {device_info.protocol}")
        print(f"  波特率: {device_info.baud_rate}")
        print(f"  连接类型: {device_info.connection_type}")
        print(f"  已连接: {device_info.is_connected}")
        print(f"  置信度: {device_info.confidence}")
    
    print("\n" + "-" * 70)
    print(f"总计: {len(devices)} 个设备")


if __name__ == "__main__":
    print("=" * 70)
    print("ASDB2自动识别串口示例")
    print("=" * 70)
    print("\n选项:")
    print("1. 批量检测所有设备")
    print("2. 自动识别并连接ASDB2")
    print("=" * 70 + "\n")
    
    choice = input("请输入选项（1-2）: ")
    
    if choice == "1":
        batch_detect_all_devices()
    elif choice == "2":
        connect_with_auto_discovery()
    else:
        print("无效选项")
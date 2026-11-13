"""
串口资源管理使用示例

【使用场景】
1. 基本串口使用
2. 自动处理权限错误
3. 串口资源管理
4. 并发访问控制

【依赖安装】
pip install pyserial psutil
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shared.drivers.comm.rs485_comm import RS485Comm
from shared.drivers.comm.serial_port_manager import (
    get_serial_port_manager,
    reset_serial_port
)


def example_1_basic_usage():
    """示例1: 基本使用（自动处理权限错误）"""
    print("\n" + "="*60)
    print("示例1: 基本使用")
    print("="*60)
    
    # 创建RS485通讯驱动（自动启用资源管理）
    rs485 = RS485Comm(
        driver_id='power_supply',
        port='COM4',  # 替换为你的串口
        baudrate=9600,
        auto_cleanup=True,      # 自动清理占用进程
        acquire_timeout=10.0    # 获取超时时间
    )
    
    # 打开串口（自动处理权限错误）
    if rs485.open():
        print("✅ 串口打开成功")
        
        # 使用串口...
        # rs485.send(b'Hello')
        # data = rs485.recv(1024)
        
        # 关闭串口（自动释放资源）
        rs485.close()
        print("✅ 串口关闭成功")
    else:
        print("❌ 串口打开失败")


def example_2_manual_port_management():
    """示例2: 手动串口资源管理"""
    print("\n" + "="*60)
    print("示例2: 手动串口资源管理")
    print("="*60)
    
    manager = get_serial_port_manager()
    
    # 列出可用串口
    print("\n可用串口:")
    ports = manager.list_available_ports()
    for port in ports:
        print(f"  - {port}")
    
    if ports:
        test_port = ports[0]
        print(f"\n使用串口: {test_port}")
        
        # 获取串口资源
        if manager.acquire_port(test_port, owner="example2", timeout=10.0):
            print("✅ 获取串口成功")
            
            # 使用串口...
            try:
                import serial
                ser = serial.Serial(test_port, baudrate=9600, timeout=1.0)
                print("✅ 串口打开成功")
                
                # 使用串口...
                # ser.write(b'Hello')
                # data = ser.read(1024)
                
                ser.close()
            except Exception as e:
                print(f"❌ 串口使用失败: {e}")
            
            # 释放串口资源
            manager.release_port(test_port)
            print("✅ 释放串口成功")
        else:
            print("❌ 获取串口失败")


def example_3_reset_port():
    """示例3: 重置串口（解决权限错误）"""
    print("\n" + "="*60)
    print("示例3: 重置串口")
    print("="*60)
    
    # 假设串口被占用或出现权限错误
    port = 'COM4'  # 替换为你的串口
    
    print(f"\n重置串口: {port}")
    
    # 重置串口（自动清理占用进程）
    if reset_serial_port(port):
        print("✅ 串口重置成功")
        
        # 现在可以正常使用串口了
        rs485 = RS485Comm(
            driver_id='power_supply',
            port=port,
            baudrate=9600
        )
        
        if rs485.open():
            print("✅ 串口打开成功")
            rs485.close()
        else:
            print("❌ 串口打开失败")
    else:
        print("❌ 串口重置失败")


def example_4_concurrent_access():
    """示例4: 并发访问控制"""
    print("\n" + "="*60)
    print("示例4: 并发访问控制")
    print("="*60)
    
    import threading
    import time
    
    def worker(worker_id, port):
        """工作线程"""
        print(f"工作线程 {worker_id} 开始")
        
        # 创建RS485通讯驱动
        rs485 = RS485Comm(
            driver_id=f'worker_{worker_id}',
            port=port,
            baudrate=9600,
            auto_cleanup=True,
            acquire_timeout=10.0
        )
        
        # 尝试打开串口
        if rs485.open():
            print(f"工作线程 {worker_id} 获取串口成功")
            
            # 使用串口2秒
            time.sleep(2)
            
            # 关闭串口
            rs485.close()
            print(f"工作线程 {worker_id} 释放串口成功")
        else:
            print(f"工作线程 {worker_id} 获取串口失败")
    
    # 列出可用串口
    ports = get_serial_port_manager().list_available_ports()
    if not ports:
        print("⚠️  没有可用的串口，跳过示例")
        return
    
    test_port = ports[0]
    print(f"测试串口: {test_port}")
    
    # 创建多个工作线程
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker, args=(i, test_port))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    print("\n✅ 并发访问测试完成")


def example_5_device_integration():
    """示例5: 设备驱动集成"""
    print("\n" + "="*60)
    print("示例5: 设备驱动集成")
    print("="*60)
    
    # 创建通信层（自动启用资源管理）
    comm = RS485Comm(
        driver_id='power_supply_comm',
        port='COM4',  # 替换为你的串口
        baudrate=9600,
        auto_cleanup=True,
        acquire_timeout=10.0
    )
    
    # 创建协议层
    from shared.drivers.protocol.modbus_rtu import ModbusRTU
    protocol = ModbusRTU(
        driver_id='power_supply_protocol',
        comm=comm,
        slave_id=1
    )
    
    # 创建设备驱动
    from projects.encoder_test.drivers.device.power_supply.power_supply import PowerSupply
    ps = PowerSupply(
        driver_id='power_supply',
        protocol=protocol
    )
    
    # 连接设备（自动处理串口资源）
    if ps.connect():
        print("✅ 设备连接成功")
        
        # 使用设备...
        # ps.set_voltage(5.0)
        # voltage = ps.read_voltage()
        
        # 断开连接（自动释放串口资源）
        ps.disconnect()
        print("✅ 设备断开成功")
    else:
        print("❌ 设备连接失败")


def example_6_error_handling():
    """示例6: 错误处理和恢复"""
    print("\n" + "="*60)
    print("示例6: 错误处理和恢复")
    print("="*60)
    
    rs485 = RS485Comm(
        driver_id='test',
        port='COM4',  # 替换为你的串口
        baudrate=9600,
        auto_cleanup=True,
        acquire_timeout=10.0
    )
    
    # 尝试打开串口
    if not rs485.open():
        print("❌ 串口打开失败")
        
        # 检查错误原因
        if rs485.error_count > 0:
            print(f"错误计数: {rs485.error_count}")
        
        # 尝试重置串口
        print("\n尝试重置串口...")
        if reset_serial_port(rs485.port):
            print("✅ 串口重置成功")
            
            # 重新尝试打开
            if rs485.open():
                print("✅ 串口打开成功")
                rs485.close()
            else:
                print("❌ 串口仍然无法打开")
        else:
            print("❌ 串口重置失败")
    else:
        print("✅ 串口打开成功")
        rs485.close()


def example_7_health_check():
    """示例7: 健康检查"""
    print("\n" + "="*60)
    print("示例7: 健康检查")
    print("="*60)
    
    manager = get_serial_port_manager()
    
    # 列出可用串口
    ports = manager.list_available_ports()
    if not ports:
        print("⚠️  没有可用的串口，跳过示例")
        return
    
    test_port = ports[0]
    print(f"测试串口: {test_port}")
    
    # 检查串口状态
    from shared.drivers.comm.serial_port_manager import SerialPortStatus
    status = manager.check_port_status(test_port)
    print(f"串口状态: {status.value}")
    
    # 查看所有串口状态
    print(f"\n所有串口状态:")
    all_status = manager.get_all_ports_status()
    for port, info in all_status.items():
        print(f"  {port}:")
        print(f"    状态: {info['status']}")
        print(f"    占用者: {info['lock_owner']}")
        print(f"    进程: {info['process_name']} (PID: {info['process_id']})")


def main():
    """主函数"""
    print("="*60)
    print("串口资源管理使用示例")
    print("="*60)
    
    try:
        # 运行所有示例
        example_1_basic_usage()
        example_2_manual_port_management()
        example_3_reset_port()
        example_4_concurrent_access()
        # example_5_device_integration()  # 需要实际设备
        example_6_error_handling()
        example_7_health_check()
        
        print("\n" + "="*60)
        print("✅ 所有示例完成")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  示例被中断")
    except Exception as e:
        print(f"\n\n❌ 示例异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
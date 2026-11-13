"""
串口资源管理器测试脚本

【测试目的】
验证串口资源管理器的功能
测试串口占用检测和自动清理
测试权限错误的自动处理

【测试场景】
1. 串口资源获取和释放
2. 串口占用检测
3. 自动清理占用进程
4. 权限错误处理
5. 串口重置功能
"""
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.drivers.comm.serial_port_manager import (
    get_serial_port_manager,
    acquire_serial_port,
    release_serial_port,
    reset_serial_port,
    SerialPortStatus
)


def test_basic_usage():
    """测试基本使用"""
    print("\n" + "="*60)
    print("测试1: 基本使用")
    print("="*60)
    
    manager = get_serial_port_manager()
    
    # 列出可用串口
    print("\n可用串口:")
    ports = manager.list_available_ports()
    for port in ports:
        print(f"  - {port}")
    
    if not ports:
        print("⚠️  没有可用的串口，跳过测试")
        return
    
    test_port = ports[0]
    print(f"\n测试串口: {test_port}")
    
    # 检查串口状态
    status = manager.check_port_status(test_port)
    print(f"串口状态: {status.value}")
    
    # 获取串口
    print(f"\n获取串口...")
    if manager.acquire_port(test_port, owner="test1", timeout=5.0):
        print("✅ 获取成功")
        
        # 尝试打开串口
        try:
            import serial
            ser = serial.Serial(test_port, baudrate=9600, timeout=1.0)
            print(f"✅ 串口打开成功")
            ser.close()
        except Exception as e:
            print(f"❌ 串口打开失败: {e}")
        
        # 释放串口
        print(f"\n释放串口...")
        manager.release_port(test_port)
        print("✅ 释放成功")
    else:
        print("❌ 获取失败")


def test_port_occupancy():
    """测试串口占用检测"""
    print("\n" + "="*60)
    print("测试2: 串口占用检测")
    print("="*60)
    
    manager = get_serial_port_manager()
    
    # 列出可用串口
    ports = manager.list_available_ports()
    if not ports:
        print("⚠️  没有可用的串口，跳过测试")
        return
    
    test_port = ports[0]
    print(f"测试串口: {test_port}")
    
    # 第一次获取
    print(f"\n第一次获取串口...")
    if manager.acquire_port(test_port, owner="test2", timeout=5.0):
        print("✅ 第一次获取成功")
        
        # 检查状态
        status = manager.check_port_status(test_port)
        print(f"串口状态: {status.value}")
        
        # 查找占用进程
        occupying_process = manager.find_occupying_process(test_port)
        if occupying_process:
            pid, name = occupying_process
            print(f"占用进程: PID={pid}, Name={name}")
        else:
            print("未找到占用进程（可能已被清理）")
        
        # 释放串口
        manager.release_port(test_port)
        print("✅ 释放成功")
    else:
        print("❌ 获取失败")


def test_auto_cleanup():
    """测试自动清理功能"""
    print("\n" + "="*60)
    print("测试3: 自动清理功能")
    print("="*60)
    
    manager = get_serial_port_manager()
    
    # 列出可用串口
    ports = manager.list_available_ports()
    if not ports:
        print("⚠️  没有可用的串口，跳过测试")
        return
    
    test_port = ports[0]
    print(f"测试串口: {test_port}")
    
    # 模拟串口占用
    print(f"\n模拟串口占用...")
    try:
        import serial
        ser = serial.Serial(test_port, baudrate=9600, timeout=1.0)
        print("✅ 串口已打开（模拟占用）")
        
        # 尝试获取串口（应该自动清理）
        print(f"\n尝试获取串口（应该自动清理）...")
        if manager.acquire_port(test_port, owner="test3", timeout=5.0, auto_cleanup=True):
            print("✅ 获取成功（自动清理生效）")
            
            # 关闭串口
            ser.close()
            manager.release_port(test_port)
            print("✅ 清理完成")
        else:
            print("❌ 获取失败")
            ser.close()
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")


def test_permission_error_handling():
    """测试权限错误处理"""
    print("\n" + "="*60)
    print("测试4: 权限错误处理")
    print("="*60)
    
    from shared.drivers.comm.rs485_comm import RS485Comm
    
    # 列出可用串口
    ports = get_serial_port_manager().list_available_ports()
    if not ports:
        print("⚠️  没有可用的串口，跳过测试")
        return
    
    test_port = ports[0]
    print(f"测试串口: {test_port}")
    
    # 创建RS485通讯驱动
    print(f"\n创建RS485通讯驱动...")
    rs485 = RS485Comm(
        driver_id='test_rs485',
        port=test_port,
        baudrate=9600,
        auto_cleanup=True,
        acquire_timeout=10.0
    )
    
    # 打开串口
    print(f"\n打开串口...")
    if rs485.open():
        print("✅ 串口打开成功")
        
        # 关闭串口
        print(f"\n关闭串口...")
        rs485.close()
        print("✅ 串口关闭成功")
    else:
        print("❌ 串口打开失败")


def test_port_reset():
    """测试串口重置功能"""
    print("\n" + "="*60)
    print("测试5: 串口重置功能")
    print("="*60)
    
    manager = get_serial_port_manager()
    
    # 列出可用串口
    ports = manager.list_available_ports()
    if not ports:
        print("⚠️  没有可用的串口，跳过测试")
        return
    
    test_port = ports[0]
    print(f"测试串口: {test_port}")
    
    # 模拟串口占用
    print(f"\n模拟串口占用...")
    try:
        import serial
        ser = serial.Serial(test_port, baudrate=9600, timeout=1.0)
        print("✅ 串口已打开（模拟占用）")
        
        # 重置串口
        print(f"\n重置串口...")
        if manager.reset_port(test_port):
            print("✅ 串口重置成功")
            
            # 验证串口状态
            status = manager.check_port_status(test_port)
            print(f"串口状态: {status.value}")
        else:
            print("❌ 串口重置失败")
            ser.close()
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")


def test_concurrent_access():
    """测试并发访问"""
    print("\n" + "="*60)
    print("测试6: 并发访问")
    print("="*60)
    
    manager = get_serial_port_manager()
    
    # 列出可用串口
    ports = manager.list_available_ports()
    if not ports:
        print("⚠️  没有可用的串口，跳过测试")
        return
    
    test_port = ports[0]
    print(f"测试串口: {test_port}")
    
    import threading
    
    def worker(worker_id):
        """工作线程"""
        print(f"工作线程 {worker_id} 开始")
        
        # 尝试获取串口
        if manager.acquire_port(test_port, owner=f"worker_{worker_id}", timeout=5.0):
            print(f"工作线程 {worker_id} 获取成功")
            
            # 持有串口2秒
            time.sleep(2)
            
            # 释放串口
            manager.release_port(test_port)
            print(f"工作线程 {worker_id} 释放成功")
        else:
            print(f"工作线程 {worker_id} 获取失败")
    
    # 创建多个工作线程
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    print("\n✅ 并发访问测试完成")


def test_expiration_cleanup():
    """测试过期清理"""
    print("\n" + "="*60)
    print("测试7: 过期清理")
    print("="*60)
    
    manager = get_serial_port_manager()
    
    # 列出可用串口
    ports = manager.list_available_ports()
    if not ports:
        print("⚠️  没有可用的串口，跳过测试")
        return
    
    test_port = ports[0]
    print(f"测试串口: {test_port}")
    
    # 获取串口
    print(f"\n获取串口...")
    if manager.acquire_port(test_port, owner="test7", timeout=5.0):
        print("✅ 获取成功")
        
        # 查看所有串口状态
        print(f"\n所有串口状态:")
        all_status = manager.get_all_ports_status()
        for port, info in all_status.items():
            print(f"  {port}: {info}")
        
        # 手动触发清理（设置超时为1秒）
        print(f"\n手动触发清理...")
        manager._port_timeout = 1  # 设置超时为1秒
        manager.cleanup_expired_ports()
        
        # 查看清理后的状态
        print(f"\n清理后的串口状态:")
        all_status = manager.get_all_ports_status()
        for port, info in all_status.items():
            print(f"  {port}: {info}")
        
        # 恢复超时设置
        manager._port_timeout = 3600
        
        print("\n✅ 过期清理测试完成")
    else:
        print("❌ 获取失败")


def main():
    """主函数"""
    print("="*60)
    print("串口资源管理器测试")
    print("="*60)
    
    try:
        # 运行所有测试
        test_basic_usage()
        test_port_occupancy()
        test_auto_cleanup()
        test_permission_error_handling()
        test_port_reset()
        test_concurrent_access()
        test_expiration_cleanup()
        
        print("\n" + "="*60)
        print("✅ 所有测试完成")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
    except Exception as e:
        print(f"\n\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
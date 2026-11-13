"""
ATA-101B 功放 USB 直连通信测试

【测试目标】
设备通过 USB 线直连电脑（内置 FTDI 芯片），尝试不同的通信方法
"""
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import serial


# ===== 配置区 =====
SERIAL_PORT = 'COM3'
BAUDRATE = 9600
# ==================


def test_method1_basic():
    """方法1: 基本通信测试"""
    print("\n" + "="*70)
    print("方法1: 基本通信测试")
    print("="*70)
    
    try:
        print(f"\n打开串口 {SERIAL_PORT}...")
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=2
        )
        
        # 等待设备稳定
        print("等待设备稳定 (3秒)...")
        time.sleep(3)
        
        # 清空缓冲区
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # 发送简单命令
        print("\n发送命令: ATA,SET,AON,0000;")
        command = "ATA,SET,AON,0000;"
        ser.write(command.encode('ascii'))
        ser.flush()
        
        # 等待并读取响应
        time.sleep(1)
        response = ser.read_all()
        
        if response:
            print(f"✅ 收到响应: {response.decode('ascii', errors='replace')}")
        else:
            print("❌ 无响应")
            
        ser.close()
        return bool(response)
        
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False


def test_method2_delay():
    """方法2: 增加延时"""
    print("\n" + "="*70)
    print("方法2: 增加延时测试")
    print("="*70)
    
    try:
        print(f"\n打开串口 {SERIAL_PORT}...")
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=5  # 增加到 5 秒
        )
        
        # 等待更长时间
        print("等待设备初始化 (5秒)...")
        time.sleep(5)
        
        # 清空缓冲区
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # 发送命令
        print("\n发送命令: ATA,SET,AON,0000;")
        command = "ATA,SET,AON,0000;"
        ser.write(command.encode('ascii'))
        ser.flush()
        
        # 等待更长时间
        print("等待响应 (3秒)...")
        time.sleep(3)
        response = ser.read_all()
        
        if response:
            print(f"✅ 收到响应: {response.decode('ascii', errors='replace')}")
        else:
            print("❌ 无响应")
            
        ser.close()
        return bool(response)
        
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False


def test_method3_polling():
    """方法3: 轮询读取"""
    print("\n" + "="*70)
    print("方法3: 轮询读取测试")
    print("="*70)
    
    try:
        print(f"\n打开串口 {SERIAL_PORT}...")
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=0.1  # 非阻塞模式
        )
        
        # 等待
        print("等待设备稳定 (2秒)...")
        time.sleep(2)
        
        # 清空缓冲区
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # 发送命令
        print("\n发送命令: ATA,SET,AON,0000;")
        command = "ATA,SET,AON,0000;"
        ser.write(command.encode('ascii'))
        ser.flush()
        
        # 轮询读取
        print("轮询读取响应 (5秒)...")
        all_response = b''
        start_time = time.time()
        
        while time.time() - start_time < 5:
            chunk = ser.read(1024)
            if chunk:
                all_response += chunk
                print(f"  收到 {len(chunk)} 字节")
            time.sleep(0.1)
        
        if all_response:
            print(f"\n✅ 总收到响应: {all_response.decode('ascii', errors='replace')}")
        else:
            print("\n❌ 无响应")
            
        ser.close()
        return bool(all_response)
        
    except Exception as e:
        print(f" 异常: {e}")
        return False


def test_method4_different_commands():
    """方法4: 尝试不同命令"""
    print("\n" + "="*70)
    print("方法4: 尝试不同命令")
    print("="*70)
    
    # 尝试多种可能的命令格式
    test_commands = [
        "ATA,SET,AON,0000;",
        "ATA,SET,AON;",
        "AON,0000;",
        "AON;",
        "AON",
        "SET,AON,0000",
    ]
    
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1
        )
        
        time.sleep(2)
        ser.reset_input_buffer()
        
        for cmd in test_commands:
            print(f"\n测试命令: {cmd}")
            ser.write(cmd.encode('ascii'))
            ser.flush()
            time.sleep(1)
            
            response = ser.read_all()
            if response:
                print(f"  ✅ 收到: {response.decode('ascii', errors='replace')}")
                ser.reset_input_buffer()
            else:
                print(f"  ❌ 无响应")
        
        ser.close()
        
    except Exception as e:
        print(f"❌ 异常: {e}")


def test_method5_check_dtr_rts():
    """方法5: 检查 DTR/RTS 控制线"""
    print("\n" + "="*70)
    print("方法5: 测试 DTR/RTS 控制线")
    print("="*70)
    
    # 有些设备需要设置 DTR/RTS 才能工作
    configurations = [
        {"dtr": True, "rts": True, "name": "DTR=True, RTS=True"},
        {"dtr": False, "rts": False, "name": "DTR=False, RTS=False"},
        {"dtr": True, "rts": False, "name": "DTR=True, RTS=False"},
        {"dtr": False, "rts": True, "name": "DTR=False, RTS=True"},
    ]
    
    for config in configurations:
        print(f"\n测试配置: {config['name']}")
        
        try:
            ser = serial.Serial(
                port=SERIAL_PORT,
                baudrate=BAUDRATE,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1
            )
            
            ser.dtr = config['dtr']
            ser.rts = config['rts']
            
            time.sleep(1)
            ser.reset_input_buffer()
            
            print("  发送: ATA,SET,AON,0000;")
            ser.write(b"ATA,SET,AON,0000;")
            ser.flush()
            
            time.sleep(1)
            response = ser.read_all()
            
            if response:
                print(f"  ✅ 收到: {response.decode('ascii', errors='replace')}")
            else:
                print(f"  ❌ 无响应")
            
            ser.close()
            
        except Exception as e:
            print(f"  ❌ 异常: {e}")


def show_device_info():
    """显示设备信息"""
    print("\n" + "="*70)
    print("设备信息")
    print("="*70)
    
    import serial.tools.list_ports
    
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.device == SERIAL_PORT:
            print(f"\n端口: {port.device}")
            print(f"描述: {port.description}")
            print(f"制造商: {port.manufacturer}")
            print(f"序列号: {port.serial_number}")
            print(f"硬件ID: {port.hwid}")
            break


def main():
    """主函数"""
    print("="*70)
    print("ATA-101B 功放 USB 直连通信诊断")
    print("="*70)
    
    # 显示设备信息
    show_device_info()
    
    print("\n\n选择测试方法:")
    print("1. 基本通信测试")
    print("2. 增加延时测试")
    print("3. 轮询读取测试")
    print("4. 尝试不同命令格式")
    print("5. 测试 DTR/RTS 控制线")
    print("6. 运行所有测试")
    print("0. 退出")
    
    while True:
        try:
            choice = input("\n请选择 (0-6): ").strip()
            
            if choice == '0':
                print("\n退出")
                break
            elif choice == '1':
                test_method1_basic()
            elif choice == '2':
                test_method2_delay()
            elif choice == '3':
                test_method3_polling()
            elif choice == '4':
                test_method4_different_commands()
            elif choice == '5':
                test_method5_check_dtr_rts()
            elif choice == '6':
                test_method1_basic()
                test_method2_delay()
                test_method3_polling()
                test_method4_different_commands()
                test_method5_check_dtr_rts()
            else:
                print("无效选择")
                
        except KeyboardInterrupt:
            print("\n\n️  测试被中断")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")


if __name__ == '__main__':
    main()

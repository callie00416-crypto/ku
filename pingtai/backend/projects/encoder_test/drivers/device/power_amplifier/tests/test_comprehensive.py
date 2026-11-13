"""
ATA-101B设备全面测试工具

【功能】
- 尝试不同的初始化序列
- 尝试不同的通信参数
- 尝试原始USB通信
- 尝试各种可能的命令格式
"""
import serial
import time
import sys
from pathlib import Path

# 添加路径
current_file = Path(__file__).resolve()
backend_path = current_file.parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))


def test_initialization_sequences():
    """测试不同的初始化序列"""
    print("=" * 70)
    print("测试1: 不同的初始化序列")
    print("=" * 70)
    
    init_sequences = [
        ("无初始化", []),
        ("简单初始化", ["ATA", "INIT", "START"]),
        ("复杂初始化", ["ATA,INIT", "ATA,CONNECT", "ATA,START"]),
        ("厂商初始化", ["ATA", "SET", "INIT", "0000"]),
        ("握手初始化", ["HANDSHAKE", "CONNECT", "INIT"]),
    ]
    
    for name, sequence in init_sequences:
        print(f"\n尝试: {name}")
        print(f"初始化序列: {sequence}")
        
        try:
            ser = serial.Serial(
                port='COM3',
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1.0
            )
            
            # 发送初始化序列
            for cmd in sequence:
                full_cmd = cmd + ";"
                ser.write(full_cmd.encode('ascii'))
                time.sleep(0.1)
            
            # 等待响应
            time.sleep(0.5)
            
            # 发送测试命令
            test_cmd = "ATA,SET,AON,0000;"
            ser.write(test_cmd.encode('ascii'))
            time.sleep(0.3)
            
            # 读取响应
            if ser.in_waiting > 0:
                resp = ser.read(ser.in_waiting).decode('ascii').strip()
                print(f"  ✓ 收到响应: {resp}")
                ser.close()
                return name, sequence, resp
            else:
                print(f"  ✗ 无响应")
            
            ser.close()
            
        except Exception as e:
            print(f"  ✗ 失败: {e}")
    
    return None, None, None


def test_communication_parameters():
    """测试不同的通信参数"""
    print("\n" + "=" * 70)
    print("测试2: 不同的通信参数")
    print("=" * 70)
    
    parameters = [
        ("标准参数", 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE),
        ("高波特率", 19200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE),
        ("低波特率", 4800, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE),
        ("奇校验", 9600, serial.EIGHTBITS, serial.PARITY_ODD, serial.STOPBITS_ONE),
        ("偶校验", 9600, serial.EIGHTBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE),
        ("2停止位", 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_TWO),
        ("7数据位", 9600, serial.SEVENBITS, serial.PARITY_NONE, serial.STOPBITS_ONE),
    ]
    
    for name, baudrate, bytesize, parity, stopbits in parameters:
        print(f"\n尝试: {name}")
        print(f"参数: {baudrate}, {bytesize}, {parity}, {stopbits}")
        
        try:
            ser = serial.Serial(
                port='COM3',
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=1.0
            )
            
            # 发送测试命令
            test_cmd = "ATA,SET,AON,0000;"
            ser.write(test_cmd.encode('ascii'))
            time.sleep(0.3)
            
            # 读取响应
            if ser.in_waiting > 0:
                resp = ser.read(ser.in_waiting).decode('ascii').strip()
                print(f"  ✓ 收到响应: {resp}")
                ser.close()
                return name, (baudrate, bytesize, parity, stopbits), resp
            else:
                print(f"  ✗ 无响应")
            
            ser.close()
            
        except Exception as e:
            print(f"  ✗ 失败: {e}")
    
    return None, None, None


def test_command_formats():
    """测试不同的命令格式"""
    print("\n" + "=" * 70)
    print("测试3: 不同的命令格式")
    print("=" * 70)
    
    command_formats = [
        ("标准格式", "ATA,SET,AON,0000;"),
        ("无ATA前缀", "SET,AON,0000;"),
        ("无SET", "ATA,AON,0000;"),
        ("简短格式", "AON;"),
        ("数字格式", "1;"),
        ("无分号", "ATA,SET,AON,0000"),
        ("大写", "ATA,SET,AON,0000;"),
        ("小写", "ata,set,aon,0000;"),
        ("混合", "AtA,SeT,AoN,0000;"),
        ("无逗号", "ATA SET AON 0000;"),
        ("空格分隔", "ATA, SET, AON, 0000;"),
        ("冒号分隔", "ATA:SET:AON:0000;"),
        ("斜杠分隔", "ATA/SET/AON/0000;"),
    ]
    
    try:
        ser = serial.Serial(
            port='COM3',
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1.0
        )
        
        for name, command in command_formats:
            print(f"\n尝试: {name}")
            print(f"命令: {command}")
            
            try:
                ser.write(command.encode('ascii'))
                time.sleep(0.3)
                
                if ser.in_waiting > 0:
                    resp = ser.read(ser.in_waiting).decode('ascii').strip()
                    print(f"  ✓ 收到响应: {resp}")
                    ser.close()
                    return name, command, resp
                else:
                    print(f"  ✗ 无响应")
            
            except Exception as e:
                print(f"  ✗ 失败: {e}")
        
        ser.close()
        
    except Exception as e:
        print(f"✗ 串口打开失败: {e}")
    
    return None, None, None


def test_special_commands():
    """测试特殊命令"""
    print("\n" + "=" * 70)
    print("测试4: 特殊命令")
    print("=" * 70)
    
    special_commands = [
        ("查询状态", "STA;"),
        ("查询信息", "INFO;"),
        ("版本", "VER;"),
        ("识别", "ID;"),
        ("帮助", "HELP;"),
        ("测试", "TEST;"),
        ("连接", "CONNECT;"),
        ("断开", "DISCONNECT;"),
        ("复位", "RESET;"),
        ("模式", "MODE;"),
        ("远程", "REMOTE;"),
        ("本地", "LOCAL;"),
        ("状态", "STATUS;"),
        ("读取", "READ;"),
        ("写入", "WRITE;"),
    ]
    
    try:
        ser = serial.Serial(
            port='COM3',
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1.0
        )
        
        for name, command in special_commands:
            print(f"\n尝试: {name}")
            print(f"命令: {command}")
            
            try:
                ser.write(command.encode('ascii'))
                time.sleep(0.3)
                
                if ser.in_waiting > 0:
                    resp = ser.read(ser.in_waiting).decode('ascii').strip()
                    print(f"  ✓ 收到响应: {resp}")
                else:
                    print(f"  ✗ 无响应")
            
            except Exception as e:
                print(f"  ✗ 失败: {e}")
        
        ser.close()
        
    except Exception as e:
        print(f"✗ 串口打开失败: {e}")


def main():
    """主函数"""
    print("=" * 70)
    print("ATA-101B设备全面测试工具")
    print("=" * 70)
    
    results = []
    
    # 测试1: 初始化序列
    init_name, init_seq, init_resp = test_initialization_sequences()
    if init_resp:
        results.append(("初始化序列", init_name, init_seq, init_resp))
    
    # 测试2: 通信参数
    param_name, param_value, param_resp = test_communication_parameters()
    if param_resp:
        results.append(("通信参数", param_name, param_value, param_resp))
    
    # 测试3: 命令格式
    cmd_name, cmd_value, cmd_resp = test_command_formats()
    if cmd_resp:
        results.append(("命令格式", cmd_name, cmd_value, cmd_resp))
    
    # 测试4: 特殊命令
    test_special_commands()
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    if results:
        print(f"\n✓ 找到有效的配置/命令:")
        for category, name, value, resp in results:
            print(f"\n{category}:")
            print(f"  名称: {name}")
            print(f"  值: {value}")
            print(f"  响应: {resp}")
    else:
        print(f"\n✗ 未找到有效的配置/命令")
        print(f"\n可能的原因:")
        print(f"  1. 设备需要厂商提供的专用软件")
        print(f"  2. 设备需要特定的USB驱动")
        print(f"  3. 设备固件版本与手册不匹配")
        print(f"  4. 设备本身可能有问题")
        print(f"  5. USB通信协议不是标准串口协议")
        
        print(f"\n建议:")
        print(f"  1. 联系设备厂商，确认USB程控功能")
        print(f"  2. 尝试使用厂商提供的控制软件")
        print(f"  3. 检查设备固件版本")
        print(f"  4. 尝试使用USB协议分析工具")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n发生异常: {e}")
        import traceback
        traceback.print_exc()
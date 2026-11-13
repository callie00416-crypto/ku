"""
ATA-101B串口助手（添加换行符测试）

【功能】
- 测试不同的换行符
- 找到正确的行结束符
"""
import serial
import time
import sys
from pathlib import Path
from datetime import datetime

# 添加路径
current_file = Path(__file__).resolve()
backend_path = current_file.parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))


def test_newlines():
    """测试不同的换行符"""
    print("=" * 70)
    print("ATA-101B换行符测试")
    print("=" * 70)
    
    # 测试不同的换行符
    newline_types = [
        ("无换行符", ""),
        ("\\n (Unix换行)", "\n"),
        ("\\r\\n (Windows换行)", "\r\n"),
        ("\\r (Mac换行)", "\r"),
        ("\\r\\n\\r\\n (双换行)", "\r\n\r\n"),
        ("\\n\\r (反向换行)", "\n\r"),
    ]
    
    # 连接串口
    print(f"\n连接串口...")
    try:
        ser = serial.Serial(
            port='COM3',
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=2
        )
        print(f"✓ 串口连接成功")
    except Exception as e:
        print(f"✗ 串口连接失败：{e}")
        return None, None, None
    
    # 测试命令
    test_command = "ATA,SET,AON,0000;"
    
    print(f"\n测试命令: {test_command}")
    print(f"将测试 {len(newline_types)} 种换行符\n")
    
    for i, (name, newline) in enumerate(newline_types, 1):
        print(f"{'=' * 70}")
        print(f"测试 {i}/{len(newline_types)}: {name}")
        print(f"{'=' * 70}")
        
        # 添加换行符
        if newline:
            full_command = test_command + newline
            print(f"  换行符: {repr(newline)}")
        else:
            full_command = test_command
            print(f"  换行符: 无")
        
        print(f"  发送: {full_command}")
        
        # 显示十六进制
        hex_data = ' '.join([f'{b:02X}' for b in full_command.encode('ascii')])
        print(f"  十六进制: {hex_data}")
        
        try:
            # 发送命令
            ser.write(full_command.encode('ascii'))
            
            # 等待响应
            time.sleep(0.3)
            
            # 读取响应
            if ser.in_waiting > 0:
                resp_bytes = ser.read(ser.in_waiting)
                resp_str = resp_bytes.decode('ascii', errors='ignore').strip()
                
                print(f"  响应: {resp_str}")
                
                hex_resp = ' '.join([f'{b:02X}' for b in resp_bytes])
                print(f"  响应十六进制: {hex_resp}")
                
                # 分析响应
                if "SETDONE!" in resp_str:
                    print(f"  ✓✓✓ 成功！找到正确的换行符！")
                    print(f"  换行符: {repr(newline)}")
                    print(f"  名称: {name}")
                    ser.close()
                    return name, newline, resp_str
                elif "OVERRANGEERROR!" in resp_str:
                    print(f"  ✓ 收到响应（参数越界）")
                    print(f"  换行符: {repr(newline)}")
                    print(f"  名称: {name}")
                    ser.close()
                    return name, newline, resp_str
                elif "SETERROR!" in resp_str:
                    print(f"  ✓ 收到响应（指令错误）")
                    print(f"  换行符: {repr(newline)}")
                    print(f"  名称: {name}")
                    ser.close()
                    return name, newline, resp_str
                else:
                    print(f"  ? 收到未知响应: {resp_str}")
            else:
                print(f"  响应: (无数据)")
        
        except Exception as e:
            print(f"  ✗ 发送失败: {e}")
        
        time.sleep(0.5)
    
    # 断开连接
    ser.close()
    print(f"\n✓ 串口已断开")
    
    return None, None, None


def test_all_commands_with_newline(newline):
    """使用正确的换行符测试所有命令"""
    print("\n" + "=" * 70)
    print("使用正确的换行符测试所有命令")
    print("=" * 70)
    
    print(f"\n换行符: {repr(newline)}")
    
    # 连接串口
    print(f"\n连接串口...")
    try:
        ser = serial.Serial(
            port='COM3',
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=2
        )
        print(f"✓ 串口连接成功")
    except Exception as e:
        print(f"✗ 串口连接失败：{e}")
        return
    
    # 测试命令
    test_commands = [
        ("输出开", "ATA,SET,AON,0000;"),
        ("输出关", "ATA,SET,AOF,0000;"),
        ("增益20dB", "ATA,SET,AMP,0020;"),
        ("增益0dB", "ATA,SET,AMP,0000;"),
        ("输入电阻50Ω", "ATA,SET,RIN,0050;"),
        ("输出电阻50Ω", "ATA,SET,ROT,0500;"),
    ]
    
    success_count = 0
    fail_count = 0
    
    for i, (name, command) in enumerate(test_commands, 1):
        print(f"\n{'=' * 70}")
        print(f"测试 {i}/{len(test_commands)}: {name}")
        print(f"{'=' * 70}")
        
        # 添加换行符
        full_command = command + newline
        print(f"  发送: {full_command}")
        
        try:
            # 发送命令
            ser.write(full_command.encode('ascii'))
            
            # 等待响应
            time.sleep(0.3)
            
            # 读取响应
            if ser.in_waiting > 0:
                resp_bytes = ser.read(ser.in_waiting)
                resp_str = resp_bytes.decode('ascii', errors='ignore').strip()
                
                print(f"  响应: {resp_str}")
                
                # 分析响应
                if "SETDONE!" in resp_str:
                    print(f"  ✓ 命令执行成功")
                    success_count += 1
                elif "OVERRANGEERROR!" in resp_str:
                    print(f"  ✗ 参数越界")
                    fail_count += 1
                elif "SETERROR!" in resp_str:
                    print(f"  ✗ 指令错误")
                    fail_count += 1
                else:
                    print(f"  ? 未知响应: {resp_str}")
                    fail_count += 1
            else:
                print(f"  响应: (无数据)")
                fail_count += 1
        
        except Exception as e:
            print(f"  ✗ 发送失败: {e}")
            fail_count += 1
        
        time.sleep(0.5)
    
    # 断开连接
    ser.close()
    print(f"\n✓ 串口已断开")
    
    # 总结
    print(f"\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    print(f"\n测试结果:")
    print(f"  成功: {success_count}/{len(test_commands)}")
    print(f"  失败: {fail_count}/{len(test_commands)}")
    
    if success_count == len(test_commands):
        print(f"\n✓✓✓ 所有命令都成功！")
        print(f"  换行符: {repr(newline)}")
    elif success_count > 0:
        print(f"\n✓ 部分命令成功")
        print(f"  换行符: {repr(newline)}")
    else:
        print(f"\n✗ 所有命令都失败")


def main():
    """主函数"""
    print("=" * 70)
    print("ATA-101B换行符测试工具")
    print("=" * 70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试1: 找到正确的换行符
    print(f"\n【步骤1】测试不同的换行符")
    name, newline, resp = test_newlines()
    
    if newline:
        # 测试2: 使用正确的换行符测试所有命令
        print(f"\n【步骤2】使用正确的换行符测试所有命令")
        test_all_commands_with_newline(newline)
    else:
        print(f"\n✗ 未找到有效的换行符")
        print(f"可能需要其他配置")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n发生异常: {e}")
        import traceback
        traceback.print_exc()
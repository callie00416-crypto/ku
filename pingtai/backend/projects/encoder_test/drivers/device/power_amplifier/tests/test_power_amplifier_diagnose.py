"""
ATA-101B 功放通信诊断工具

【功能】
- 发送原始命令并显示十六进制数据
- 查看设备返回的原始响应
- 帮助诊断通信问题
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


def bytes_to_hex(data):
    """将字节数据转换为十六进制字符串"""
    if not data:
        return "<empty>"
    return ' '.join(f'{b:02X}' for b in data)


def bytes_to_ascii(data):
    """将字节数据转换为 ASCII 字符串"""
    if not data:
        return "<empty>"
    try:
        return data.decode('ascii').strip()
    except:
        return "<invalid ASCII>"


def test_raw_communication():
    """测试原始通信"""
    print("="*60)
    print("ATA-101B 功放通信诊断工具")
    print("="*60)
    
    print(f"\n串口: {SERIAL_PORT}")
    print(f"波特率: {BAUDRATE}")
    print(f"数据位: 8")
    print(f"校验位: None")
    print(f"停止位: 1\n")
    
    try:
        # 打开串口
        print("正在打开串口...")
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=2  # 2秒超时
        )
        print("✅ 串口打开成功\n")
        
        # 测试命令列表
        test_commands = [
            ("输出开", "ATA,SET,AON,0000;"),
            ("输出关", "ATA,SET,AOF,0000;"),
            ("增益设置(20dB)", "ATA,SET,AMP,0020;"),
            ("输入电阻(50Ω)", "ATA,SET,RIN,0050;"),
            ("输出电阻(50Ω)", "ATA,SET,ROT,0500;"),
            ("保存设置", "ATA,SET,SAV,0000;"),
        ]
        
        print("="*60)
        print("开始测试命令\n")
        
        for name, command in test_commands:
            print("-" * 60)
            print(f"测试: {name}")
            print(f"发送命令: {command}")
            
            # 清空接收缓冲区
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # 发送命令
            command_bytes = command.encode('ascii')
            print(f"发送数据(HEX): {bytes_to_hex(command_bytes)}")
            print(f"发送数据(ASCII): {command}")
            
            bytes_sent = ser.write(command_bytes)
            ser.flush()
            print(f"已发送 {bytes_sent} 字节")
            
            # 等待响应
            time.sleep(0.5)
            
            # 读取响应
            response_bytes = ser.read_all()
            
            if response_bytes:
                print(f"\n✅ 收到响应:")
                print(f"  数据(HEX): {bytes_to_hex(response_bytes)}")
                print(f"  数据(ASCII): {bytes_to_ascii(response_bytes)}")
                print(f"  字节数: {len(response_bytes)}")
                
                # 检查响应内容
                response_str = bytes_to_ascii(response_bytes)
                if "SET DONE!" in response_str:
                    print(f"  状态: ✅ 成功")
                elif "SET ERROR!" in response_str:
                    print(f"  状态: ❌ 命令错误")
                elif "OVER RANGE ERROR!" in response_str:
                    print(f"  状态: ❌ 参数越界")
                else:
                    print(f"  状态: ️  未知响应")
            else:
                print(f"\n❌ 未收到响应（超时）")
                print(f"  可能原因:")
                print(f"  1. 功放设备未通电")
                print(f"  2. RS485 接线错误（A/B 线接反）")
                print(f"  3. 设备需要特殊初始化")
                print(f"  4. 波特率不匹配")
            
            print()
            time.sleep(1)  # 命令间隔 1 秒
        
        print("="*60)
        print("\n诊断完成\n")
        
        # 关闭串口
        ser.close()
        print("✅ 串口已关闭\n")
        
    except serial.SerialException as e:
        print(f"\n❌ 串口错误: {e}\n")
    except Exception as e:
        print(f"\n❌ 异常: {e}\n")
        import traceback
        traceback.print_exc()


def test_echo_mode():
    """测试回显模式（检查线路）"""
    print("="*60)
    print("回显测试 - 检查 RS485 线路")
    print("="*60)
    
    print("\n此测试用于检查 RS485 A/B 线是否接反")
    print("将 RS485 的 A 和 B 短接，然后按回车继续...")
    input()
    
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1
        )
        
        print("\n发送测试数据 'HELLO'...")
        test_data = b'HELLO'
        ser.write(test_data)
        ser.flush()
        
        time.sleep(0.5)
        response = ser.read_all()
        
        if response == test_data:
            print("✅ 收到回显数据 - RS485 线路正常")
            print(f"   发送: {test_data}")
            print(f"   接收: {response}")
        else:
            print("❌ 未收到正确的回显数据")
            print(f"   发送: {test_data}")
            print(f"   接收: {response}")
            print("\n可能原因:")
            print("  1. RS485 A/B 线接反")
            print("  2. 线路连接不良")
            print("  3. 终端电阻问题")
        
        ser.close()
        
    except Exception as e:
        print(f"\n❌ 测试异常: {e}\n")


def show_wiring_guide():
    """显示接线指南"""
    print("\n" + "="*60)
    print("RS485 接线指南")
    print("="*60)
    
    print("""
功放 ATA-101B          USB转RS485线          电脑
─────────────         ┌──────────┐
│   RS485    │         │  USB     │
│            │         │  转      │
│  A+ (D+)   │◄───────►│  RS485   │──USB──► USB端口
│  B- (D-)   │◄───────►│  线      │
│  GND       │◄───────►│          │
└────────────         └──────────┘

注意事项:
1. A+ 接 A+（或 D+ 接 D+）
2. B- 接 B-（或 D- 接 D-）
3. GND 建议连接（可选）
4. 如果通信失败，尝试交换 A 和 B 线
5. 确保功放设备已通电

常见接线错误:
❌ A+ 接到 B-
❌ B- 接到 A+
❌ 只接了一根线
❌ 功放未通电
""")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("ATA-101B 功放通信诊断")
    print("="*60)
    print("\n请选择测试模式:")
    print("1. 原始通信测试（推荐）")
    print("2. 回显测试（检查线路）")
    print("3. 查看接线指南")
    print("4. 退出")
    
    while True:
        try:
            choice = input("\n请选择 (1-4): ").strip()
            
            if choice == '1':
                test_raw_communication()
            elif choice == '2':
                test_echo_mode()
            elif choice == '3':
                show_wiring_guide()
            elif choice == '4':
                print("\n退出诊断工具")
                break
            else:
                print("无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  诊断被中断")
            break
        except EOFError:
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")


if __name__ == '__main__':
    main()

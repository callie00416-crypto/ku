"""
ATA-101B驱动测试（直接使用协议）

【功能】
- 直接使用CustomASCIIProtocol测试
- 验证换行符支持
- 验证响应格式
"""
import sys
from pathlib import Path
import serial
import time

# 添加路径
current_file = Path(__file__).resolve()
backend_path = current_file.parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

from shared.drivers.protocol.custom_ascii_protocol import CustomASCIIProtocol


class SimpleSerialComm:
    """简单的串口通信层"""
    
    def __init__(self, port='COM3', baudrate=9600, timeout=2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
    
    def connect(self):
        """连接"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            print(f"✓ 串口连接成功")
            return True
        except Exception as e:
            print(f"✗ 串口连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"✓ 串口已断开")
    
    def send(self, data):
        """发送数据"""
        if self.ser and self.ser.is_open:
            self.ser.write(data)
    
    def recv(self, size=1024, timeout=1.0):
        """接收数据"""
        if self.ser and self.ser.is_open:
            time.sleep(0.3)
            if self.ser.in_waiting > 0:
                return self.ser.read(self.ser.in_waiting)
        return b''


def test_protocol():
    """测试协议"""
    print("=" * 70)
    print("ATA-101B协议测试")
    print("=" * 70)
    
    # 创建通信层
    print(f"\n创建通信层...")
    comm = SimpleSerialComm(port='COM3', baudrate=9600, timeout=2)
    
    # 创建协议层（使用正确的换行符）
    print(f"创建协议层...")
    protocol = CustomASCIIProtocol(
        driver_id='power_amplifier',
        comm=comm,
        command_prefix='ATA,SET,',
        command_suffix=';',
        newline='\r\n'  # 正确的换行符
    )
    
    # 连接
    print(f"\n连接设备...")
    if not protocol.connect():
        print("✗ 连接失败")
        return
    
    # 测试命令
    test_commands = [
        ("输出关", "AOF,0000"),
        ("增益0dB", "AMP,0000"),
        ("增益12dB", "AMP,0012"),
        ("输入电阻50Ω", "RIN,0050"),
        ("输出电阻50Ω", "ROT,0500"),
        ("保存设置", "SAV,0000"),
    ]
    
    success_count = 0
    fail_count = 0
    
    for i, (name, command) in enumerate(test_commands, 1):
        print(f"\n{'=' * 70}")
        print(f"测试 {i}/{len(test_commands)}: {name}")
        print(f"{'=' * 70}")
        print(f"  命令: {command}")
        
        try:
            response = protocol.send_command(command)
            print(f"  响应: {response}")
            
            if "SET DONE!" in response:
                print(f"  ✓✓✓ 命令执行成功！")
                success_count += 1
            elif "OVER RANGE ERROR!" in response:
                print(f"  ✗ 参数越界")
                fail_count += 1
            elif "SET ERROR!" in response:
                print(f"  ✗ 指令错误")
                fail_count += 1
            else:
                print(f"  ? 未知响应")
                fail_count += 1
        except Exception as e:
            print(f"  ✗ 执行异常: {e}")
            fail_count += 1
    
    # 断开连接
    print(f"\n断开连接...")
    protocol.disconnect()
    
    # 总结
    print(f"\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    print(f"\n测试结果:")
    print(f"  成功: {success_count}/{len(test_commands)}")
    print(f"  失败: {fail_count}/{len(test_commands)}")
    
    if success_count == len(test_commands):
        print(f"\n✓✓✓ 所有命令都成功！")
        print(f"  协议已正确配置")
        print(f"  换行符: \\r\\n")
        print(f"  响应格式: SET DONE!")
    elif success_count > 0:
        print(f"\n✓ 部分命令成功")
        print(f"  协议基本正常")
    else:
        print(f"\n✗ 所有命令都失败")


def main():
    """主函数"""
    try:
        test_protocol()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
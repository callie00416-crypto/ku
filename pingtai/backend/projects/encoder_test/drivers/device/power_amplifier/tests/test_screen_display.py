"""
ATA-101B功放屏幕显示测试

【功能】
- 发送各种命令到功放
- 让用户观察屏幕显示变化
- 验证命令是否生效
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


class PowerAmplifierTester:
    def __init__(self, port='COM3', baudrate=9600):
        """初始化测试器"""
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.newline = '\r\n'
        
    def connect(self):
        """连接串口"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=2
            )
            print(f"✓ 串口连接成功：{self.port}")
            return True
        except Exception as e:
            print(f"✗ 串口连接失败：{e}")
            return False
    
    def disconnect(self):
        """断开串口"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"✓ 串口已断开")
    
    def send_command(self, command):
        """发送命令"""
        if not self.ser or not self.ser.is_open:
            print("✗ 串口未连接")
            return ""
        
        full_command = command + self.newline
        
        try:
            self.ser.write(full_command.encode('ascii'))
            time.sleep(0.3)
            
            if self.ser.in_waiting > 0:
                resp_bytes = self.ser.read(self.ser.in_waiting)
                resp_str = resp_bytes.decode('ascii').strip()
                return resp_str
            else:
                return ""
        except Exception as e:
            print(f"✗ 发送失败：{e}")
            return ""
    
    def test_screen_display(self):
        """测试屏幕显示"""
        print("=" * 70)
        print("ATA-101B功放屏幕显示测试")
        print("=" * 70)
        print(f"\n请观察功放屏幕显示变化！")
        print(f"每个命令之间有3秒间隔，方便您观察。\n")
        
        time.sleep(2)
        
        # 测试序列
        test_sequence = [
            {
                "name": "初始状态",
                "command": None,
                "description": "请记录当前屏幕显示内容"
            },
            {
                "name": "输出关",
                "command": "ATA,SET,AOF,0000;",
                "description": "关闭输出，观察屏幕显示"
            },
            {
                "name": "增益0dB",
                "command": "ATA,SET,AMP,0000;",
                "description": "设置增益为0dB，观察屏幕显示"
            },
            {
                "name": "增益12dB",
                "command": "ATA,SET,AMP,0012;",
                "description": "设置增益为12dB，观察屏幕显示"
            },
            {
                "name": "增益20dB",
                "command": "ATA,SET,AMP,0020;",
                "description": "设置增益为20dB，观察屏幕显示"
            },
            {
                "name": "输入电阻50Ω",
                "command": "ATA,SET,RIN,0050;",
                "description": "设置输入电阻为50Ω，观察屏幕显示"
            },
            {
                "name": "输出电阻50Ω",
                "command": "ATA,SET,ROT,0500;",
                "description": "设置输出电阻为50Ω，观察屏幕显示"
            },
            {
                "name": "输出开",
                "command": "ATA,SET,AON,0000;",
                "description": "打开输出，观察屏幕显示"
            },
            {
                "name": "输出关",
                "command": "ATA,SET,AOF,0000;",
                "description": "关闭输出，观察屏幕显示"
            },
            {
                "name": "保存设置",
                "command": "ATA,SET,SAV,0000;",
                "description": "保存设置，观察屏幕显示"
            },
        ]
        
        for i, test in enumerate(test_sequence, 1):
            print(f"\n{'=' * 70}")
            print(f"测试 {i}/{len(test_sequence)}: {test['name']}")
            print(f"{'=' * 70}")
            print(f"说明: {test['description']}")
            
            if test['command']:
                print(f"命令: {test['command']}")
                
                resp = self.send_command(test['command'])
                
                if resp:
                    if "SET DONE!" in resp:
                        print(f"响应: SET DONE! ✓")
                    elif "SET ERROR!" in resp:
                        print(f"响应: SET ERROR! ✗")
                    elif "OVER RANGE ERROR!" in resp:
                        print(f"响应: OVER RANGE ERROR! ✗")
                    else:
                        print(f"响应: {resp}")
                else:
                    print(f"响应: (无数据)")
            else:
                print(f"命令: (无)")
            
            print(f"\n请观察屏幕显示变化...")
            print(f"您看到的变化：")
            
            # 等待用户观察
            time.sleep(3)
        
        print(f"\n{'=' * 70}")
        print("测试完成")
        print(f"{'=' * 70}")
        print(f"\n请总结您观察到的屏幕显示变化：")
        print(f"1. 初始状态：")
        print(f"2. 哪些命令引起了屏幕显示变化？")
        print(f"3. 屏幕显示的具体内容是什么？")
        print(f"4. 是否有错误信息？")


def main():
    """主函数"""
    print("=" * 70)
    print("ATA-101B功放屏幕显示测试")
    print("=" * 70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建测试器
    tester = PowerAmplifierTester(port='COM3', baudrate=9600)
    
    # 连接串口
    print(f"\n连接串口...")
    if not tester.connect():
        print("✗ 串口连接失败，无法继续测试")
        return
    
    # 测试屏幕显示
    tester.test_screen_display()
    
    # 断开连接
    print(f"\n断开连接...")
    tester.disconnect()
    
    print(f"\n测试结束，请总结您的观察结果！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n发生异常: {e}")
        import traceback
        traceback.print_exc()
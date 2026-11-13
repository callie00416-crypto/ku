"""
ATA-101B功放输出开关测试

【功能】
- 专门测试输出开关功能
- 让用户观察屏幕显示变化
- 验证开关是否生效
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


class PowerAmplifierSwitchTester:
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
    
    def test_output_switch(self):
        """测试输出开关"""
        print("=" * 70)
        print("ATA-101B功放输出开关测试")
        print("=" * 70)
        print(f"\n请仔细观察功放屏幕显示变化！")
        print(f"每个开关操作之间有5秒间隔，方便您观察。\n")
        
        time.sleep(2)
        
        # 测试开关序列
        switch_tests = [
            {
                "name": "初始状态",
                "command": None,
                "description": "请记录当前屏幕显示内容和输出状态"
            },
            {
                "name": "第1次 - 输出关",
                "command": "ATA,SET,AOF,0000;",
                "description": "关闭输出，观察屏幕显示和输出状态"
            },
            {
                "name": "第2次 - 输出开",
                "command": "ATA,SET,AON,0000;",
                "description": "打开输出，观察屏幕显示和输出状态"
            },
            {
                "name": "第3次 - 输出关",
                "command": "ATA,SET,AOF,0000;",
                "description": "关闭输出，观察屏幕显示和输出状态"
            },
            {
                "name": "第4次 - 输出开",
                "command": "ATA,SET,AON,0000;",
                "description": "打开输出，观察屏幕显示和输出状态"
            },
            {
                "name": "第5次 - 输出关",
                "command": "ATA,SET,AOF,0000;",
                "description": "关闭输出，观察屏幕显示和输出状态"
            },
            {
                "name": "第6次 - 输出开",
                "command": "ATA,SET,AON,0000;",
                "description": "打开输出，观察屏幕显示和输出状态"
            },
            {
                "name": "最终 - 输出关",
                "command": "ATA,SET,AOF,0000;",
                "description": "最终关闭输出，观察屏幕显示和输出状态"
            },
        ]
        
        for i, test in enumerate(switch_tests, 1):
            print(f"\n{'=' * 70}")
            print(f"测试 {i}/{len(switch_tests)}: {test['name']}")
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
            
            print(f"\n⏱️  请观察屏幕显示变化（5秒）...")
            print(f"👀 您看到的变化：")
            
            # 等待用户观察
            time.sleep(5)
        
        print(f"\n{'=' * 70}")
        print("测试完成")
        print(f"{'=' * 70}")
        print(f"\n请总结您观察到的输出开关效果：")
        print(f"1. 输出开时，屏幕显示什么？输出状态是什么？")
        print(f"2. 输出关时，屏幕显示什么？输出状态是什么？")
        print(f"3. 屏幕上是否有输出状态指示？")
        print(f"4. 开关切换时屏幕是否有明显变化？")
        print(f"5. 是否有LED指示灯变化？")


def main():
    """主函数"""
    print("=" * 70)
    print("ATA-101B功放输出开关测试")
    print("=" * 70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建测试器
    tester = PowerAmplifierSwitchTester(port='COM3', baudrate=9600)
    
    # 连接串口
    print(f"\n连接串口...")
    if not tester.connect():
        print("✗ 串口连接失败，无法继续测试")
        return
    
    # 测试输出开关
    tester.test_output_switch()
    
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
"""
ATA-101B 功放交互式调试工具

【功能】
提供命令行交互界面，可以逐个测试功放的各项功能

【使用说明】
1. 修改 SERIAL_PORT 为你的串口
2. 运行: python test_power_amplifier_interactive.py
3. 按照提示输入命令
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.drivers.comm.rs485_comm import RS485Comm
from shared.drivers.protocol.custom_ascii_protocol import CustomASCIIProtocol
from projects.encoder_test.drivers.device.power_amplifier.power_amplifier import ATA101BPowerAmplifier


# ===== 配置区 =====
# 使用 USB 转串口线连接功放
# 运行 test_detect_usb_serial.py 自动检测正确的 COM 端口
SERIAL_PORT = 'COM3'  # 修改为检测到的端口号（如 COM3, COM5 等）
BAUDRATE = 9600
# ==================


class PowerAmplifierDebugger:
    """功放调试器"""
    
    def __init__(self):
        self.comm = None
        self.protocol = None
        self.device = None
        self.connected = False
    
    def connect(self):
        """连接设备"""
        print(f"\n正在连接串口 {SERIAL_PORT}...")
        
        try:
            # 创建通信层
            self.comm = RS485Comm(
                driver_id='power_amplifier_rs485',
                port=SERIAL_PORT,
                baudrate=BAUDRATE,
                auto_cleanup=True,
                acquire_timeout=10.0
            )
            
            if not self.comm.open():
                print("❌ 串口打开失败")
                return False
            
            # 创建协议层
            self.protocol = CustomASCIIProtocol(
                driver_id='power_amplifier_protocol',
                comm=self.comm,
                command_prefix='ATA,SET,',
                command_suffix=';'
            )
            
            # 创建设备层
            self.device = ATA101BPowerAmplifier(
                driver_id='power_amplifier',
                protocol=self.protocol
            )
            
            if not self.device.connect():
                print("❌ 设备连接失败")
                return False
            
            self.connected = True
            print("✅ 设备连接成功")
            return True
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开设备"""
        if self.device:
            self.device.disconnect()
            self.connected = False
            print("✅ 设备已断开")
    
    def show_status(self):
        """显示设备状态"""
        if not self.connected:
            print("❌ 设备未连接")
            return
        
        status = self.device.get_status()
        print("\n" + "="*40)
        print("设备状态")
        print("="*40)
        print(f"输出使能: {'ON' if status['output_enabled'] else 'OFF'}")
        print(f"输入电阻: {status['input_resistance']}Ω")
        print(f"输出电阻: {status['output_resistance']}Ω")
        print(f"增益: {status['gain']}dB")
        print("="*40)
    
    def output_on(self):
        """打开输出"""
        if not self.connected:
            print("❌ 设备未连接")
            return
        
        if self.device.output_on():
            print("✅ 输出已打开")
        else:
            print("❌ 输出打开失败")
    
    def output_off(self):
        """关闭输出"""
        if not self.connected:
            print("❌ 设备未连接")
            return
        
        if self.device.output_off():
            print("✅ 输出已关闭")
        else:
            print("❌ 输出关闭失败")
    
    def set_gain(self):
        """设置增益"""
        if not self.connected:
            print("❌ 设备未连接")
            return
        
        try:
            gain = input("请输入增益值 (0-20dB, 步进2): ")
            gain = int(gain)
            
            if self.device.set_gain(gain):
                print(f"✅ 增益已设置为 {gain}dB")
            else:
                print(f"❌ 增益设置失败")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    def set_input_resistance(self):
        """设置输入电阻"""
        if not self.connected:
            print("❌ 设备未连接")
            return
        
        try:
            resistance = input("请输入输入电阻值 (50 或 1000): ")
            resistance = float(resistance)
            
            if self.device.set_input_resistance(resistance):
                print(f"✅ 输入电阻已设置为 {resistance}Ω")
            else:
                print(f"❌ 输入电阻设置失败")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    def set_output_resistance(self):
        """设置输出电阻"""
        if not self.connected:
            print("❌ 设备未连接")
            return
        
        try:
            resistance = input("请输入输出电阻值 (1.5 或 50): ")
            resistance = float(resistance)
            
            if self.device.set_output_resistance(resistance):
                print(f"✅ 输出电阻已设置为 {resistance}Ω")
            else:
                print(f"❌ 输出电阻设置失败")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    def save_settings(self):
        """保存设置"""
        if not self.connected:
            print("❌ 设备未连接")
            return
        
        if self.device.save_settings():
            print("✅ 设置已保存")
        else:
            print("❌ 设置保存失败")
    
    def reset_device(self):
        """重置设备"""
        if not self.connected:
            print(" 设备未连接")
            return
        
        if self.device.reset():
            print("✅ 设备已重置")
        else:
            print("❌ 设备重置失败")
    
    def show_help(self):
        """显示帮助"""
        print("\n" + "="*40)
        print("可用命令")
        print("="*40)
        print("status        - 显示设备状态")
        print("on            - 打开输出")
        print("off           - 关闭输出")
        print("gain          - 设置增益")
        print("rin           - 设置输入电阻")
        print("rout          - 设置输出电阻")
        print("save          - 保存设置")
        print("reset         - 重置设备")
        print("help          - 显示帮助")
        print("quit/exit     - 退出")
        print("="*40)
    
    def run(self):
        """运行交互式调试"""
        print("="*40)
        print("ATA-101B 功放交互式调试工具")
        print("="*40)
        
        # 连接设备
        if not self.connect():
            print("无法连接设备，退出")
            return
        
        self.show_help()
        
        # 交互循环
        while True:
            try:
                cmd = input("\n> ").strip().lower()
                
                if cmd in ['quit', 'exit', 'q']:
                    break
                elif cmd == 'status':
                    self.show_status()
                elif cmd == 'on':
                    self.output_on()
                elif cmd == 'off':
                    self.output_off()
                elif cmd == 'gain':
                    self.set_gain()
                elif cmd == 'rin':
                    self.set_input_resistance()
                elif cmd == 'rout':
                    self.set_output_resistance()
                elif cmd == 'save':
                    self.save_settings()
                elif cmd == 'reset':
                    self.reset_device()
                elif cmd == 'help':
                    self.show_help()
                else:
                    print(f"未知命令: {cmd}")
                    print("输入 'help' 查看可用命令")
                    
            except KeyboardInterrupt:
                print("\n\n️  调试被中断")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
        
        # 断开设备
        self.disconnect()
        print("退出调试工具")


def main():
    """主函数"""
    debugger = PowerAmplifierDebugger()
    debugger.run()


if __name__ == '__main__':
    main()

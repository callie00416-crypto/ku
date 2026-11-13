"""
USB 串口自动检测工具

【功能】
自动检测系统中的 USB 转串口设备，帮助确定功放设备的串口号
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import serial.tools.list_ports


def detect_usb_serial_ports():
    """检测 USB 转串口设备"""
    print("="*60)
    print("USB 串口自动检测工具")
    print("="*60)
    
    print("\n正在扫描系统串口...\n")
    
    # 获取所有串口
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ 未找到任何串口设备")
        print("\n可能的原因:")
        print("1. USB 转串口线未连接")
        print("2. 驱动程序未安装")
        print("3. 串口被其他程序占用")
        return None
    
    print(f"找到 {len(ports)} 个串口设备:\n")
    print("-" * 60)
    
    usb_ports = []
    
    for i, port in enumerate(ports, 1):
        is_usb = False
        port_type = ""
        
        # 检测是否为 USB 串口
        usb_indicators = ['USB', 'CH340', 'CH341', 'CP210', 'FTDI', 'FT232', 
                         'PL2303', 'Silicon Labs', 'FTDI']
        
        description_upper = port.description.upper()
        hwid_upper = port.hwid.upper() if port.hwid else ""
        
        for indicator in usb_indicators:
            if indicator.upper() in description_upper or indicator.upper() in hwid_upper:
                is_usb = True
                port_type = "USB 转串口"
                break
        
        if not is_usb:
            port_type = "内置串口"
        
        print(f"{i}. {port.device}")
        print(f"   描述: {port.description}")
        print(f"   类型: {port_type}")
        
        if port.manufacturer:
            print(f"   制造商: {port.manufacturer}")
        
        if port.serial_number:
            print(f"   序列号: {port.serial_number}")
        
        if port.hwid:
            print(f"   硬件ID: {port.hwid}")
        
        if is_usb:
            usb_ports.append(port.device)
            print(f"   ✅ 推荐用于功放设备")
        
        print()
    
    print("-" * 60)
    
    if usb_ports:
        print(f"\n✅ 找到 {len(usb_ports)} 个 USB 转串口设备:")
        for port in usb_ports:
            print(f"   - {port}")
        
        # 推荐第一个 USB 串口
        recommended_port = usb_ports[0]
        print(f"\n💡 推荐使用: {recommended_port}")
        return recommended_port
    else:
        print("\n⚠️  未找到 USB 转串口设备")
        print("\n可能的解决方案:")
        print("1. 检查 USB 转串口线是否连接")
        print("2. 安装串口驱动程序")
        print("   - CH340/CH341: http://www.wch.cn/downloads/CH341SER_ZIP.html")
        print("   - CP210x: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers")
        print("   - FTDI: https://ftdichip.com/drivers/vcp-drivers/")
        print("3. 在设备管理器中查看端口列表")
        return None


def test_port_communication(port, baudrate=9600):
    """测试串口通信"""
    print(f"\n测试串口 {port} 通信...")
    
    try:
        import serial
        
        # 尝试打开串口
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1
        )
        
        print(f"✅ 串口 {port} 打开成功")
        print(f"   波特率: {baudrate}")
        print(f"   数据位: 8")
        print(f"   校验位: None")
        print(f"   停止位: 1")
        
        # 关闭串口
        ser.close()
        print(f"✅ 串口 {port} 关闭成功")
        
        return True
        
    except serial.SerialException as e:
        print(f"❌ 串口 {port} 通信失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 串口 {port} 测试异常: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("USB 串口检测与测试工具")
    print("="*60)
    
    # 检测 USB 串口
    recommended_port = detect_usb_serial_ports()
    
    if recommended_port:
        # 测试通信
        test_port_communication(recommended_port)
        
        print("\n" + "="*60)
        print("配置建议")
        print("="*60)
        print(f"\n请在调试脚本中设置:")
        print(f'  SERIAL_PORT = \'{recommended_port}\'')
        print(f'  BAUDRATE = 9600')
        
        print("\n" + "="*60)
        print("下一步")
        print("="*60)
        print("\n1. 确认功放设备已连接到该串口")
        print("2. 运行功放调试脚本:")
        print(f"   python test_power_amplifier.py")
        print("\n3. 或使用交互式调试:")
        print(f"   python test_power_amplifier_interactive.py")
    else:
        print("\n" + "="*60)
        print("未找到可用的 USB 串口")
        print("="*60)
        print("\n请检查:")
        print("1. USB 转串口线是否正确连接")
        print("2. 驱动程序是否已安装")
        print("3. 设备管理器中是否能看到串口设备")
        print("\nWindows 设备管理器查看方法:")
        print("  1. 右键 '此电脑' -> '管理'")
        print("  2. 展开 '端口 (COM 和 LPT)'")
        print("  3. 查看 COM 端口列表")


if __name__ == '__main__':
    main()

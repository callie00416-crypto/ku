"""
USB设备检测工具

【功能】
- 检测所有USB设备
- 查找ATA-101B设备
- 分析设备通信协议
- 尝试不同的通信方式
"""
import sys
import time
from pathlib import Path

# 添加路径
current_file = Path(__file__).resolve()
backend_path = current_file.parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    print("⚠️ pyusb未安装，跳过USB设备检测")
    print("   安装命令: pip install pyusb")

try:
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("⚠️ pyserial未安装，跳过串口检测")
    print("   安装命令: pip install pyserial")


def detect_usb_devices():
    """检测USB设备"""
    print("=" * 70)
    print("USB设备检测")
    print("=" * 70)
    
    if not USB_AVAILABLE:
        print("✗ USB检测功能不可用")
        return
    
    try:
        # 查找所有USB设备
        devices = usb.core.find(find_all=True)
        
        if not devices:
            print("✗ 未找到USB设备")
            return
        
        print(f"\n找到 {len(devices)} 个USB设备:\n")
        
        for i, dev in enumerate(devices, 1):
            try:
                # 获取设备信息
                vendor_id = hex(dev.idVendor)
                product_id = hex(dev.idProduct)
                
                # 尝试获取设备名称
                manufacturer = usb.util.get_string(dev, dev.iManufacturer) if dev.iManufacturer else "未知"
                product = usb.util.get_string(dev, dev.iProduct) if dev.iProduct else "未知"
                
                print(f"{i}. 设备:")
                print(f"   厂商ID: {vendor_id}")
                print(f"   产品ID: {product_id}")
                print(f"   厂商: {manufacturer}")
                print(f"   产品: {product}")
                
                # 检查是否是ATA-101B
                if "ATA" in product or "101" in product or "安泰" in manufacturer:
                    print(f"   ⭐ 可能是ATA-101B设备！")
                
                print()
                
            except Exception as e:
                print(f"{i}. 设备: (读取失败: {e})")
                print()
    
    except Exception as e:
        print(f"✗ USB检测失败: {e}")


def detect_serial_ports():
    """检测串口"""
    print("=" * 70)
    print("串口检测")
    print("=" * 70)
    
    if not SERIAL_AVAILABLE:
        print("✗ 串口检测功能不可用")
        return
    
    try:
        ports = serial.tools.list_ports.comports()
        
        if not ports:
            print("✗ 未找到串口")
            return
        
        print(f"\n找到 {len(ports)} 个串口:\n")
        
        for i, port in enumerate(ports, 1):
            print(f"{i}. {port.device}")
            print(f"   描述: {port.description}")
            print(f"   硬件ID: {port.hwid}")
            
            # 检查是否是USB虚拟串口
            if "USB" in port.description or "USB" in port.hwid:
                print(f"   ⭐ USB虚拟串口")
            
            # 检查是否是ATA-101B
            if "ATA" in port.description or "101" in port.description or "安泰" in port.description:
                print(f"   ⭐ 可能是ATA-101B设备！")
            
            print()
    
    except Exception as e:
        print(f"✗ 串口检测失败: {e}")


def analyze_communication_protocol():
    """分析通信协议"""
    print("=" * 70)
    print("通信协议分析")
    print("=" * 70)
    
    print("\n如果设备直接使用USB连接，可能的通信方式:")
    print("1. USB虚拟串口（CDC-ACM）")
    print("   - 设备模拟串口通信")
    print("   - 使用串口协议")
    print("   - 需要正确的串口参数")
    
    print("\n2. USB HID（人机接口设备）")
    print("   - 使用HID协议")
    print("   - 需要使用HID库")
    print("   - 通信方式不同")
    
    print("\n3. USB自定义协议")
    print("   - 厂商自定义协议")
    print("   - 需要厂商提供的SDK")
    print("   - 可能需要特定驱动")
    
    print("\n4. USB大容量存储")
    print("   - 设备模拟U盘")
    print("   - 通过文件通信")
    print("   - 需要文件操作")


def main():
    """主函数"""
    print("=" * 70)
    print("ATA-101B设备USB检测工具")
    print("=" * 70)
    
    # 检测USB设备
    print(f"\n[1/3] 检测USB设备...")
    detect_usb_devices()
    
    # 检测串口
    print(f"\n[2/3] 检测串口...")
    detect_serial_ports()
    
    # 分析通信协议
    print(f"\n[3/3] 分析通信协议...")
    analyze_communication_protocol()
    
    # 建议
    print(f"\n{'=' * 70}")
    print("建议")
    print(f"{'=' * 70}")
    
    print("\n1. 查看设备手册")
    print("   - 确认USB通信协议")
    print("   - 查看是否有专用驱动")
    print("   - 确认通信参数")
    
    print("\n2. 查看设备管理器")
    print("   - 查看设备类型")
    print("   - 查看驱动程序")
    print("   - 查看设备属性")
    
    print("\n3. 尝试厂商软件")
    print("   - 使用厂商提供的控制软件")
    print("   - 观察软件如何通信")
    print("   - 使用USB分析工具")
    
    print("\n4. 联系厂商")
    print("   - 确认USB通信协议")
    print("   - 获取通信SDK")
    print("   - 获取技术支持")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n检测被用户中断")
    except Exception as e:
        print(f"\n发生异常: {e}")
        import traceback
        traceback.print_exc()
"""
真实设备测试脚本 - 编码器上断电测试用例

【设备配置】
- 功率放大器: ATA-101B (COM3, 115200 baud)
- 波形发生器: RIGOL DG811 (USB, USBTMC)
- 编码器: DPT磁双编码器 (COM4, 2500000 baud)

【前置条件】
1. 所有设备已正确连接
2. 设备驱动已安装
3. NI-VISA 已安装（用于波形发生器）
"""
import sys
import os

# 添加 backend 到 Python 路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 导入测试用例
from projects.encoder_test.core.testcase.encoder.encoder_power_cycle_case import (
    EncoderPowerCycleCase,
    EncoderSinglePowerCycleCase
)

# 导入设备驱动
from shared.drivers.comm.rs485_comm import RS485Comm
from shared.drivers.protocol.custom_ascii import CustomAsciiProtocol
from shared.drivers.protocol.scpi_protocol import SCPIProtocol
from projects.encoder_test.drivers.device.power_amplifier.power_amplifier import ATA101BPowerAmplifier
from projects.encoder_test.drivers.device.waveform_generator.dg811 import DG811WaveformGenerator
from projects.encoder_test.drivers.device.encoder.analyzer_encoder import AnalyzerEncoderDriver

# 导入 USB VISA 通信
import pyvisa


def create_power_amplifier(port='COM3', baudrate=115200):
    """创建功率放大器设备"""
    print(f"\n创建功率放大器: {port}, {baudrate} baud")
    
    # 创建通信层
    comm = SerialComm(
        driver_id='serial_pa',
        port=port,
        baudrate=baudrate,
        timeout=2.0
    )
    
    # 创建协议层
    protocol = CustomAsciiProtocol(
        driver_id='ascii_pa',
        comm=comm
    )
    
    # 创建设备驱动
    power_amp = ATA101BPowerAmplifier(
        driver_id='power_amplifier',
        protocol=protocol
    )
    
    # 连接设备
    if power_amp.connect():
        print(f"✅ 功率放大器连接成功")
        return power_amp
    else:
        print(f"❌ 功率放大器连接失败")
        return None


def create_waveform_generator(resource_string='USB0::0x1AB1::0x0643::DG8A272300397::INSTR'):
    """创建波形发生器设备"""
    print(f"\n创建波形发生器: {resource_string}")
    
    try:
        # 导入 USB VISA 通信驱动
        from shared.drivers.comm.usb_visa_comm import USBVisaComm
        from shared.drivers.protocol.scpi_protocol import SCPIProtocol
        
        # 解析资源字符串获取 VID 和 PID
        # USB0::0x1AB1::0x0643::DG8A272300397::INSTR
        parts = resource_string.split('::')
        if len(parts) >= 3:
            vid = int(parts[1], 16)  # 0x1AB1
            pid = int(parts[2], 16)  # 0x0643
        else:
            raise ValueError(f"无效的资源字符串: {resource_string}")
        
        # 创建通信层
        comm = USBVisaComm(
            driver_id='usb_visa_dg811',
            vid=vid,
            pid=pid
        )
        
        # 创建协议层
        protocol = SCPIProtocol(
            driver_id='scpi_dg811',
            comm=comm
        )
        
        # 创建设备驱动
        waveform_gen = DG811WaveformGenerator(
            driver_id='waveform_generator',
            protocol=protocol
        )
        
        # 连接设备
        if waveform_gen.connect():
            print(f"✅ 波形发生器连接成功")
            return waveform_gen
        else:
            print(f"❌ 波形发生器连接失败")
            return None
        
    except Exception as e:
        print(f"❌ 波形发生器连接失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_encoder(com_port='COM4', baud_rate=2500000):
    """创建编码器设备"""
    print(f"\n创建编码器: {com_port}, {baud_rate} baud")
    
    # 创建设备驱动
    encoder = AnalyzerEncoderDriver(
        driver_id='encoder',
        com_port=com_port
    )
    
    # 连接设备
    if encoder.connect():
        print(f"✅ 编码器连接成功")
        return encoder
    else:
        print(f"❌ 编码器连接失败")
        return None


def test_single_power_cycle_real():
    """测试单次上断电（真实设备）"""
    print("\n" + "="*60)
    print("测试单次上断电循环（真实设备）")
    print("="*60)
    
    # 创建设备
    power_amp = create_power_amplifier(port='COM3')
    encoder = create_encoder(com_port='COM4')
    
    if not power_amp or not encoder:
        print("\n❌ 设备创建失败，无法进行测试")
        return None
    
    try:
        # 创建测试用例
        case = EncoderSinglePowerCycleCase(
            power_amplifier=power_amp,
            encoder=encoder,
            case_id="single_power_cycle_real",
            use_mock=False
        )
        
        # 设置参数
        case.set_parameter('power_off_delay', 1.0)
        case.set_parameter('power_on_delay', 2.0)
        case.set_parameter('tolerance', 0.5)
        
        # 执行测试
        result = case.execute()
        
        print(f"\n测试结果: {result.status.value}")
        print(f"测试消息: {result.message}")
        if result.data:
            print(f"测试数据: {result.data}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # 清理设备
        if power_amp:
            power_amp.output_off()
            power_amp.disconnect()
        if encoder:
            encoder.disconnect()


def test_multiple_power_cycle_real(cycle_count=3):
    """测试多次上断电循环（真实设备）"""
    print("\n" + "="*60)
    print(f"测试多次上断电循环 {cycle_count}次（真实设备）")
    print("="*60)
    
    # 创建设备
    power_amp = create_power_amplifier(port='COM3')
    waveform_gen = create_waveform_generator()  # 如果波形发生器不可用，可以传 None
    encoder = create_encoder(com_port='COM4')
    
    if not power_amp or not encoder:
        print("\n❌ 设备创建失败，无法进行测试")
        return None
    
    try:
        # 创建测试用例
        case = EncoderPowerCycleCase(
            power_amplifier=power_amp,
            waveform_generator=waveform_gen,
            encoder=encoder,
            case_id="multi_power_cycle_real",
            use_mock=False
        )
        
        # 设置参数
        case.set_parameter('cycle_count', cycle_count)
        case.set_parameter('power_off_delay', 1.0)
        case.set_parameter('power_on_delay', 2.0)
        case.set_parameter('tolerance', 0.5)
        case.set_parameter('waveform_type', 'SIN')
        case.set_parameter('frequency', 1000.0)
        case.set_parameter('amplitude', 5.0)
        case.set_parameter('gain', 20)
        
        # 执行测试
        result = case.execute()
        
        print(f"\n测试结果: {result.status.value}")
        print(f"测试消息: {result.message}")
        if result.data:
            print(f"测试数据: {result.data}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # 清理设备
        if power_amp:
            power_amp.output_off()
            power_amp.disconnect()
        if waveform_gen:
            waveform_gen.disconnect()
        if encoder:
            encoder.disconnect()


def list_available_ports():
    """列出可用的串口"""
    import serial.tools.list_ports
    
    print("\n" + "="*60)
    print("可用串口列表")
    print("="*60)
    
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"  {port.device}: {port.description}")
    
    if not ports:
        print("  未检测到串口设备")


def list_visa_devices():
    """列出可用的 VISA 设备"""
    try:
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        
        print("\n" + "="*60)
        print("可用 VISA 设备")
        print("="*60)
        
        if resources:
            for resource in resources:
                print(f"  {resource}")
        else:
            print("  未检测到 VISA 设备")
        
        rm.close()
    except Exception as e:
        print(f"\n❌ 无法列出 VISA 设备: {e}")


if __name__ == '__main__':
    print("="*60)
    print("编码器上断电测试 - 真实设备模式")
    print("="*60)
    
    # 列出可用设备
    list_available_ports()
    list_visa_devices()
    
    # 询问用户选择测试类型
    print("\n请选择测试类型:")
    print("1. 单次上断电测试")
    print("2. 多次上断电循环测试（3次）")
    print("3. 多次上断电循环测试（10次）")
    print("0. 退出")
    
    choice = input("\n请输入选项 (0-3): ").strip()
    
    if choice == '1':
        test_single_power_cycle_real()
    elif choice == '2':
        test_multiple_power_cycle_real(cycle_count=3)
    elif choice == '3':
        test_multiple_power_cycle_real(cycle_count=10)
    elif choice == '0':
        print("退出测试")
    else:
        print("无效选项")
    
    print("\n测试完成")
"""
ATA-101B 功放调试脚本

【调试功能】
1. 串口连接测试
2. 开关控制测试
3. 参数设置测试（增益、输入电阻、输出电阻）
4. 状态查询
5. 设置保存
6. 完整流程测试

【使用说明】
修改 SERIAL_PORT 为你的串口名称（Windows: COM1, COM3 等；Linux: /dev/ttyUSB0 等）
然后运行: python test_power_amplifier.py
"""
import sys
import time
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
BAUDRATE = 9600       # 根据功放协议文档设置
# ==================


def test_connection(comm, protocol, device):
    """测试1: 连接测试"""
    print("\n" + "="*60)
    print("测试1: 连接测试")
    print("="*60)
    
    print(f"\n正在连接串口 {SERIAL_PORT}...")
    if comm.open():
        print("✅ 串口打开成功")
    else:
        print("❌ 串口打开失败")
        return False
    
    print(f"\n正在连接设备...")
    if device.connect():
        print("✅ 设备连接成功")
        return True
    else:
        print("❌ 设备连接失败")
        return False


def test_output_control(device):
    """测试2: 开关控制测试"""
    print("\n" + "="*60)
    print("测试2: 开关控制测试")
    print("="*60)
    
    # 测试打开输出
    print("\n测试: 打开输出")
    if device.output_on():
        print("✅ 输出打开成功")
    else:
        print("❌ 输出打开失败")
        return False
    
    time.sleep(1)  # 等待1秒
    
    # 检查状态
    status = device.get_status()
    print(f"当前状态: {status}")
    
    # 测试关闭输出
    print("\n测试: 关闭输出")
    if device.output_off():
        print("✅ 输出关闭成功")
    else:
        print("❌ 输出关闭失败")
        return False
    
    time.sleep(1)
    
    # 再次检查状态
    status = device.get_status()
    print(f"当前状态: {status}")
    
    return True


def test_gain_setting(device):
    """测试3: 增益设置测试"""
    print("\n" + "="*60)
    print("测试3: 增益设置测试")
    print("="*60)
    
    test_gains = [0, 12, 20]
    
    for gain in test_gains:
        print(f"\n测试: 设置增益为 {gain}dB")
        if device.set_gain(gain):
            print(f"✅ 增益设置成功: {gain}dB")
        else:
            print(f"❌ 增益设置失败: {gain}dB")
            return False
        
        time.sleep(1)
        
        # 检查状态
        status = device.get_status()
        print(f"当前增益: {status['gain']}dB")
    
    return True


def test_input_resistance(device):
    """测试4: 输入电阻设置测试"""
    print("\n" + "="*60)
    print("测试4: 输入电阻设置测试")
    print("="*60)
    
    test_resistances = [50.0, 1000.0]
    
    for resistance in test_resistances:
        print(f"\n测试: 设置输入电阻为 {resistance}Ω")
        if device.set_input_resistance(resistance):
            print(f"✅ 输入电阻设置成功: {resistance}Ω")
        else:
            print(f"❌ 输入电阻设置失败: {resistance}Ω")
            return False
        
        time.sleep(1)
        
        # 检查状态
        status = device.get_status()
        print(f"当前输入电阻: {status['input_resistance']}Ω")
    
    return True


def test_output_resistance(device):
    """测试5: 输出电阻设置测试"""
    print("\n" + "="*60)
    print("测试5: 输出电阻设置测试")
    print("="*60)
    
    test_resistances = [1.5, 50.0]
    
    for resistance in test_resistances:
        print(f"\n测试: 设置输出电阻为 {resistance}Ω")
        if device.set_output_resistance(resistance):
            print(f"✅ 输出电阻设置成功: {resistance}Ω")
        else:
            print(f"❌ 输出电阻设置失败: {resistance}Ω")
            return False
        
        time.sleep(1)
        
        # 检查状态
        status = device.get_status()
        print(f"当前输出电阻: {status['output_resistance']}Ω")
    
    return True


def test_save_settings(device):
    """测试6: 保存设置测试"""
    print("\n" + "="*60)
    print("测试6: 保存设置测试")
    print("="*60)
    
    print("\n测试: 保存设置")
    if device.save_settings():
        print("✅ 设置保存成功")
        return True
    else:
        print("❌ 设置保存失败")
        return False


def test_full_workflow(device):
    """测试7: 完整流程测试"""
    print("\n" + "="*60)
    print("测试7: 完整流程测试")
    print("="*60)
    
    print("\n执行完整工作流程:")
    print("1. 设置增益为 20dB")
    print("2. 设置输入电阻为 1000Ω")
    print("3. 设置输出电阻为 50Ω")
    print("4. 打开输出")
    print("5. 保存设置")
    print("6. 关闭输出")
    
    # 设置参数
    if not device.set_gain(20):
        print("❌ 增益设置失败")
        return False
    print("✅ 增益设置成功")
    
    time.sleep(0.5)
    
    if not device.set_input_resistance(1000.0):
        print("❌ 输入电阻设置失败")
        return False
    print("✅ 输入电阻设置成功")
    
    time.sleep(0.5)
    
    if not device.set_output_resistance(50.0):
        print("❌ 输出电阻设置失败")
        return False
    print("✅ 输出电阻设置成功")
    
    time.sleep(0.5)
    
    # 打开输出
    if not device.output_on():
        print("❌ 输出打开失败")
        return False
    print("✅ 输出打开成功")
    
    time.sleep(1)
    
    # 保存设置
    if not device.save_settings():
        print("❌ 设置保存失败")
        return False
    print("✅ 设置保存成功")
    
    time.sleep(0.5)
    
    # 关闭输出
    if not device.output_off():
        print("❌ 输出关闭失败")
        return False
    print("✅ 输出关闭成功")
    
    # 最终状态
    print("\n最终状态:")
    status = device.get_status()
    for key, value in status.items():
        if key != 'device_info':
            print(f"  {key}: {value}")
    
    return True


def test_invalid_parameters(device):
    """测试8: 无效参数测试"""
    print("\n" + "="*60)
    print("测试8: 无效参数测试")
    print("="*60)
    
    print("\n测试无效增益值 (应该失败):")
    result = device.set_gain(15)  # 15不是2的倍数
    print(f"设置增益15dB: {'✅ 正确拒绝' if not result else ' 错误接受'}")
    
    result = device.set_gain(25)  # 超出范围
    print(f"设置增益25dB: {'✅ 正确拒绝' if not result else '❌ 错误接受'}")
    
    print("\n测试无效电阻值 (应该失败):")
    result = device.set_input_resistance(100.0)  # 无效值
    print(f"设置输入电阻100Ω: {'✅ 正确拒绝' if not result else '❌ 错误接受'}")
    
    result = device.set_output_resistance(10.0)  # 无效值
    print(f"设置输出电阻10Ω: {'✅ 正确拒绝' if not result else '❌ 错误接受'}")
    
    return True


def main():
    """主函数"""
    print("="*60)
    print("ATA-101B 功放调试脚本")
    print("="*60)
    print(f"\n串口: {SERIAL_PORT}")
    print(f"波特率: {BAUDRATE}")
    
    try:
        # 创建通信层
        print("\n创建通信层...")
        comm = RS485Comm(
            driver_id='power_amplifier_rs485',
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            auto_cleanup=True,
            acquire_timeout=10.0
        )
        
        # 创建协议层
        print("创建协议层...")
        protocol = CustomASCIIProtocol(
            driver_id='power_amplifier_protocol',
            comm=comm,
            command_prefix='ATA,SET,',
            command_suffix=';'
        )
        
        # 创建设备层
        print("创建设备层...")
        device = ATA101BPowerAmplifier(
            driver_id='power_amplifier',
            protocol=protocol
        )
        
        # 运行测试
        if test_connection(comm, protocol, device):
            test_output_control(device)
            test_gain_setting(device)
            test_input_resistance(device)
            test_output_resistance(device)
            test_save_settings(device)
            test_full_workflow(device)
            test_invalid_parameters(device)
            
            print("\n" + "="*60)
            print("✅ 所有调试测试完成")
            print("="*60)
        else:
            print("\n❌ 连接失败，无法继续测试")
        
        # 清理资源
        print("\n清理资源...")
        device.disconnect()
        print("✅ 资源清理完成")
        
    except KeyboardInterrupt:
        print("\n\n️  调试被中断")
        # 确保清理资源
        try:
            device.disconnect()
        except:
            pass
    except Exception as e:
        print(f"\n\n❌ 调试异常: {e}")
        import traceback
        traceback.print_exc()
        # 确保清理资源
        try:
            device.disconnect()
        except:
            pass


if __name__ == '__main__':
    main()

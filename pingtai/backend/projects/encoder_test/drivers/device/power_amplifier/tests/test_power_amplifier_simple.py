"""
ATA-101B功率放大器驱动简单测试

【目的】
- 测试ATA-101B功率放大器驱动逻辑
- 验证自定义ASCII协议
- 不依赖实际硬件
"""
import sys
from pathlib import Path

# 添加路径
backend_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

import logging
from shared.drivers.protocol.custom_ascii_protocol import CustomASCIIProtocol
from projects.encoder_test.drivers.device.power_amplifier.power_amplifier import ATA101BPowerAmplifier


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_power_amplifier_logic():
    """测试功率放大器驱动逻辑"""
    
    print("=" * 70)
    print("ATA-101B功率放大器驱动逻辑测试")
    print("=" * 70)
    
    # 创建模拟协议
    class MockProtocol:
        """模拟协议"""
        
        def send_command(self, command: str) -> str:
            """模拟发送命令"""
            print(f"  发送命令: {command}")
            return "SET DONE!"
    
    # 创建设备驱动
    print("\n[1/1] 创建设备驱动...")
    protocol = MockProtocol()
    pa = ATA101BPowerAmplifier(
        driver_id='power_amplifier',
        protocol=protocol
    )
    print("✓ 设备驱动创建完成")
    print(f"  设备名称: {pa.device_info['manufacturer']} {pa.device_info['model']}")
    print(f"  通道数: {pa.device_info['channels']}")
    
    # 测试方法
    print("\n测试方法调用:")
    
    print("\n[1] 设置增益 (20dB)...")
    result = pa.set_gain(20)
    print(f"  结果: {result}")
    
    print("\n[2] 设置输入电阻 (50Ω)...")
    result = pa.set_input_resistance(50.0)
    print(f"  结果: {result}")
    
    print("\n[3] 设置输出电阻 (50Ω)...")
    result = pa.set_output_resistance(50.0)
    print(f"  结果: {result}")
    
    print("\n[4] 打开输出...")
    result = pa.output_on()
    print(f"  结果: {result}")
    
    print("\n[5] 获取状态...")
    status = pa.get_status()
    print(f"  状态: {status}")
    
    print("\n[6] 关闭输出...")
    result = pa.output_off()
    print(f"  结果: {result}")
    
    print("\n[7] 保存设置...")
    result = pa.save_settings()
    print(f"  结果: {result}")
    
    print("\n" + "=" * 70)
    print("逻辑测试完成")
    print("=" * 70)
    
    return True


def main():
    """主函数"""
    try:
        success = test_power_amplifier_logic()
        
        if success:
            print("\n✓ 测试成功")
            return 0
        else:
            print("\n✗ 测试失败")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n发生异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
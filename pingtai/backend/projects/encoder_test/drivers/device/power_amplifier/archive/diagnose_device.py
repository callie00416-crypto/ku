"""
ATA-101B设备诊断工具

【功能】
- 检查串口连接
- 发送测试命令
- 接收设备响应
- 诊断通信问题
"""
import sys
from pathlib import Path

# 添加路径
current_file = Path(__file__).resolve()
backend_path = current_file.parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

import time
import logging
from shared.drivers.comm.rs485_comm import RS485Comm
from shared.drivers.protocol.custom_ascii_protocol import CustomASCIIProtocol
from shared.drivers.comm.device_serial_config_manager import get_device_config_manager


# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def diagnose_device(device_id: str = "power_amplifier"):
    """诊断设备"""
    
    print("=" * 70)
    print("ATA-101B设备诊断工具")
    print("=" * 70)
    
    # 1. 加载设备配置
    print(f"\n[1/5] 加载设备配置...")
    config_manager = get_device_config_manager()
    config_file = backend_path / "conf" / "device_serial_config.json"
    
    if not config_file.exists():
        print(f"✗ 配置文件不存在: {config_file}")
        return
    
    config_manager.load_config_file(str(config_file))
    config = config_manager.get_device_config(device_id)
    
    if not config:
        print(f"✗ 未找到设备配置: {device_id}")
        return
    
    print(f"✓ 设备配置:")
    print(f"  设备名称: {config.device_name}")
    print(f"  串口号: {config.port}")
    print(f"  波特率: {config.baudrate}")
    print(f"  数据位: {config.data_bits}")
    print(f"  停止位: {config.stop_bits}")
    print(f"  校验位: {config.parity}")
    
    # 2. 打开串口
    print(f"\n[2/5] 打开串口...")
    try:
        comm = RS485Comm(
            driver_id=device_id,
            port=config.port,
            baudrate=config.baudrate,
            data_bits=config.data_bits,
            stop_bits=config.stop_bits,
            parity=config.parity,
            timeout=2.0
        )
        
        if not comm.open():
            print(f"✗ 串口打开失败")
            print("  可能原因:")
            print("  1. 设备未上电")
            print("  2. 串口被占用")
            print("  3. 串口号错误")
            print("  4. 通信参数不匹配")
            return
        
        print(f"✓ 串口打开成功")
    except Exception as e:
        print(f"✗ 串口打开失败: {e}")
        return
    
    # 3. 发送测试命令
    print(f"\n[3/5] 发送测试命令...")
    
    test_commands = [
        ("打开输出", "ATA,SET,AON,0000;"),
        ("关闭输出", "ATA,SET,AOF,0000;"),
        ("设置增益20dB", "ATA,SET,AMP,0020;"),
        ("设置增益0dB", "ATA,SET,AMP,0000;"),
        ("设置输入电阻50Ω", "ATA,SET,RIN,0050;"),
        ("设置输出电阻50Ω", "ATA,SET,ROT,0500;"),
    ]
    
    for cmd_name, command in test_commands:
        print(f"\n  测试命令: {cmd_name}")
        print(f"  发送: {command}")
        
        try:
            # 发送命令
            comm.send(command.encode('ascii'))
            print(f"  ✓ 命令已发送")
            
            # 等待响应
            time.sleep(0.1)
            
            # 接收响应
            response = comm.recv(size=1024, timeout=1.0)
            
            if response:
                response_str = response.decode('ascii', errors='ignore').strip()
                print(f"  ✓ 响应: {response_str}")
                
                # 检查响应内容
                if 'SET DONE!' in response_str:
                    print(f"  ✓ 命令执行成功")
                elif 'SET ERROR!' in response_str:
                    print(f"  ✗ 命令执行失败")
                elif 'OVER RARANGE ERROR!' in response_str:
                    print(f"  ✗ 参数越界")
                else:
                    print(f"  ? 未知响应")
            else:
                print(f"  ✗ 无响应")
                print(f"  可能原因:")
                print(f"    1. 设备未连接")
                print(f"    2. 设备未上电")
                print(f"    3. 串口接线错误")
                print(f"    4. 设备不支持此命令")
                print(f"    5. 响应超时")
        
        except Exception as e:
            print(f"  ✗ 发送失败: {e}")
    
    # 4. 使用协议层测试
    print(f"\n[4/5] 使用协议层测试...")
    try:
        protocol = CustomASCIIProtocol(
            driver_id=device_id,
            comm=comm,
            command_prefix='ATA,SET,',
            command_suffix=';'
        )
        
        print(f"  测试命令: 打开输出")
        response = protocol.send_command('AON,0000', timeout=1000)
        print(f"  响应: {response}")
        
        time.sleep(0.2)
        
        print(f"  测试命令: 关闭输出")
        response = protocol.send_command('AOF,0000', timeout=1000)
        print(f"  响应: {response}")
        
    except Exception as e:
        print(f"  ✗ 协议层测试失败: {e}")
    
    # 5. 关闭串口
    print(f"\n[5/5] 关闭串口...")
    try:
        comm.close()
        print(f"✓ 串口已关闭")
    except Exception as e:
        print(f"✗ 串口关闭失败: {e}")
    
    # 诊断建议
    print(f"\n{'=' * 70}")
    print("诊断建议")
    print(f"{'=' * 70}")
    
    print(f"\n如果所有命令都无响应，请检查:")
    print(f"  1. 设备是否已上电")
    print(f"  2. RS485转USB转换器是否正常工作")
    print(f"  3. 串口接线是否正确:")
    print(f"     - A 接 R+")
    print(f"     - B 接 R-")
    print(f"     - GND 接 GND")
    print(f"  4. 通信参数是否匹配:")
    print(f"     - 波特率: {config.baudrate}")
    print(f"     - 数据位: {config.data_bits}")
    print(f"     - 停止位: {config.stop_bits}")
    print(f"     - 校验位: {config.parity}")
    print(f"  5. 设备是否支持串口控制")
    print(f"  6. 设备是否处于远程控制模式")
    
    print(f"\n如果部分命令有响应，请检查:")
    print(f"  1. 命令格式是否正确")
    print(f"  2. 参数值是否在有效范围内")
    print(f"  3. 设备是否支持该命令")
    
    print(f"\n如果响应格式不正确，请检查:")
    print(f"  1. 设备固件版本")
    print(f"  2. 设备手册中的协议说明")
    print(f"  3. 是否需要特殊的前缀或后缀")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ATA-101B设备诊断工具')
    parser.add_argument('--device', '-d', type=str, default='power_amplifier', 
                        help='设备ID (默认: power_amplifier)')
    args = parser.parse_args()
    
    try:
        diagnose_device(args.device)
        return 0
    except KeyboardInterrupt:
        print("\n\n诊断被用户中断")
        return 1
    except Exception as e:
        print(f"\n发生异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
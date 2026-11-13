"""
ATA-101B设备深度诊断工具

【功能】
- 增加响应超时时间
- 持续读取设备响应
- 尝试不同的命令格式
- 检查设备通信细节
"""
import sys
from pathlib import Path
import time

# 添加路径
current_file = Path(__file__).resolve()
backend_path = current_file.parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

import logging
from shared.drivers.comm.rs485_comm import RS485Comm
from shared.drivers.comm.device_serial_config_manager import get_device_config_manager


# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def deep_diagnose(device_id: str = "power_amplifier"):
    """深度诊断设备"""
    
    print("=" * 70)
    print("ATA-101B设备深度诊断工具")
    print("=" * 70)
    
    # 1. 加载设备配置
    print(f"\n[1/6] 加载设备配置...")
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
    
    # 2. 打开串口（使用更长的超时）
    print(f"\n[2/6] 打开串口...")
    try:
        comm = RS485Comm(
            driver_id=device_id,
            port=config.port,
            baudrate=config.baudrate,
            data_bits=config.data_bits,
            stop_bits=config.stop_bits,
            parity=config.parity,
            timeout=5.0  # 增加超时时间
        )
        
        if not comm.open():
            print(f"✗ 串口打开失败")
            return
        
        print(f"✓ 串口打开成功")
    except Exception as e:
        print(f"✗ 串口打开失败: {e}")
        return
    
    # 3. 清空缓冲区
    print(f"\n[3/6] 清空缓冲区...")
    try:
        # 尝试读取并清空缓冲区
        for _ in range(10):
            data = comm.recv(size=1024, timeout=0.1)
            if data:
                print(f"  清空数据: {data}")
            else:
                break
        print(f"✓ 缓冲区已清空")
    except Exception as e:
        print(f"✗ 清空缓冲区失败: {e}")
    
    # 4. 发送测试命令并持续读取响应
    print(f"\n[4/6] 发送测试命令并持续读取响应...")
    
    test_commands = [
        ("打开输出", "ATA,SET,AON,0000;"),
        ("关闭输出", "ATA,SET,AOF,0000;"),
        ("设置增益20dB", "ATA,SET,AMP,0020;"),
        ("设置增益0dB", "ATA,SET,AMP,0000;"),
    ]
    
    for cmd_name, command in test_commands:
        print(f"\n  测试命令: {cmd_name}")
        print(f"  发送: {command}")
        
        try:
            # 发送命令
            comm.send(command.encode('ascii'))
            print(f"  ✓ 命令已发送")
            
            # 持续读取响应（最多5秒）
            print(f"  等待响应...")
            all_responses = []
            start_time = time.time()
            
            while time.time() - start_time < 5.0:
                try:
                    response = comm.recv(size=1024, timeout=0.5)
                    if response:
                        response_str = response.decode('ascii', errors='ignore').strip()
                        all_responses.append(response_str)
                        print(f"  收到响应: {response_str}")
                        
                        # 检查是否是期望的响应
                        if 'SET DONE!' in response_str:
                            print(f"  ✓ 命令执行成功")
                            break
                        elif 'SET ERROR!' in response_str:
                            print(f"  ✗ 命令执行失败")
                            break
                        elif 'OVER RANGE ERROR!' in response_str:
                            print(f"  ✗ 参数越界")
                            break
                except:
                    pass
            
            if all_responses:
                print(f"  ✓ 总共收到 {len(all_responses)} 个响应")
            else:
                print(f"  ✗ 无响应")
                print(f"  可能原因:")
                print(f"    1. 设备不会自动返回响应")
                print(f"    2. 需要发送查询命令来获取响应")
                print(f"    3. 设备需要特定的握手协议")
                print(f"    4. 命令格式不正确")
        
        except Exception as e:
            print(f"  ✗ 发送失败: {e}")
        
        time.sleep(1.0)  # 命令之间延迟
    
    # 5. 尝试查询命令
    print(f"\n[5/6] 尝试查询命令...")
    
    query_commands = [
        ("查询状态", "ATA,GET,STA;"),
        ("查询状态", "ATA,GET;"),
        ("查询状态", "ATA,STA;"),
        ("查询状态", "STA;"),
        ("查询状态", "?;"),
        ("查询状态", "STATUS;"),
    ]
    
    for cmd_name, command in query_commands:
        print(f"\n  尝试查询: {cmd_name}")
        print(f"  发送: {command}")
        
        try:
            comm.send(command.encode('ascii'))
            print(f"  ✓ 命令已发送")
            
            # 等待响应
            time.sleep(0.5)
            response = comm.recv(size=1024, timeout=2.0)
            
            if response:
                response_str = response.decode('ascii', errors='ignore').strip()
                print(f"  ✓ 收到响应: {response_str}")
            else:
                print(f"  ✗ 无响应")
        
        except Exception as e:
            print(f"  ✗ 失败: {e}")
    
    # 6. 关闭串口
    print(f"\n[6/6] 关闭串口...")
    try:
        comm.close()
        print(f"✓ 串口已关闭")
    except Exception as e:
        print(f"✗ 串口关闭失败: {e}")
    
    # 诊断结论
    print(f"\n{'=' * 70}")
    print("诊断结论")
    print(f"{'=' * 70}")
    
    print(f"\n如果设备完全没有响应，可能的原因:")
    print(f"  1. 设备不会自动返回响应（需要查询命令）")
    print(f"  2. 设备需要特定的握手协议")
    print(f"  3. 设备需要先发送初始化命令")
    print(f"  4. 设备处于本地控制模式，不支持远程控制")
    print(f"  5. 设备固件版本不同，协议有变化")
    
    print(f"\n建议:")
    print(f"  1. 查看设备手册，确认通信协议")
    print(f"  2. 尝试使用设备自带的上位机软件")
    print(f"  3. 联系设备厂商，确认串口控制功能")
    print(f"  4. 检查设备是否有远程/本地控制切换开关")
    print(f"  5. 查看设备显示屏，确认命令是否生效")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ATA-101B设备深度诊断工具')
    parser.add_argument('--device', '-d', type=str, default='power_amplifier', 
                        help='设备ID (默认: power_amplifier)')
    args = parser.parse_args()
    
    try:
        deep_diagnose(args.device)
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
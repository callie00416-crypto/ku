"""
串口设备管理工具 - Serial Port Device Management Tool

【功能】
1. 列出所有可用串口
2. 检测设备连接状态
3. 自动分配串口
4. 管理设备配置
5. 验证设备连接

【使用场景】
工业自动化测试平台中，需要管理大量硬件设备
通过此工具可以方便地查看和管理所有设备的串口连接
"""
import sys
import argparse
import json
from pathlib import Path

# 添加路径
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from shared.drivers.comm.serial_port_manager import get_serial_port_manager, SerialPortStatus
from shared.drivers.comm.device_serial_config_manager import get_device_config_manager, DeviceSerialConfig


def list_all_ports():
    """列出所有可用串口"""
    print("=" * 70)
    print("可用串口列表")
    print("=" * 70)
    
    port_manager = get_serial_port_manager()
    available_ports = port_manager.list_available_ports()
    
    if not available_ports:
        print("\n未找到可用串口")
        return
    
    print(f"\n找到 {len(available_ports)} 个可用串口:\n")
    
    for i, port in enumerate(available_ports, 1):
        status = port_manager.check_port_status(port)
        status_text = {
            SerialPortStatus.FREE: "✓ 空闲",
            SerialPortStatus.OCCUPIED: "✗ 被占用",
            SerialPortStatus.ERROR: "✗ 错误",
            SerialPortStatus.UNKNOWN: "? 未知"
        }.get(status, f"? {status.value}")
        
        print(f"{i}. {port:15s} - {status_text}")
    
    print()


def check_device_status(device_id: str = None):
    """检查设备状态"""
    print("=" * 70)
    print("设备状态检查")
    print("=" * 70)
    
    # 加载配置
    config_manager = get_device_config_manager()
    config_file = backend_path / "conf" / "device_serial_config.json"
    
    if config_file.exists():
        config_manager.load_config_file(str(config_file))
        print(f"\n已加载配置文件: {config_file}")
    else:
        print(f"\n配置文件不存在: {config_file}")
        return
    
    # 获取设备列表
    if device_id:
        configs = [config_manager.get_device_config(device_id)]
        configs = [c for c in configs if c is not None]
    else:
        configs = config_manager.list_device_configs()
    
    if not configs:
        print("\n未找到设备配置")
        return
    
    print(f"\n找到 {len(configs)} 个设备配置:\n")
    
    for i, config in enumerate(configs, 1):
        port_manager = get_serial_port_manager()
        port_status = port_manager.check_port_status(config.port)
        connection_status = config_manager.verify_device_connection(config.device_id)
        
        status_text = {
            SerialPortStatus.FREE: "✓ 空闲",
            SerialPortStatus.OCCUPIED: "✗ 被占用",
            SerialPortStatus.ERROR: "✗ 错误",
            SerialPortStatus.UNKNOWN: "? 未知"
        }.get(port_status, f"? {port_status.value}")
        
        connection_text = "✓ 连接正常" if connection_status else "✗ 连接失败"
        
        print(f"{i}. {config.device_name} ({config.device_id})")
        print(f"   设备类型: {config.device_type}")
        print(f"   串口号:   {config.port}")
        print(f"   波特率:   {config.baudrate}")
        print(f"   端口状态: {status_text}")
        print(f"   连接状态: {connection_text}")
        print(f"   自动检测: {'是' if config.auto_detect else '否'}")
        if config.description:
            print(f"   描述:     {config.description}")
        print()


def auto_detect_ports():
    """自动检测设备串口"""
    print("=" * 70)
    print("自动检测设备串口")
    print("=" * 70)
    
    # 加载配置
    config_manager = get_device_config_manager()
    config_file = backend_path / "conf" / "device_serial_config.json"
    
    if config_file.exists():
        config_manager.load_config_file(str(config_file))
        print(f"\n已加载配置文件: {config_file}")
    else:
        print(f"\n配置文件不存在: {config_file}")
        return
    
    # 获取所有设备配置
    configs = config_manager.list_device_configs()
    
    if not configs:
        print("\n未找到设备配置")
        return
    
    print(f"\n开始检测 {len(configs)} 个设备的串口...\n")
    
    detected_count = 0
    
    for config in configs:
        if config.auto_detect:
            print(f"检测设备: {config.device_name} ({config.device_id})")
            
            detected_port = config_manager.auto_detect_device_port(config.device_id)
            
            if detected_port:
                print(f"  ✓ 检测到串口: {detected_port}")
                
                # 更新配置
                if detected_port != config.port:
                    print(f"  → 更新配置: {config.port} -> {detected_port}")
                    config_manager.update_device_port(config.device_id, detected_port)
                    detected_count += 1
                else:
                    print(f"  → 配置无需更新")
            else:
                print(f"  ✗ 未检测到串口")
            
            print()
        else:
            print(f"跳过设备: {config.device_name} ({config.device_id}) - 未启用自动检测\n")
    
    # 保存配置
    if detected_count > 0:
        print(f"检测完成，已更新 {detected_count} 个设备配置")
        print("是否保存配置？(y/n): ", end="")
        
        try:
            choice = input().strip().lower()
            if choice == 'y':
                config_manager.save_config_file()
                print("✓ 配置已保存")
            else:
                print("✗ 配置未保存")
        except (EOFError, KeyboardInterrupt):
            print("\n✗ 配置未保存")
    else:
        print("检测完成，配置无需更新")


def add_device_config():
    """添加设备配置"""
    print("=" * 70)
    print("添加设备配置")
    print("=" * 70)
    
    try:
        print("\n请输入设备信息:")
        
        device_id = input("设备ID (如: power_amplifier): ").strip()
        if not device_id:
            print("✗ 设备ID不能为空")
            return
        
        device_name = input("设备名称 (如: ATA-101B功率放大器): ").strip()
        if not device_name:
            print("✗ 设备名称不能为空")
            return
        
        device_type = input("设备类型 (如: power_amplifier): ").strip()
        if not device_type:
            print("✗ 设备类型不能为空")
            return
        
        port = input("串口号 (如: COM1): ").strip()
        if not port:
            print("✗ 串口号不能为空")
            return
        
        baudrate = int(input("波特率 (默认: 9600): ").strip() or "9600")
        data_bits = int(input("数据位 (默认: 8): ").strip() or "8")
        stop_bits = int(input("停止位 (默认: 1): ").strip() or "1")
        parity = input("校验位 (none/even/odd, 默认: none): ").strip() or "none"
        flow_control = input("流控制 (none/rtscts/xonxoff, 默认: none): ").strip() or "none"
        timeout = int(input("超时时间ms (默认: 1000): ").strip() or "1000")
        
        auto_detect = input("启用自动检测 (y/n, 默认: y): ").strip().lower() == 'y'
        
        verify_command = input("验证命令 (可选，留空跳过): ").strip() or None
        verify_response = input("验证响应 (可选，留空跳过): ").strip() or None
        
        description = input("描述 (可选): ").strip() or ""
        
        # 创建配置
        config = DeviceSerialConfig(
            device_id=device_id,
            device_name=device_name,
            device_type=device_type,
            port=port,
            baudrate=baudrate,
            data_bits=data_bits,
            stop_bits=stop_bits,
            parity=parity,
            flow_control=flow_control,
            timeout=timeout,
            auto_detect=auto_detect,
            verify_command=verify_command,
            verify_response=verify_response,
            description=description
        )
        
        # 添加配置
        config_manager = get_device_config_manager()
        config_manager.add_device_config(config)
        
        print(f"\n✓ 设备配置已添加: {device_id}")
        
        # 保存配置
        print("是否保存配置？(y/n): ", end="")
        choice = input().strip().lower()
        if choice == 'y':
            config_file = backend_path / "conf" / "device_serial_config.json"
            config_manager._config_file = config_file
            config_manager.save_config_file()
            print("✓ 配置已保存")
        
    except ValueError as e:
        print(f"✗ 输入错误: {e}")
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except Exception as e:
        print(f"✗ 发生异常: {e}")


def remove_device_config(device_id: str):
    """移除设备配置"""
    print("=" * 70)
    print("移除设备配置")
    print("=" * 70)
    
    config_manager = get_device_config_manager()
    config_file = backend_path / "conf" / "device_serial_config.json"
    
    if config_file.exists():
        config_manager.load_config_file(str(config_file))
    
    config = config_manager.get_device_config(device_id)
    
    if not config:
        print(f"\n✗ 未找到设备配置: {device_id}")
        return
    
    print(f"\n设备信息:")
    print(f"  设备ID: {config.device_id}")
    print(f"  设备名称: {config.device_name}")
    print(f"  设备类型: {config.device_type}")
    print(f"  串口号: {config.port}")
    
    print(f"\n确认删除？(y/n): ", end="")
    try:
        choice = input().strip().lower()
        if choice == 'y':
            config_manager.remove_device_config(device_id)
            print(f"✓ 设备配置已删除: {device_id}")
            
            # 保存配置
            print("是否保存配置？(y/n): ", end="")
            choice = input().strip().lower()
            if choice == 'y':
                config_manager.save_config_file()
                print("✓ 配置已保存")
        else:
            print("✗ 操作已取消")
    except (EOFError, KeyboardInterrupt):
        print("\n\n操作已取消")


def list_device_configs():
    """列出所有设备配置"""
    print("=" * 70)
    print("设备配置列表")
    print("=" * 70)
    
    config_manager = get_device_config_manager()
    config_file = backend_path / "conf" / "device_serial_config.json"
    
    if config_file.exists():
        config_manager.load_config_file(str(config_file))
        print(f"\n已加载配置文件: {config_file}")
    else:
        print(f"\n配置文件不存在: {config_file}")
        return
    
    configs = config_manager.list_device_configs()
    
    if not configs:
        print("\n未找到设备配置")
        return
    
    print(f"\n找到 {len(configs)} 个设备配置:\n")
    
    for i, config in enumerate(configs, 1):
        print(f"{i}. {config.device_name} ({config.device_id})")
        print(f"   设备类型: {config.device_type}")
        print(f"   串口号:   {config.port}")
        print(f"   波特率:   {config.baudrate}")
        print(f"   数据位:   {config.data_bits}")
        print(f"   停止位:   {config.stop_bits}")
        print(f"   校验位:   {config.parity}")
        print(f"   流控制:   {config.flow_control}")
        print(f"   超时时间: {config.timeout}ms")
        print(f"   自动检测: {'是' if config.auto_detect else '否'}")
        if config.description:
            print(f"   描述:     {config.description}")
        print()


def reset_port(port: str):
    """重置串口"""
    print("=" * 70)
    print("重置串口")
    print("=" * 70)
    
    port_manager = get_serial_port_manager()
    
    print(f"\n正在重置串口: {port}")
    
    if port_manager.reset_port(port):
        print(f"✓ 串口 {port} 重置成功")
    else:
        print(f"✗ 串口 {port} 重置失败")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='串口设备管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出所有可用串口
  python serial_device_manager.py list-ports
  
  # 检查所有设备状态
  python serial_device_manager.py check-status
  
  # 检查特定设备状态
  python serial_device_manager.py check-status --device power_amplifier
  
  # 自动检测设备串口
  python serial_device_manager.py auto-detect
  
  # 添加设备配置
  python serial_device_manager.py add-device
  
  # 移除设备配置
  python serial_device_manager.py remove-device --device power_amplifier
  
  # 列出所有设备配置
  python serial_device_manager.py list-devices
  
  # 重置串口
  python serial_device_manager.py reset-port --port COM1
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 列出串口
    subparsers.add_parser('list-ports', help='列出所有可用串口')
    
    # 检查设备状态
    check_parser = subparsers.add_parser('check-status', help='检查设备状态')
    check_parser.add_argument('--device', '-d', help='设备ID')
    
    # 自动检测
    subparsers.add_parser('auto-detect', help='自动检测设备串口')
    
    # 添加设备
    subparsers.add_parser('add-device', help='添加设备配置')
    
    # 移除设备
    remove_parser = subparsers.add_parser('remove-device', help='移除设备配置')
    remove_parser.add_argument('--device', '-d', required=True, help='设备ID')
    
    # 列出设备
    subparsers.add_parser('list-devices', help='列出所有设备配置')
    
    # 重置串口
    reset_parser = subparsers.add_parser('reset-port', help='重置串口')
    reset_parser.add_argument('--port', '-p', required=True, help='串口号')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # 执行命令
    try:
        if args.command == 'list-ports':
            list_all_ports()
        elif args.command == 'check-status':
            check_device_status(args.device)
        elif args.command == 'auto-detect':
            auto_detect_ports()
        elif args.command == 'add-device':
            add_device_config()
        elif args.command == 'remove-device':
            remove_device_config(args.device)
        elif args.command == 'list-devices':
            list_device_configs()
        elif args.command == 'reset-port':
            reset_port(args.port)
        else:
            parser.print_help()
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        return 1
    except Exception as e:
        print(f"\n发生异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
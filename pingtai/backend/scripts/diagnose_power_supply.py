"""
电源设备详细诊断脚本

【诊断内容】
- 测试不同的设备地址
- 增加超时时间
- 检查通信参数
- 逐个测试寄存器
"""
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
import serial.tools.list_ports
from pymodbus.client import ModbusSerialClient
import struct

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_device_addresses():
    """测试不同的设备地址"""
    logger.info("=" * 60)
    logger.info("测试不同设备地址")
    logger.info("=" * 60)
    
    # 查找USB串口
    ports = serial.tools.list_ports.comports()
    usb_port = None
    for port in ports:
        if 'USB' in port.description or 'Silicon Labs' in port.description:
            usb_port = port.device
            logger.info(f"找到USB串口: {usb_port}")
            break
    
    if not usb_port:
        usb_port = 'COM4'
        logger.warning("使用默认串口: COM4")
    
    # 测试不同的设备地址
    device_ids = [1, 2, 3, 4, 5, 6, 7, 8]
    
    for device_id in device_ids:
        logger.info(f"\n测试设备地址: {device_id}")
        
        try:
            # 创建客户端，增加超时时间
            client = ModbusSerialClient(
                port=usb_port,
                baudrate=9600,
                timeout=3,  # 增加超时时间
                parity='N',
                stopbits=1,
                bytesize=8
            )
            
            if not client.connect():
                logger.error(f"  ❌ 连接失败")
                continue
            
            logger.info(f"  ✅ 连接成功")
            
            # 尝试读取远程模式寄存器
            try:
                result = client.read_holding_registers(0x0000, count=1, device_id=device_id)
                if result.isError():
                    logger.info(f"  ❌ 读取寄存器失败: {result}")
                else:
                    logger.info(f"  ✅ 读取寄存器成功: {result.registers}")
                    logger.info(f"  🎯 找到有效设备地址: {device_id}")
                    client.close()
                    return device_id
                    
            except Exception as e:
                logger.info(f"  ❌ 读取异常: {e}")
            
            client.close()
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"  ❌ 测试异常: {e}")
    
    logger.error("❌ 未找到有效设备地址")
    return None


def test_communication_parameters():
    """测试不同的通信参数"""
    logger.info("\n" + "=" * 60)
    logger.info("测试不同通信参数")
    logger.info("=" * 60)
    
    # 查找USB串口
    ports = serial.tools.list_ports.comports()
    usb_port = None
    for port in ports:
        if 'USB' in port.description or 'Silicon Labs' in port.description:
            usb_port = port.device
            break
    
    if not usb_port:
        usb_port = 'COM4'
    
    # 测试不同的波特率
    baudrates = [9600, 19200, 38400, 115200]
    
    for baudrate in baudrates:
        logger.info(f"\n测试波特率: {baudrate}")
        
        try:
            client = ModbusSerialClient(
                port=usb_port,
                baudrate=baudrate,
                timeout=2,
                parity='N',
                stopbits=1,
                bytesize=8
            )
            
            if not client.connect():
                logger.info(f"  ❌ 连接失败")
                continue
            
            logger.info(f"  ✅ 连接成功")
            
            # 尝试读取远程模式寄存器
            try:
                result = client.read_holding_registers(0x0000, count=1, device_id=1)
                if result.isError():
                    logger.info(f"  ❌ 读取失败: {result}")
                else:
                    logger.info(f"  ✅ 读取成功: {result.registers}")
                    logger.info(f"  🎯 找到有效波特率: {baudrate}")
                    client.close()
                    return baudrate
                    
            except Exception as e:
                logger.info(f"  ❌ 读取异常: {e}")
            
            client.close()
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"  ❌ 测试异常: {e}")
    
    logger.error("❌ 未找到有效波特率")
    return None


def test_register_access():
    """测试寄存器访问"""
    logger.info("\n" + "=" * 60)
    logger.info("测试寄存器访问")
    logger.info("=" * 60)
    
    # 查找USB串口
    ports = serial.tools.list_ports.comports()
    usb_port = None
    for port in ports:
        if 'USB' in port.description or 'Silicon Labs' in port.description:
            usb_port = port.device
            break
    
    if not usb_port:
        usb_port = 'COM4'
    
    # 创建客户端
    client = ModbusSerialClient(
        port=usb_port,
        baudrate=9600,
        timeout=3,
        parity='N',
        stopbits=1,
        bytesize=8
    )
    
    if not client.connect():
        logger.error("❌ 连接失败")
        return
    
    logger.info("✅ 连接成功")
    
    # 测试关键寄存器
    test_registers = [
        (0x0000, "远程模式"),
        (0x0001, "通道1设定电压"),
        (0x0003, "通道1设定电流"),
        (0x001B, "通道1输出控制"),
        (0x001D, "通道1输出电压"),
        (0x001F, "通道1输出电流"),
    ]
    
    for addr, name in test_registers:
        logger.info(f"\n测试寄存器: 0x{addr:04X} ({name})")
        
        try:
            # 读取单个寄存器
            result = client.read_holding_registers(addr, count=1, device_id=1)
            if result.isError():
                logger.info(f"  ❌ 读取失败: {result}")
            else:
                logger.info(f"  ✅ 读取成功: {result.registers}")
                
        except Exception as e:
            logger.info(f"  ❌ 读取异常: {e}")
        
        time.sleep(0.3)
    
    client.close()


def test_write_operations():
    """测试写操作"""
    logger.info("\n" + "=" * 60)
    logger.info("测试写操作")
    logger.info("=" * 60)
    
    # 查找USB串口
    ports = serial.tools.list_ports.comports()
    usb_port = None
    for port in ports:
        if 'USB' in port.description or 'Silicon Labs' in port.description:
            usb_port = port.device
            break
    
    if not usb_port:
        usb_port = 'COM4'
    
    # 创建客户端
    client = ModbusSerialClient(
        port=usb_port,
        baudrate=9600,
        timeout=3,
        parity='N',
        stopbits=1,
        bytesize=8
    )
    
    if not client.connect():
        logger.error("❌ 连接失败")
        return
    
    logger.info("✅ 连接成功")
    
    # 测试写远程模式
    logger.info("\n测试写远程模式寄存器")
    try:
        result = client.write_register(0x0000, 1, device_id=1)
        if result.isError():
            logger.error(f"❌ 写入失败: {result}")
        else:
            logger.info(f"✅ 写入成功")
            
        time.sleep(0.5)
        
        # 读取验证
        result = client.read_holding_registers(0x0000, count=1, device_id=1)
        if not result.isError():
            logger.info(f"读取验证: {result.registers}")
            
    except Exception as e:
        logger.error(f"❌ 写入异常: {e}")
    
    client.close()


def main():
    """主函数"""
    logger.info("电源设备详细诊断")
    logger.info("=" * 60)
    
    # 测试设备地址
    device_id = test_device_addresses()
    
    # 测试通信参数
    baudrate = test_communication_parameters()
    
    # 测试寄存器访问
    test_register_access()
    
    # 测试写操作
    test_write_operations()
    
    logger.info("\n" + "=" * 60)
    logger.info("诊断完成")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
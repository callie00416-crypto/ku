"""
简单读取测试
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

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_simple_read():
    """简单读取测试"""
    logger.info("=" * 60)
    logger.info("简单读取测试")
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
    
    # 创建客户端
    client = ModbusSerialClient(
        port=usb_port,
        baudrate=9600,
        timeout=3,
        parity='N',
        stopbits=1,
        bytesize=8
    )
    
    try:
        # 连接
        logger.info("连接Modbus客户端...")
        if not client.connect():
            logger.error("❌ 连接失败")
            return
        
        logger.info("✅ 连接成功")
        
        # 1. 读取远程模式寄存器（已知可工作）
        logger.info("\n【测试1】读取远程模式寄存器(0x0000)")
        result = client.read_holding_registers(0x0000, count=1, device_id=1)
        if result.isError():
            logger.error(f"❌ 读取失败: {result}")
        else:
            logger.info(f"✅ 读取成功: {result.registers[0]}")
        
        time.sleep(0.3)
        
        # 2. 读取电压设置寄存器
        logger.info("\n【测试2】读取电压设置寄存器(0x0001, 2个寄存器)")
        result = client.read_holding_registers(0x0001, count=2, device_id=1)
        if result.isError():
            logger.error(f"❌ 读取失败: {result}")
        else:
            logger.info(f"✅ 读取成功: {[hex(r) for r in result.registers]}")
        
        time.sleep(0.3)
        
        # 3. 读取电流设置寄存器
        logger.info("\n【测试3】读取电流设置寄存器(0x0003, 2个寄存器)")
        result = client.read_holding_registers(0x0003, count=2, device_id=1)
        if result.isError():
            logger.error(f"❌ 读取失败: {result}")
        else:
            logger.info(f"✅ 读取成功: {[hex(r) for r in result.registers]}")
        
        time.sleep(0.3)
        
        # 4. 读取单个寄存器测试
        logger.info("\n【测试4】读取单个寄存器测试")
        test_addresses = [0x0001, 0x0002, 0x0003, 0x0004, 0x0005, 0x0006, 0x0007]
        for addr in test_addresses:
            result = client.read_holding_registers(addr, count=1, device_id=1)
            if result.isError():
                logger.info(f"❌ 0x{addr:04X}: {result}")
            else:
                logger.info(f"✅ 0x{addr:04X}: {result.registers[0]} (0x{result.registers[0]:04X})")
            time.sleep(0.2)
        
        # 5. 连续读取测试
        logger.info("\n【测试5】连续读取测试")
        result = client.read_holding_registers(0x0000, count=10, device_id=1)
        if result.isError():
            logger.error(f"❌ 读取失败: {result}")
        else:
            logger.info(f"✅ 读取成功: {[hex(r) for r in result.registers]}")
        
        # 6. 尝试读取输出控制寄存器
        logger.info("\n【测试6】读取输出控制寄存器(0x001B)")
        result = client.read_holding_registers(0x001B, count=1, device_id=1)
        if result.isError():
            logger.error(f"❌ 读取失败: {result}")
        else:
            logger.info(f"✅ 读取成功: {result.registers[0]} (0x{result.registers[0]:04X})")
        
        # 7. 尝试写入输出控制寄存器
        logger.info("\n【测试7】写入输出控制寄存器(0x001B)")
        result = client.write_register(0x001B, 1, device_id=1)
        if result.isError():
            logger.error(f"❌ 写入失败: {result}")
        else:
            logger.info(f"✅ 写入成功")
            
            time.sleep(0.5)
            
            # 验证写入
            result = client.read_holding_registers(0x001B, count=1, device_id=1)
            if result.isError():
                logger.error(f"❌ 验证读取失败: {result}")
            else:
                logger.info(f"✅ 验证读取成功: {result.registers[0]} (0x{result.registers[0]:04X})")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 测试完成")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            if client:
                client.close()
                logger.info("✅ 资源清理完成")
        except:
            pass


if __name__ == '__main__':
    test_simple_read()
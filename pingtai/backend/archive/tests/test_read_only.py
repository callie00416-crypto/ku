"""
测试读取功能（跳过输出控制）
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
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def ieee754_words_to_float(high_word: int, low_word: int):
    """将两个16位整数转换为IEEE 754浮点数"""
    ieee754_bytes = struct.pack('>HH', high_word, low_word)
    return struct.unpack('>f', ieee754_bytes)[0]


def test_read_only():
    """只测试读取功能"""
    logger.info("=" * 60)
    logger.info("测试读取功能")
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
        
        # 1. 设置远程模式
        logger.info("\n【步骤1】设置远程模式")
        result = client.write_register(0x0000, 1, device_id=1)
        if result.isError():
            logger.error(f"❌ 设置远程模式失败: {result}")
            return
        logger.info("✅ 远程模式设置成功")
        
        time.sleep(0.5)
        
        # 2. 设置电压和电流
        logger.info("\n【步骤2】设置电压5.0V，电流8.0A")
        high_word_v, low_word_v = struct.unpack('>HH', struct.pack('>f', 5.0))
        high_word_i, low_word_i = struct.unpack('>HH', struct.pack('>f', 8.0))
        
        result = client.write_registers(0x0001, [high_word_v, low_word_v], device_id=1)
        if result.isError():
            logger.error(f"❌ 设置电压失败: {result}")
            return
        logger.info("✅ 电压设置成功")
        
        result = client.write_registers(0x0003, [high_word_i, low_word_i], device_id=1)
        if result.isError():
            logger.error(f"❌ 设置电流失败: {result}")
            return
        logger.info("✅ 电流设置成功")
        
        time.sleep(0.5)
        
        # 3. 尝试读取输出数据（协议示例：从0x001D读5个寄存器）
        logger.info("\n【步骤3】读取输出数据")
        try:
            result = client.read_holding_registers(0x001D, count=5, device_id=1)
            if result.isError():
                logger.error(f"❌ 读取输出失败: {result}")
                return
            
            registers = result.registers
            logger.info(f"读取到5个寄存器: {[hex(r) for r in registers]}")
            
            output_voltage = ieee754_words_to_float(registers[0], registers[1])
            output_current = ieee754_words_to_float(registers[2], registers[3])
            cc_cv_status = registers[4]
            
            logger.info(f"输出电压: {output_voltage:.3f}V")
            logger.info(f"输出电流: {output_current:.3f}A")
            logger.info(f"CC/CV状态: {cc_cv_status} ({'CV' if cc_cv_status else 'CC'})")
            
        except Exception as e:
            logger.error(f"❌ 读取输出异常: {e}")
            return
        
        # 4. 尝试读取不同的寄存器范围
        logger.info("\n【步骤4】测试不同寄存器范围")
        
        test_ranges = [
            (0x0010, 10, "0x0010-0x0019"),
            (0x0015, 10, "0x0015-0x001E"),
            (0x0018, 10, "0x0018-0x0021"),
            (0x0020, 10, "0x0020-0x0029"),
        ]
        
        for start_addr, count, desc in test_ranges:
            try:
                result = client.read_holding_registers(start_addr, count=count, device_id=1)
                if result.isError():
                    logger.info(f"❌ {desc} 读取失败: {result}")
                else:
                    logger.info(f"✅ {desc} 读取成功: {[hex(r) for r in result.registers]}")
                    
                    # 检查是否包含输出控制寄存器
                    if 0x001B in range(start_addr, start_addr + count):
                        output_ctrl_idx = 0x001B - start_addr
                        output_ctrl = result.registers[output_ctrl_idx]
                        logger.info(f"  🎯 输出控制寄存器(0x001B)值: {output_ctrl}")
                    
            except Exception as e:
                logger.info(f"❌ {desc} 读取异常: {e}")
            
            time.sleep(0.3)
        
        # 5. 尝试写入输出控制寄存器
        logger.info("\n【步骤5】尝试写入输出控制")
        try:
            # 先读取当前值
            result = client.read_holding_registers(0x001B, count=1, device_id=1)
            if result.isError():
                logger.error(f"❌ 读取输出控制失败: {result}")
            else:
                current_value = result.registers[0]
                logger.info(f"当前输出控制值: {current_value}")
                
                # 尝试写入新值
                new_value = 1 if current_value == 0 else 0
                logger.info(f"尝试写入: {new_value}")
                
                result = client.write_register(0x001B, new_value, device_id=1)
                if result.isError():
                    logger.error(f"❌ 写入输出控制失败: {result}")
                else:
                    logger.info(f"✅ 写入输出控制成功")
                    
                    # 验证写入
                    time.sleep(0.5)
                    result = client.read_holding_registers(0x001B, count=1, device_id=1)
                    if not result.isError():
                        logger.info(f"验证输出控制值: {result.registers[0]}")
                    
        except Exception as e:
            logger.error(f"❌ 输出控制测试异常: {e}")
        
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
    test_read_only()
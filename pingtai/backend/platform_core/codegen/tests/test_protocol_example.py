"""
基于协议文档示例的测试脚本

【协议示例分析】
1. 远程模式: 01 06 00 00 00 01 48 0A
2. 写电压:   01 10 00 01 00 02 04 41 40 00 00 27 8B (5.0V)
3. 写电流:   01 10 00 03 00 02 04 41 00 00 00 A7 86 (8.0A)
4. 打开输出: 01 06 00 1B 00 01 38 0D
5. 关闭输出: 01 06 00 1B 00 00 F9 CD
6. 读输出:   01 03 00 1D 00 05 15 CF (读5个寄存器)
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


def float_to_ieee754_words(value: float):
    """将浮点数转换为IEEE 754格式的两个16位整数"""
    ieee754_bytes = struct.pack('>f', value)
    high_word = struct.unpack('>H', ieee754_bytes[0:2])[0]
    low_word = struct.unpack('>H', ieee754_bytes[2:4])[0]
    return high_word, low_word


def ieee754_words_to_float(high_word: int, low_word: int):
    """将两个16位整数转换为IEEE 754浮点数"""
    ieee754_bytes = struct.pack('>HH', high_word, low_word)
    return struct.unpack('>f', ieee754_bytes)[0]


def test_protocol_example():
    """基于协议文档示例测试"""
    logger.info("=" * 60)
    logger.info("基于协议文档示例测试")
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
        try:
            result = client.write_register(0x0000, 1, device_id=1)
            if result.isError():
                logger.error(f"❌ 设置远程模式失败: {result}")
                return
            logger.info("✅ 远程模式设置成功")
            
            # 验证
            result = client.read_holding_registers(0x0000, count=1, device_id=1)
            if not result.isError():
                logger.info(f"验证: 远程模式值 = {result.registers[0]}")
            
        except Exception as e:
            logger.error(f"❌ 远程模式异常: {e}")
            return
        
        time.sleep(0.5)
        
        # 2. 设置电压（协议示例：5.0V）
        logger.info("\n【步骤2】设置电压5.0V")
        test_voltage = 5.0
        try:
            high_word, low_word = float_to_ieee754_words(test_voltage)
            logger.info(f"IEEE 754格式: 0x{high_word:04X} 0x{low_word:04X}")
            
            # 协议示例: 01 10 00 01 00 02 04 41 40 00 00 27 8B
            result = client.write_registers(0x0001, [high_word, low_word], device_id=1)
            if result.isError():
                logger.error(f"❌ 设置电压失败: {result}")
                return
            logger.info("✅ 电压设置成功")
            
        except Exception as e:
            logger.error(f"❌ 电压设置异常: {e}")
            return
        
        time.sleep(0.5)
        
        # 3. 设置电流（协议示例：8.0A）
        logger.info("\n【步骤3】设置电流8.0A")
        test_current = 8.0
        try:
            high_word, low_word = float_to_ieee754_words(test_current)
            logger.info(f"IEEE 754格式: 0x{high_word:04X} 0x{low_word:04X}")
            
            # 协议示例: 01 10 00 03 00 02 04 41 00 00 00 A7 86
            result = client.write_registers(0x0003, [high_word, low_word], device_id=1)
            if result.isError():
                logger.error(f"❌ 设置电流失败: {result}")
                return
            logger.info("✅ 电流设置成功")
            
        except Exception as e:
            logger.error(f"❌ 电流设置异常: {e}")
            return
        
        time.sleep(0.5)
        
        # 4. 打开输出
        logger.info("\n【步骤4】打开输出")
        try:
            # 协议示例: 01 06 00 1B 00 01 38 0D
            result = client.write_register(0x001B, 1, device_id=1)
            if result.isError():
                logger.error(f"❌ 打开输出失败: {result}")
                return
            logger.info("✅ 输出打开成功")
            
        except Exception as e:
            logger.error(f"❌ 打开输出异常: {e}")
            return
        
        time.sleep(1.0)
        
        # 5. 读取输出数据（协议示例：从0x001D读5个寄存器）
        logger.info("\n【步骤5】读取输出数据")
        try:
            # 协议示例: 01 03 00 1D 00 05 15 CF
            result = client.read_holding_registers(0x001D, count=5, device_id=1)
            if result.isError():
                logger.error(f"❌ 读取输出失败: {result}")
                return
            
            registers = result.registers
            logger.info(f"读取到5个寄存器: {[hex(r) for r in registers]}")
            
            # 根据协议文档，这5个寄存器包含：
            # 寄存器0-1: 输出电压 (IEEE 754)
            # 寄存器2-3: 输出电流 (IEEE 754)  
            # 寄存器4: CC/CV状态
            
            output_voltage = ieee754_words_to_float(registers[0], registers[1])
            output_current = ieee754_words_to_float(registers[2], registers[3])
            cc_cv_status = registers[4]
            
            logger.info(f"输出电压: {output_voltage:.3f}V")
            logger.info(f"输出电流: {output_current:.3f}A")
            logger.info(f"CC/CV状态: {cc_cv_status} ({'CV' if cc_cv_status else 'CC'})")
            
        except Exception as e:
            logger.error(f"❌ 读取输出异常: {e}")
            return
        
        time.sleep(1.0)
        
        # 6. 关闭输出
        logger.info("\n【步骤6】关闭输出")
        try:
            # 协议示例: 01 06 00 1B 00 00 F9 CD
            result = client.write_register(0x001B, 0, device_id=1)
            if result.isError():
                logger.error(f"❌ 关闭输出失败: {result}")
                return
            logger.info("✅ 输出关闭成功")
            
        except Exception as e:
            logger.error(f"❌ 关闭输出异常: {e}")
            return
        
        time.sleep(1.0)
        
        # 7. 再次读取验证关闭状态
        logger.info("\n【步骤7】验证关闭状态")
        try:
            result = client.read_holding_registers(0x001D, count=5, device_id=1)
            if not result.isError():
                registers = result.registers
                output_voltage = ieee754_words_to_float(registers[0], registers[1])
                output_current = ieee754_words_to_float(registers[2], registers[3])
                
                logger.info(f"输出电压: {output_voltage:.3f}V")
                logger.info(f"输出电流: {output_current:.3f}A")
                
                if output_voltage < 1.0:
                    logger.info("✅ 输出已关闭")
                else:
                    logger.warning("⚠️ 输出仍然存在")
            
        except Exception as e:
            logger.error(f"❌ 验证异常: {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 所有测试完成")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 清理资源
        try:
            if client:
                client.write_register(0x001B, 0, device_id=1)  # 关闭输出
                client.close()
                logger.info("✅ 资源清理完成")
        except:
            pass


if __name__ == '__main__':
    test_protocol_example()
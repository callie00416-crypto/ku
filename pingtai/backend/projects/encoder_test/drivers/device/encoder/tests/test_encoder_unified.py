"""统一编码器测试工具

功能：
1. 支持多种连接方式（Analyzer/RS485/BISS-C）
2. 支持连续读数测试
3. 支持单次读数测试
4. 自动检测可用串口
"""
import sys
import os
import time
import logging

# 设置路径
current_dir = os.path.dirname(os.path.abspath(__file__))
encoder_dir = os.path.dirname(current_dir)
sys.path.insert(0, encoder_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def list_serial_ports():
    """列出所有可用串口"""
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        port_list = []
        for port in ports:
            port_info = {
                'name': port.device,
                'description': port.description,
                'hwid': port.hwid
            }
            port_list.append(port_info)
        return port_list
    except ImportError:
        logger.warning("serial 库未安装")
        return []


def test_analyzer_mode(port, read_count=10, interval=0.2):
    """测试Analyzer模式"""
    from dpt_encoder_analyzer import DPTEncoderAnalyzer
    
    logger.info(f"\n=== Analyzer模式测试 ===")
    logger.info(f"端口: {port}, 读取次数: {read_count}, 间隔: {interval}s")
    
    encoder = DPTEncoderAnalyzer(port=port, baud_rate=2500000)
    
    try:
        if encoder.connect():
            logger.info("连接成功")
            
            success_count = 0
            total_inner = 0.0
            total_outer = 0.0
            
            for i in range(read_count):
                result = encoder.read_both_angles()
                
                if result and result.get('crc_valid', False):
                    inner_deg = result['inner']['angle_deg']
                    outer_deg = result['outer']['angle_deg']
                    total_inner += inner_deg
                    total_outer += outer_deg
                    success_count += 1
                    logger.info(f"[{i+1:2d}] 内圈: {inner_deg:8.4f}° | 外圈: {outer_deg:8.4f}° | CRC: ✅")
                elif result:
                    logger.info(f"[{i+1:2d}] CRC校验失败")
                else:
                    logger.info(f"[{i+1:2d}] 读取失败")
                
                time.sleep(interval)
            
            logger.info(f"\n统计: 成功 {success_count}/{read_count}")
            if success_count > 0:
                logger.info(f"内圈平均: {(total_inner/success_count):.4f}°")
                logger.info(f"外圈平均: {(total_outer/success_count):.4f}°")
            
            encoder.disconnect()
            return True
        else:
            logger.error("连接失败")
            return False
            
    except Exception as e:
        logger.error(f"测试异常: {e}")
        return False


def test_rs485_mode(port, read_count=10, interval=0.2):
    """测试RS485模式"""
    from dpt_encoder_rs485 import DPTEncoderRS485
    
    logger.info(f"\n=== RS485模式测试 ===")
    logger.info(f"端口: {port}, 读取次数: {read_count}, 间隔: {interval}s")
    
    encoder = DPTEncoderRS485(port=port, baud_rate=2500000)
    
    try:
        if encoder.connect():
            logger.info("连接成功")
            
            for i in range(read_count):
                result = encoder.read_both_angles()
                
                if result and result.get('crc_valid', False):
                    inner_deg = result['inner']['angle_deg']
                    outer_deg = result['outer']['angle_deg']
                    logger.info(f"[{i+1:2d}] 内圈: {inner_deg:8.4f}° | 外圈: {outer_deg:8.4f}° | CRC: ✅")
                elif result:
                    logger.info(f"[{i+1:2d}] CRC校验失败")
                else:
                    logger.info(f"[{i+1:2d}] 读取失败")
                
                time.sleep(interval)
            
            encoder.disconnect()
            return True
        else:
            logger.error("连接失败")
            return False
            
    except Exception as e:
        logger.error(f"测试异常: {e}")
        return False


def test_bissc_mode(spi_bus=0, spi_cs=0, read_count=10, interval=0.2):
    """测试BISS-C模式"""
    from dpt_encoder_bissc import DPTEncoderBISSC
    
    logger.info(f"\n=== BISS-C模式测试 ===")
    logger.info(f"SPI: bus={spi_bus}, cs={spi_cs}, 读取次数: {read_count}")
    
    encoder = DPTEncoderBISSC(driver_id='bissc_test', spi_bus=spi_bus, spi_cs=spi_cs)
    
    try:
        if encoder.connect():
            logger.info("连接成功")
            
            for i in range(read_count):
                result = encoder.read_both_angles()
                
                if result and result.get('crc_valid', False):
                    inner_deg = result['inner']['angle_deg']
                    outer_deg = result['outer']['angle_deg']
                    logger.info(f"[{i+1:2d}] 内圈: {inner_deg:8.4f}° | 外圈: {outer_deg:8.4f}° | CRC: ✅")
                elif result:
                    logger.info(f"[{i+1:2d}] CRC校验失败")
                else:
                    logger.info(f"[{i+1:2d}] 读取失败")
                
                time.sleep(interval)
            
            encoder.disconnect()
            return True
        else:
            logger.error("连接失败")
            return False
            
    except Exception as e:
        logger.error(f"测试异常: {e}")
        return False


def interactive_test():
    """交互式测试"""
    logger.info("=" * 70)
    logger.info("DPT编码器统一测试工具")
    logger.info("=" * 70)
    
    # 列出可用串口
    ports = list_serial_ports()
    if ports:
        logger.info("\n可用串口:")
        for i, port in enumerate(ports, 1):
            logger.info(f"  [{i}] {port['name']} - {port['description']}")
    else:
        logger.info("\n⚠️  未找到可用串口")
    
    # 选择模式
    print("\n选择测试模式:")
    print("  1. Analyzer模式 (推荐)")
    print("  2. RS485模式")
    print("  3. BISS-C模式")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == '1':
        if ports:
            port = input(f"输入串口 (默认 {ports[0]['name']}): ").strip() or ports[0]['name']
        else:
            port = input("输入串口: ").strip()
        
        count = int(input("读取次数 (默认 10): ").strip() or 10)
        test_analyzer_mode(port, count)
        
    elif choice == '2':
        if ports:
            port = input(f"输入串口 (默认 {ports[0]['name']}): ").strip() or ports[0]['name']
        else:
            port = input("输入串口: ").strip()
        
        count = int(input("读取次数 (默认 10): ").strip() or 10)
        test_rs485_mode(port, count)
        
    elif choice == '3':
        bus = int(input("SPI总线 (默认 0): ").strip() or 0)
        cs = int(input("SPI片选 (默认 0): ").strip() or 0)
        count = int(input("读取次数 (默认 10): ").strip() or 10)
        test_bissc_mode(bus, cs, count)
        
    else:
        logger.error("无效选择")


def quick_test(port='COM6', mode='analyzer', count=10):
    """快速测试"""
    if mode.lower() == 'analyzer':
        test_analyzer_mode(port, count)
    elif mode.lower() == 'rs485':
        test_rs485_mode(port, count)
    elif mode.lower() == 'bissc':
        test_bissc_mode(0, 0, count)
    else:
        logger.error(f"不支持的模式: {mode}")


if __name__ == "__main__":
    # 支持命令行参数
    if len(sys.argv) > 1:
        # python test_encoder_unified.py [port] [mode] [count]
        port = sys.argv[1] if len(sys.argv) > 1 else 'COM6'
        mode = sys.argv[2] if len(sys.argv) > 2 else 'analyzer'
        count = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        quick_test(port, mode, count)
    else:
        interactive_test()
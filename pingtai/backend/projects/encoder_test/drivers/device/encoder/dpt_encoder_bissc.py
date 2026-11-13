import sys
import os

# 尝试导入基础设备类
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))))
    sys.path.insert(0, backend_dir)
    from shared.drivers.base.base_device import BaseDevice
except ImportError:
    # 如果没有BaseDevice，创建一个简单的基类
    class BaseDevice:
        def __init__(self, driver_id, **kwargs):
            self.driver_id = driver_id
            self._is_connected = False
            self._device_status = "disconnected"

from typing import Dict, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)

# BISS-C CRC-6 表 (多项式 x^6 + x^1 + 1 = 0x43)
_BISS_CRC6_TABLE = [
    0x00, 0x03, 0x06, 0x05, 0x0C, 0x0F, 0x0A, 0x09,
    0x18, 0x1B, 0x1E, 0x1D, 0x14, 0x17, 0x12, 0x11,
    0x30, 0x33, 0x36, 0x35, 0x3C, 0x3F, 0x3A, 0x39,
    0x28, 0x2B, 0x2E, 0x2D, 0x24, 0x27, 0x22, 0x21,
    0x23, 0x20, 0x25, 0x26, 0x2F, 0x2C, 0x29, 0x2A,
    0x3B, 0x38, 0x3D, 0x3E, 0x37, 0x34, 0x31, 0x32,
    0x13, 0x10, 0x15, 0x16, 0x1F, 0x1C, 0x19, 0x1A,
    0x0B, 0x08, 0x0D, 0x0E, 0x07, 0x04, 0x01, 0x02
]

def calc_biss_crc6(data: bytes) -> int:
    """
    计算BISS-C协议的CRC-6校验值
    
    参数：
        data: 需要计算CRC的数据（47位，不包含CRC位）
    
    返回：
        CRC-6校验值（取反后的值）
    """
    if len(data) < 6:
        return 0
    
    crc = 0
    bit_count = 0
    
    # 从MSB到LSB处理每一位（共47位）
    for byte_idx in range(6):
        byte = data[byte_idx]
        for bit_pos in range(7, -1, -1):
            # 只处理前47位
            if bit_count >= 47:
                break
            
            bit = (byte >> bit_pos) & 1
            # 确保索引在0-63范围内
            index = ((crc << 1) | bit) & 0x3F
            crc = _BISS_CRC6_TABLE[index]
            bit_count += 1
    
    # BISS-C协议要求CRC取反后发送
    return crc ^ 0x3F


class DPTEncoderBISSC(BaseDevice):
    """
    DPT磁双编码器BISS-C协议驱动
    
    协议特点：
    - 四线制：MA+、MA-（时钟）、SLO+、SLO-（数据）
    - 时钟频率：120kHz - 2.5MHz
    - 数据格式：56位
      - b55-b32: 内圈角度（24位）
      - b31-b8: 外圈角度（24位）
      - b7: 错误位（低电平有效）
      - b6: 警告位（低电平有效）
      - b5-b0: CRC-6（取反后发送）
    - CRC多项式：x^6 + x^1 + 1 (0x43)
    """
    
    PROTOCOL_NAME = "BISS-C"
    DATA_BITS = 56
    ANGLE_BITS = 24
    
    def __init__(self, driver_id: str = 'dpt_bissc', 
                 spi_bus: int = 0, spi_cs: int = 0, **kwargs):
        """
        初始化BISS-C编码器驱动
        
        参数：
            driver_id: 驱动标识
            spi_bus: SPI总线编号
            spi_cs: SPI片选引脚
            **kwargs: 其他参数
        """
        super().__init__(driver_id, protocol=self.PROTOCOL_NAME, **kwargs)
        self.spi_bus = spi_bus
        self.spi_cs = spi_cs
        self.spi_device = None
        self._inner_angle = 0.0
        self._outer_angle = 0.0
        self._error_flag = False
        self._warning_flag = False
        self._crc_valid = False
    
    def connect(self) -> bool:
        """建立连接（通过SPI模拟BISS-C时序）"""
        try:
            # 初始化SPI（BISS-C使用SPI模式模拟）
            self._init_spi()
            self._is_connected = True
            self._device_status = "connected"
            logger.info(f"BISS-C编码器驱动连接成功: {self.driver_id}")
            return True
        except Exception as e:
            logger.error(f"BISS-C编码器连接失败: {e}", exc_info=True)
            self._device_status = "error"
            return False
    
    def _init_spi(self):
        """初始化SPI通信"""
        try:
            import spidev
            self.spi_device = spidev.SpiDev()
            self.spi_device.open(self.spi_bus, self.spi_cs)
            # BISS-C时钟频率范围: 120kHz - 2.5MHz
            self.spi_device.max_speed_hz = 2500000
            self.spi_device.mode = 1  # CPOL=0, CPHA=1
            self.spi_device.bits_per_word = 8
        except ImportError:
            logger.warning("spidev模块不可用，使用模拟模式")
            self.spi_device = None
    
    def disconnect(self):
        """断开连接"""
        try:
            if self.spi_device:
                self.spi_device.close()
        finally:
            self._is_connected = False
            self._device_status = "disconnected"
            logger.info(f"BISS-C编码器驱动已断开: {self.driver_id}")
    
    def _read_raw_data(self) -> Optional[bytes]:
        """读取原始BISS-C数据（模拟时序）"""
        if not self._is_connected:
            return None
        
        try:
            if self.spi_device:
                # 发送时钟并接收数据
                # BISS-C第一个字节是ACK字节(0x82)，后面是8字节数据
                response = self.spi_device.xfer2([0x00] * 9)
                return bytes(response[1:])  # 跳过第一个ACK字节
            else:
                # 模拟数据用于测试
                return self._generate_simulated_data()
        except Exception as e:
            logger.error(f"读取BISS-C数据失败: {e}")
            return None
    
    def _generate_simulated_data(self) -> bytes:
        """生成模拟BISS-C数据（用于测试）"""
        # 模拟237度的内圈和外圈角度
        inner_raw = int(237.0 * (1 << 24) / 360.0)
        outer_raw = int(237.5 * (1 << 24) / 360.0)
        
        # 组装56位数据
        # b55-b32: 内圈角度(24位)
        # b31-b8: 外圈角度(24位)  
        # b7: 错误位(0=正常)
        # b6: 警告位(0=正常)
        # b5-b0: CRC-6
        
        data = bytearray(7)
        # 内圈角度（MSB在前）
        data[0] = (inner_raw >> 16) & 0xFF
        data[1] = (inner_raw >> 8) & 0xFF
        data[2] = inner_raw & 0xFF
        # 外圈角度（MSB在前）
        data[3] = (outer_raw >> 16) & 0xFF
        data[4] = (outer_raw >> 8) & 0xFF
        data[5] = outer_raw & 0xFF
        # 状态位和CRC（模拟）
        data[6] = 0x3F  # 错误位=0, 警告位=1, CRC=全1
        
        return bytes(data)
    
    def _parse_data(self, raw_data: bytes) -> Dict[str, Any]:
        """解析BISS-C协议数据"""
        if len(raw_data) < 7:
            return None
        
        result = {
            'raw_data': list(raw_data),
            'raw_hex': raw_data.hex(' '),
            'inner': {},
            'outer': {},
            'status': {}
        }
        
        # 解析内圈角度 (b55-b32, 24位, MSB在前)
        inner_raw = (raw_data[0] << 16) | (raw_data[1] << 8) | raw_data[2]
        inner_deg = inner_raw * 360.0 / (1 << 24)
        
        # 解析外圈角度 (b31-b8, 24位, MSB在前)
        outer_raw = (raw_data[3] << 16) | (raw_data[4] << 8) | raw_data[5]
        outer_deg = outer_raw * 360.0 / (1 << 24)
        
        # 解析状态位 (b7-b6)
        error_bit = (raw_data[6] >> 7) & 1  # 错误位，低电平有效
        warning_bit = (raw_data[6] >> 6) & 1  # 警告位，低电平有效
        
        # 解析CRC-6 (b5-b0)
        received_crc = raw_data[6] & 0x3F
        
        # 计算CRC校验
        crc_data = raw_data[:6]
        calculated_crc = calc_biss_crc6(crc_data)
        crc_valid = (received_crc == calculated_crc)
        
        result['inner'] = {
            'angle_raw': inner_raw,
            'angle_deg': inner_deg
        }
        result['outer'] = {
            'angle_raw': outer_raw,
            'angle_deg': outer_deg
        }
        result['status'] = {
            'error': error_bit == 0,  # 低电平有效
            'warning': warning_bit == 0,  # 低电平有效
            'error_bit': error_bit,
            'warning_bit': warning_bit
        }
        result['crc_valid'] = crc_valid
        result['received_crc'] = received_crc
        result['calculated_crc'] = calculated_crc
        
        return result
    
    def read_data(self) -> Dict[str, Any]:
        """读取双编码器数据"""
        if not self._is_connected:
            logger.error("BISS-C编码器未连接")
            return None
        
        raw_data = self._read_raw_data()
        if raw_data:
            result = self._parse_data(raw_data)
            if result:
                self._inner_angle = result['inner']['angle_deg']
                self._outer_angle = result['outer']['angle_deg']
                self._error_flag = result['status']['error']
                self._warning_flag = result['status']['warning']
                self._crc_valid = result['crc_valid']
                
                logger.info(f"BISS-C读取成功: 内圈={self._inner_angle:.4f}°, 外圈={self._outer_angle:.4f}°, CRC={'通过' if self._crc_valid else '失败'}")
            return result
        return None
    
    def read_inner_angle(self) -> Optional[Dict[str, Any]]:
        """读取内圈角度"""
        data = self.read_data()
        if data:
            return {
                'angle_raw': data['inner']['angle_raw'],
                'angle_deg': data['inner']['angle_deg'],
                'crc_valid': data['crc_valid']
            }
        return None
    
    def read_outer_angle(self) -> Optional[Dict[str, Any]]:
        """读取外圈角度"""
        data = self.read_data()
        if data:
            return {
                'angle_raw': data['outer']['angle_raw'],
                'angle_deg': data['outer']['angle_deg'],
                'crc_valid': data['crc_valid']
            }
        return None
    
    def read_both_angles(self) -> Optional[Dict[str, Any]]:
        """读取双角度数据（兼容RS485驱动接口）"""
        return self.read_data()
    
    def get_status(self) -> Dict[str, Any]:
        """获取设备状态"""
        return {
            'connected': self._is_connected,
            'device_status': self._device_status,
            'inner_angle': self._inner_angle,
            'outer_angle': self._outer_angle,
            'error_flag': self._error_flag,
            'warning_flag': self._warning_flag,
            'crc_valid': self._crc_valid,
            'protocol': self.PROTOCOL_NAME
        }
    
    def execute_command(self, cmd: str, params: Dict[str, Any] = None) -> Optional[Any]:
        """执行命令"""
        if not self._is_connected:
            logger.error("编码器未连接")
            return None
        
        try:
            if cmd == 'read_data':
                return self.read_data()
            elif cmd == 'read_inner':
                return self.read_inner_angle()
            elif cmd == 'read_outer':
                return self.read_outer_angle()
            elif cmd == 'read_both':
                return self.read_both_angles()
            elif cmd == 'get_status':
                return self.get_status()
            else:
                logger.error(f"未知命令: {cmd}")
                return None
        except Exception as e:
            logger.error(f"执行命令失败 {cmd}: {e}", exc_info=True)
            return None
    
    def reset(self):
        """重置设备"""
        logger.info(f"重置BISS-C编码器: {self.driver_id}")
        self.disconnect()
        self.connect()
    
    def write_data(self, data: Any) -> bool:
        """写入数据（编码器通常只读，此方法保留接口兼容性）"""
        logger.warning("BISS-C编码器为只读设备，不支持写入数据")
        return False


# 测试函数
def test_bissc_encoder():
    logging.basicConfig(level=logging.INFO)
    
    encoder = DPTEncoderBISSC(driver_id='test_bissc', spi_bus=0, spi_cs=0)
    
    try:
        if encoder.connect():
            print("\n=== BISS-C编码器测试 ===")
            
            # 读取数据
            print("\n1. 读取双角度:")
            result = encoder.read_both_angles()
            if result:
                print(f"   内圈角度: {result['inner']['angle_deg']:.4f}°")
                print(f"   外圈角度: {result['outer']['angle_deg']:.4f}°")
                print(f"   CRC校验: {'通过' if result['crc_valid'] else '失败'}")
                print(f"   错误状态: {'正常' if not result['status']['error'] else '错误'}")
                print(f"   警告状态: {'正常' if not result['status']['warning'] else '警告'}")
                print(f"   原始数据: {result['raw_hex']}")
            
            # 读取状态
            print("\n2. 获取状态:")
            status = encoder.get_status()
            print(f"   连接状态: {'已连接' if status['connected'] else '未连接'}")
            print(f"   协议类型: {status['protocol']}")
            
            print("\n=== 测试完成 ===")
            
        else:
            print("编码器连接失败")
            
    finally:
        encoder.disconnect()


if __name__ == "__main__":
    test_bissc_encoder()
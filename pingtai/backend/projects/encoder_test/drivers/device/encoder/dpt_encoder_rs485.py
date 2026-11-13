import serial
import time
import logging
from typing import Any

logger = logging.getLogger(__name__)

# CRC-8 表 (多项式 x^8 + x^7 + x^4 + x^2 + x^1 + 1)
_CRC8_TABLE = [
    0x00, 0x97, 0xB9, 0x2E, 0xE5, 0x72, 0x5C, 0xCB, 0x5D, 0xCA, 0xE4, 0x73, 0xB8, 0x2F, 0x01, 0x96,
    0xBA, 0x2D, 0x03, 0x94, 0x5F, 0xC8, 0xE6, 0x71, 0xE7, 0x70, 0x5E, 0xC9, 0x02, 0x95, 0xBB, 0x2C,
    0xE3, 0x74, 0x5A, 0xCD, 0x06, 0x91, 0xBF, 0x28, 0xBE, 0x29, 0x07, 0x90, 0x5B, 0xCC, 0xE2, 0x75,
    0x59, 0xCE, 0xE0, 0x77, 0xBC, 0x2B, 0x05, 0x92, 0x04, 0x93, 0xBD, 0x2A, 0xE1, 0x76, 0x58, 0xCF,
    0x51, 0xC6, 0xE8, 0x7F, 0xB4, 0x23, 0x0D, 0x9A, 0x0C, 0x9B, 0xB5, 0x22, 0xE9, 0x7E, 0x50, 0xC7,
    0xEB, 0x7C, 0x52, 0xC5, 0x0E, 0x99, 0xB7, 0x20, 0xB6, 0x21, 0x0F, 0x98, 0x53, 0xC4, 0xEA, 0x7D,
    0xB2, 0x25, 0x0B, 0x9C, 0x57, 0xC0, 0xEE, 0x79, 0xEF, 0x78, 0x56, 0xC1, 0x0A, 0x9D, 0xB3, 0x24,
    0x08, 0x9F, 0xB1, 0x26, 0xED, 0x7A, 0x54, 0xC3, 0x55, 0xC2, 0xEC, 0x7B, 0xB0, 0x27, 0x09, 0x9E,
    0xA2, 0x35, 0x1B, 0x8C, 0x47, 0xD0, 0xFE, 0x69, 0xFF, 0x68, 0x46, 0xD1, 0x1A, 0x8D, 0xA3, 0x34,
    0x18, 0x8F, 0xA1, 0x36, 0xFD, 0x6A, 0x44, 0xD3, 0x45, 0xD2, 0xFC, 0x6B, 0xA0, 0x37, 0x19, 0x8E,
    0x41, 0xD6, 0xF8, 0x6F, 0xA4, 0x33, 0x1D, 0x8A, 0x1C, 0x8B, 0xA5, 0x32, 0xF9, 0x6E, 0x40, 0xD7,
    0xFB, 0x6C, 0x42, 0xD5, 0x1E, 0x89, 0xA7, 0x30, 0xA6, 0x31, 0x1F, 0x88, 0x43, 0xD4, 0xFA, 0x6D,
    0xF3, 0x64, 0x4A, 0xDD, 0x16, 0x81, 0xAF, 0x38, 0xAE, 0x39, 0x17, 0x80, 0x4B, 0xDC, 0xF2, 0x65,
    0x49, 0xDE, 0xF0, 0x67, 0xAC, 0x3B, 0x15, 0x82, 0x14, 0x83, 0xAD, 0x3A, 0xF1, 0x66, 0x48, 0xDF,
    0x10, 0x87, 0xA9, 0x3E, 0xF5, 0x62, 0x4C, 0xDB, 0x4D, 0xDA, 0xF4, 0x63, 0xA8, 0x3F, 0x11, 0x86,
    0xAA, 0x3D, 0x13, 0x84, 0x4F, 0xD8, 0xF6, 0x61, 0xF7, 0x60, 0x4E, 0xD9, 0x12, 0x85, 0xAB, 0x3C
]

def calc_crc8(data):
    """计算CRC-8校验值"""
    if isinstance(data, list):
        data = bytes(data)
    crc = data[0]
    for byte in data[1:]:
        crc = _CRC8_TABLE[crc ^ byte]
    return crc

class DPTEncoderRS485:
    """
    DPT磁双编码器RS485协议驱动
    
    协议特点：
    - 字符长度：8 bit
    - 奇偶校验：无
    - 停止位：1
    - 流控制：无
    - 字节顺序：LSB优先（小端序）
    - 波特率：2.5 Mbps（默认）或 5 Mbps
    """
    
    # 指令定义
    CMD_SET_INNER_ZERO = 0x29    # 设置内零位
    CMD_SET_OUTER_ZERO = 0x30    # 设置外零位
    CMD_GET_INNER_ANGLE = 0x31   # 获取内角度
    CMD_GET_OUTER_ANGLE = 0x32   # 获取外角度
    CMD_GET_BOTH_ANGLE = 0x33    # 获取内+外角度
    CMD_GET_INNER_WITH_STATUS = 0x41  # 获取内角度+状态
    CMD_GET_OUTER_WITH_STATUS = 0x42  # 获取外角度+状态
    CMD_GET_BOTH_WITH_STATUS = 0x43   # 获取内+外角度+状态
    
    def __init__(self, port='COM5', baud_rate=2500000):
        """
        初始化编码器
        
        Args:
            port: 串口端口
            baud_rate: 波特率，支持 2500000 (2.5Mbps) 或 5000000 (5Mbps)
        """
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self._connected = False
        
    def connect(self):
        """建立连接"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
                write_timeout=1
            )
            self._connected = True
            logger.info(f"DPT编码器连接成功: {self.port} @ {self.baud_rate}")
            return True
        except Exception as e:
            logger.error(f"DPT编码器连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self._connected = False
            logger.info("DPT编码器已断开")
    
    def is_connected(self):
        """检查连接状态"""
        return self._connected and self.ser and self.ser.is_open
    
    def _send_command(self, command, expected_length):
        """发送命令并接收响应"""
        if not self.is_connected():
            raise ConnectionError("编码器未连接")
        
        try:
            # 清空接收缓冲区
            self.ser.flushInput()
            
            # 发送命令
            self.ser.write(bytes([command]))
            
            # 等待数据
            time.sleep(0.01)  # 10ms 等待响应
            
            # 读取数据
            if self.ser.in_waiting >= expected_length:
                data = self.ser.read(expected_length)
                return data
            else:
                # 尝试读取所有可用数据
                time.sleep(0.05)
                data = self.ser.read(self.ser.in_waiting)
                if len(data) >= expected_length:
                    return data[:expected_length]
                return data
                
        except Exception as e:
            logger.error(f"发送命令失败: {e}")
            return None
    
    def _parse_angle(self, data):
        """解析24位角度数据（LSB优先）"""
        if len(data) >= 3:
            angle_raw = (data[2] << 16) | (data[1] << 8) | data[0]
            angle_deg = angle_raw * 360.0 / (1 << 24)
            return angle_raw, angle_deg
        return None, None
    
    def read_inner_angle(self):
        """读取内圈角度"""
        """返回：{'angle_raw': int, 'angle_deg': float, 'crc_valid': bool}"""
        data = self._send_command(self.CMD_GET_INNER_ANGLE, 4)
        if data and len(data) == 4:
            angle_raw, angle_deg = self._parse_angle(data[:3])
            crc_valid = (calc_crc8(data[:3]) == data[3])
            return {
                'angle_raw': angle_raw,
                'angle_deg': angle_deg,
                'crc_valid': crc_valid,
                'raw_data': list(data)
            }
        return None
    
    def read_outer_angle(self):
        """读取外圈角度"""
        """返回：{'angle_raw': int, 'angle_deg': float, 'crc_valid': bool}"""
        data = self._send_command(self.CMD_GET_OUTER_ANGLE, 4)
        if data and len(data) == 4:
            angle_raw, angle_deg = self._parse_angle(data[:3])
            crc_valid = (calc_crc8(data[:3]) == data[3])
            return {
                'angle_raw': angle_raw,
                'angle_deg': angle_deg,
                'crc_valid': crc_valid,
                'raw_data': list(data)
            }
        return None
    
    def read_both_angles(self):
        """读取内圈和外圈角度"""
        """返回：{'inner': {...}, 'outer': {...}, 'crc_valid': bool}"""
        data = self._send_command(self.CMD_GET_BOTH_ANGLE, 7)
        if data and len(data) == 7:
            inner_raw, inner_deg = self._parse_angle(data[0:3])
            outer_raw, outer_deg = self._parse_angle(data[3:6])
            crc_valid = (calc_crc8(data[:6]) == data[6])
            return {
                'inner': {
                    'angle_raw': inner_raw,
                    'angle_deg': inner_deg
                },
                'outer': {
                    'angle_raw': outer_raw,
                    'angle_deg': outer_deg
                },
                'crc_valid': crc_valid,
                'raw_data': list(data)
            }
        return None
    
    def read_both_with_status(self):
        """读取内圈和外圈角度及状态"""
        """返回：{'inner': {...}, 'outer': {...}, 'status': int, 'crc_valid': bool}"""
        data = self._send_command(self.CMD_GET_BOTH_WITH_STATUS, 8)
        if data and len(data) == 8:
            inner_raw, inner_deg = self._parse_angle(data[0:3])
            outer_raw, outer_deg = self._parse_angle(data[3:6])
            status = data[6]
            crc_valid = (calc_crc8(data[:7]) == data[7])
            
            # 解析状态位
            status_info = {
                'error': (status & 0x80) != 0,           # b7: 错误指示
                'outer_angle_error': (status & 0x10) != 0,  # b4: 外圈角度错误
                'inner_angle_error': (status & 0x08) != 0   # b3: 内圈角度错误
            }
            
            return {
                'inner': {
                    'angle_raw': inner_raw,
                    'angle_deg': inner_deg
                },
                'outer': {
                    'angle_raw': outer_raw,
                    'angle_deg': outer_deg
                },
                'status': status,
                'status_info': status_info,
                'crc_valid': crc_valid,
                'raw_data': list(data)
            }
        return None
    
    def set_inner_zero(self):
        """设置内圈零位（需要连续发送10次）"""
        success_count = 0
        for i in range(10):
            # 先发送获取内角度命令
            self._send_command(self.CMD_GET_INNER_ANGLE, 4)
            time.sleep(0.02)
            # 再发送设置零位命令
            data = self._send_command(self.CMD_SET_INNER_ZERO, 2)
            if data and len(data) == 2:
                count = data[0]
                if count == 10:
                    success_count += 1
            time.sleep(0.02)
        
        return success_count >= 10
    
    def set_outer_zero(self):
        """设置外圈零位（需要连续发送10次）"""
        success_count = 0
        for i in range(10):
            # 先发送获取外角度命令
            self._send_command(self.CMD_GET_OUTER_ANGLE, 4)
            time.sleep(0.02)
            # 再发送设置零位命令
            data = self._send_command(self.CMD_SET_OUTER_ZERO, 2)
            if data and len(data) == 2:
                count = data[0]
                if count == 10:
                    success_count += 1
            time.sleep(0.02)
        
        return success_count >= 10
    
    def reset(self):
        """重置设备"""
        logger.info(f"重置RS485编码器: {self.port}")
        self.disconnect()
        self.connect()
    
    def write_data(self, data: Any) -> bool:
        """写入数据（编码器通常只读，此方法保留接口兼容性）"""
        logger.warning("RS485编码器为只读设备，不支持写入数据")
        return False
    
    def __del__(self):
        """析构函数，确保断开连接"""
        self.disconnect()

# 测试函数
def test_dpt_encoder(port='COM6', baud_rate=2500000, read_count=10):
    logging.basicConfig(level=logging.INFO)
    
    encoder = DPTEncoderRS485(port=port, baud_rate=baud_rate)
    
    try:
        if encoder.connect():
            print("\n=== DPT双编码器测试 ===")
            print(f"端口: {port}, 波特率: {baud_rate}")
            print(f"连续读取角度 {read_count} 次\n")
            
            # 连续读取角度
            for i in range(read_count):
                result = encoder.read_both_angles()
                if result and result['crc_valid']:
                    inner_deg = result['inner']['angle_deg']
                    outer_deg = result['outer']['angle_deg']
                    print(f"[{i+1:2d}] 内圈: {inner_deg:8.4f}° | 外圈: {outer_deg:8.4f}° | CRC: ✅")
                elif result:
                    print(f"[{i+1:2d}] 内圈: {'N/A':>8} | 外圈: {'N/A':>8} | CRC: ❌")
                else:
                    print(f"[{i+1:2d}] 读取失败")
                
                # 每次读取间隔50ms
                time.sleep(0.05)
            
            print("\n=== 测试完成 ===")
            
        else:
            print("编码器连接失败")
            
    finally:
        encoder.disconnect()

if __name__ == "__main__":
    test_dpt_encoder()